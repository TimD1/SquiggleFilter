import argparse
import random
import multiprocessing as mp
import itertools

from ont_fast5_api.fast5_interface import get_fast5_file
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import mappy
import h5py
import pysam
from numba import njit
from sklearn import metrics

import pyguppyclient
from pyguppyclient.decode import ReadData

def yield_reads(folder):
    ''' Yields full-length reads from all FAST5 files in a directory. '''
    for filename in glob(f"{folder}/*.fast5"):
        with get_fast5_file(filename, 'r') as f5_fh:
            for read in f5_fh.get_reads():
                raw = read.handle[read.raw_dataset_name][:]
                channel_info = read.handle[read.global_key + 'channel_id'].attrs
                scaling = channel_info['range'] / channel_info['digitisation']
                offset = int(channel_info['offset'])
                yield ReadData(raw, read.read_id, scaling=scaling, offset=offset)

################################################################################

def basecall_align(read_type, length, args):

    folder = args.virus_dir if read_type == "virus" else args.other_dir
    max_reads = args.max_virus_reads if read_type == "virus" else args.max_other_reads

    # initialize mappy aligner
    aligner = mappy.Aligner(
            fn_idx_in = args.virus_dir+"/reference.fasta",
            preset = "map-ont",
            best_n = 1
    )

    # initialize guppy basecaller
    if args.bp_type == "dna":
        guppy_config = f"/opt/ont/guppy/data/dna_r9.4.1_450bps_{args.model_type}.cfg"
    else:
        guppy_config = f"/opt/ont/guppy/data/rna_r9.4.1_70bps_{args.model_type}.cfg"

    read_count = 0
    scores = np.zeros(max_reads)
    with pyguppyclient.GuppyBasecallerClient(guppy_config, port=1234) as bc:
        for fast5_fn in glob(folder + "/fast5/*.fast5"):
            for read in yield_read_chunks(fast5_fn, args.trim_start, length):
                if read_type=="virus" and read.read_id not in [x.split()[0] for x in \
                    open(folder+"/aligned/calls_to_ref.sam").readlines()]: continue
                read_count += 1
                if read_count >= max_reads: break
                called = bc.basecall(read)
                try:
                    alignment = next(aligner.map(called.seq))
                    scores[read_count] = alignment.mapq
                except(StopIteration):
                    pass # no alignment

            if read_count >= max_reads: break

        # return mapping scores
        return scores

################################################################################

def get_fasta(fasta_fn):
    ''' Get sequence from FASTA filename. '''
    with open(fasta_fn, 'r') as fasta:
        return ''.join(fasta.read().split('\n')[1:])

def rev_comp(bases):
    ''' Get reverse complement of sequence. '''
    return bases.replace('A','t').replace('T','a') \
            .replace('G','c').replace('C','g').upper()[::-1]

def load_model():
    ''' Load k-mer model file into Python dict. '''
    kmer_model = {}
    with open(f"../data/{args.bp_type}_kmer_model.txt", 'r') as model_file:
        for line in model_file:
            kmer, current = line.split()
            kmer_model[kmer] = float(current)
    return kmer_model

def discrete_normalize(seq, bits=8, minval=-8, maxval=8):
    ''' 
    Approximate normalization which converts signal to integer of desired precision. 
    '''
    mean = int(np.mean(seq))
    mean_avg_dev = int(np.mean(np.abs(seq - mean)))
    norm_seq = (seq - mean) / mean_avg_dev

    norm_seq[norm_seq < minval] = minval
    norm_seq[norm_seq > maxval] = maxval
    norm_seq = ( (norm_seq - minval) * ((2**(bits)-1)/(maxval-minval)) ).astype(int)
    return norm_seq

def ref_signal(fasta, kmer_model):
    ''' Convert reference FASTA to expected reference signal (z-scores). '''
    signal = np.zeros(len(fasta))
    k = 6 if args.bp_type == "dna" else 5
    for kmer_start in range(len(fasta)-k):
        signal[kmer_start] = kmer_model[fasta[kmer_start:kmer_start+k]]
    return discrete_normalize(signal*100)

################################################################################

ref = None

@njit()
def sdtw(seq):
    ''' Returns minimum alignment score for subsequence DTW, linear memory. '''

    # initialize cost matrix
    cost_mat_prev = np.zeros(len(ref))
    cost_mat_curr = np.zeros(len(ref))

    # compute entire cost matrix
    cost_mat_prev[0] = abs(seq[0]-ref[0])
    for i in range(1, len(seq)):
        cost_mat_curr[0] = cost_mat_prev[0] + abs(seq[i]-ref[0])
        for j in range(1, len(ref)):
            cost_mat_curr[j] = abs(seq[i]-ref[j]) + \
                min(cost_mat_prev[j-1], cost_mat_curr[j-1], cost_mat_prev[j])
        cost_mat_prev[:] = cost_mat_curr[:]
    return np.min(cost_mat_curr)

################################################################################

def dtw_align(read_type, length, args):
    global ref

    # get reference signal
    ref_fasta = get_fasta(args.virus_dir + "/reference.fasta")
    kmer_model = load_model()
    fwd_ref_sig = ref_signal(ref_fasta, kmer_model)
    rev_ref_sig = ref_signal(rev_comp(ref_fasta), kmer_model)
    ref_sig = np.concatenate((fwd_ref_sig, rev_ref_sig))
    ref = ref_sig

    # preprocess all reads
    reads = []
    folder = args.virus_dir if read_type == "virus" else args.other_dir
    max_reads = args.max_virus_reads if read_type == "virus" else args.max_other_reads
    read_count = 0
    for fast5_fn in glob(folder + "/fast5/*.fast5"):
        fast5_file = h5py.File(fast5_fn, 'r')
        for read_name in fast5_file:
            signal = np.array(fast5_file[read_name]['Raw']['Signal'] \
                        [:args.trim_start+length], dtype=np.int16)
            signal = discrete_normalize(signal)
            signal = signal[args.trim_start:]
            if read_count >= max_reads: break
            read_count += 1
            reads.append(signal)
        if read_count >= max_reads: break

    # align reads
    with mp.Pool() as pool:
        dists = pool.map(sdtw, reads)
    return np.array(dists)

################################################################################

def validate(args):

    basepair_types = ["dna", "rna"]
    if args.bp_type not in basepair_types:
        print(f"ERROR: 'args.bp_type' must be one of {basepair_types}.")
        exit(1)

    model_types = ["fast", "hac"]
    if args.model_type not in model_types:
        print(f"ERROR: 'args.model_type' must be one of {model_types}.")
        exit(1)

################################################################################

def generate_bedfile(args):
    ''' 
    Generate BED-file for ensuring minimum read-until depth over each region.
    '''

    # extract reference length and contig name from reference FASTA
    fasta_fn = f"{args.virus_dir}/reference.fasta"
    fasta_len = len(get_fasta(fasta_fn))
    fasta = pysam.FastaFile(fasta_fn)
    contig = fasta.references[0]

    # generate regions of 1000bp (will enforce minimum avg coverage in each)
    bedfile_fn = f"{args.virus_dir}/regions.bed"
    with open(bedfile_fn, 'w') as bedfile:
        for x in range(1, fasta_len, 1000):
            bedfile.write(f"{contig}\t{x}\t{x+1000}\n")
    return bedfile_fn

################################################################################

def do_read_until(read, ru_queue, sam_queue, args):
    lengths = [int(l) for l in args.chunk_lengths.split(",")]
    thresholds = [int(t) for t in args.chunk_thresholds.split(",")]

    ru_queue.put(f"{read.read_id}\t2\t3\n")
    return

def write_ru_data(ru_queue, ru_data_fn):
    '''
    Writes all read-until data to file.
    '''

    with open(ru_data_fn, 'w') as ru_data:
        while True:
            data = ru_queue.get()
            if data == "kill": break
            ru_data.write(data)
            ru_data.flush()
    return

################################################################################

def main(args):

    validate(args)

    bedfile = generate_bedfile(args)

    target_coverage_met = False
    while not target_coverage_met:
        virus_reads = yield_reads(f"{args.virus_dir}/fast5")
        other_reads = yield_reads(f"{args.other_dir}/fast5")

        batch = [next(virus_reads)] + \
                list(itertools.islice(other_reads, args.ratio))

        # threads = []
        # threads.append(mp.Process(target=do_read_until, 
        #     args=(virus_reads.next(), args)))
        # for other_read in itertools.islice(other_reads, args.ratio):
        #     threads.append(mp.Process(target=do_read_until, 
        #         args=(other_read, args)))
        # for t in threads: t.start()
        # for t in threads: t.join()

        with mp.Pool() as pool:
            manager = mp.Manager()
            sam_queue = manager.Queue()
            ru_queue = manager.Queue()

            # sam_writer = pool.apply_async(write_sam, (args.sam_file))
            ru_writer = pool.apply_async(write_ru_data, 
                (ru_queue, args.ru_data_file))

            jobs = []
            for read in batch:
                job = pool.apply_async(do_read_until, 
                        (read, ru_queue, sam_queue, args))
                jobs.append(job)
            for job in jobs: job.get()

            # sam_queue.put('kill')
            ru_queue.put('kill')
            # sam_writer.get()
            ru_writer.get()
        break


        target_coverage_met = check_coverage_progress(args)



################################################################################

def parser():
    parser = argparse.ArgumentParser()

    # guppy parameters
    parser.add_argument("--bp_type", default="dna")
    parser.add_argument("--model_type", default="hac")

    # read-until parameters
    parser.add_argument("--virus_dir", default="/x/squiggalign_data/lambda")
    parser.add_argument("--other_dir", default="/x/squiggalign_data/human")
    parser.add_argument("--ratio", type=int, default=10)
    parser.add_argument("--target_coverage", type=float, default=1)
    parser.add_argument("--basecall", action="store_true", default=False)

    # output data parameters
    parser.add_argument("--sam_file", default="read_until_alignments.sam")
    parser.add_argument("--ru_data_file", default="read_until_data.txt")

    # read chunk selection parameters
    parser.add_argument("--trim_start", type=int, default=1000)
    parser.add_argument("--chunk_lengths", 
            default="1000,2000,3000,4000,5000,6000,7000,8000,9000,10000")
    parser.add_argument("--chunk_thresholds", 
            default="5500,11000,15000,19000,24000,29000,34000,39000,44000")

    return parser

################################################################################

if __name__ == "__main__":
    parser = parser()
    args = parser.parse_args()
    main(args)
