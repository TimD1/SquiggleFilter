import argparse
import random
import multiprocessing as mp
import itertools
import os, sys, shutil
import subprocess as sp

from ont_fast5_api.fast5_interface import get_fast5_file
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import mappy
import h5py
import pysam
from numba import njit
from sklearn import metrics

import pyguppyclient as pgc
from pyguppyclient.decode import ReadData

ref = None

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

def get_aligner(args):
    return mappy.Aligner(
            fn_idx_in = f"{args.virus_dir}/reference.fasta",
            preset = "map-ont",
            best_n = 1
    )

################################################################################

def get_fasta(fasta_fn):
    ''' Get sequence from FASTA filename. '''
    with open(fasta_fn, 'r') as fasta:
        return ''.join(fasta.read().split('\n')[1:])

def rev_comp(bases):
    ''' Get reverse complement of sequence. '''
    return bases.replace('A','t').replace('T','a') \
            .replace('G','c').replace('C','g').upper()[::-1]

def load_model(args):
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

def get_reference(args):

    # load fasta and generate reference squiggles
    ref_fasta = get_fasta(f"{args.virus_dir}/reference.fasta")
    kmer_model = load_model(args)
    fwd_ref_sig = ref_signal(ref_fasta, kmer_model)
    rev_ref_sig = ref_signal(rev_comp(ref_fasta), kmer_model)
    ref_sig = np.concatenate((fwd_ref_sig, rev_ref_sig))

    # direct RNA seq on ssRNA should only need forward sequence
    if args.bp_type == "dna":
        return ref_sig
    elif args.bp_type == "rna":
        return fwd_ref_sig
    else:
        return ref_sig

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
            bedfile.write(f"{contig}\t{x}\t{x+999}\n")
    return bedfile_fn

################################################################################

def do_dtw_read_until(read, ru_queue, args):

    # parse lengths and thresholds
    lengths = [int(l) for l in args.chunk_lengths.split(",")]
    thresholds = [int(t) for t in args.chunk_thresholds.split(",")]
    rejected = False
    for length, threshold in zip(lengths, thresholds):

        # extract region, normalize, calculate score
        signal = read.signal[:args.trim_start+length]
        signal = discrete_normalize(signal)
        signal = signal[args.trim_start:]
        score = sdtw(signal)

        # reject read if too dissimilar
        if score > threshold:
            ru_queue.put(f"{read.read_id}\t{args.trim_start+length}" \
                    f"\t{score}\tFalse\n")
            rejected = True
            break

    # read passes all checks, basecall and align
    if not rejected:
        ru_queue.put(f"{read.read_id}\t{len(read.signal)}\t{score}\tTrue\n")
        return read

    return None

################################################################################

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

def write_sam_header(aligner, args):
    '''
    Writes SAM header to file, using aligner information.
    (borrowed from https://github.com/nanoporetech/bonito io.py)
    '''
    with open(args.sam_file, 'w') as sam_file:
        sam_file.write('%s\n' % os.linesep.join([
            "\t".join([
                '@SQ', 'SN:%s' % name, 'LN:%s' % len(aligner.seq(name))
            ]) for name in aligner.seq_names
        ]))

        sam_file.write('%s\n' % "\t".join([
            '@PG',
            'ID:read-until',
            'PN:read-until',
            'VN:%s' "0.0.0",
            'CL:%s' % ' '.join(sys.argv),
        ]))
        sam_file.flush()

def write_sam_data(read_id, sequence, qstring, alignment, args):
    '''
    Writes all alignment data to SAM file.
    (borrowed from https://github.com/nanoporetech/bonito io.py)
    '''
    with open(args.sam_file, 'a') as sam_file:
        softclip = [
            '%sS' % alignment.q_st if alignment.q_st else '',
            alignment.cigar_str,
            '%sS' % (len(sequence) - alignment.q_en) if \
                    len(sequence) - alignment.q_en else ''
        ]
        sam_file.write("%s\n" % "\t".join(map(str, [
            read_id,
            0 if alignment.strand == +1 else 16,
            alignment.ctg,
            alignment.r_st + 1,
            alignment.mapq,
            ''.join(softclip if alignment.strand == +1 else softclip[::-1]),
            '*', 0, 0,
            sequence if alignment.strand == +1 else rev_comp(sequence),
            qstring,
            'NM:i:%s' % alignment.NM,
            'MD:Z:%s' % alignment.MD,
        ])))
        sam_file.flush()
    return

################################################################################

def generate_bam(args):

    # index reference FASTA
    ref_fasta = f"{args.virus_dir}/reference.fasta"
    if not os.path.exists(f"{ref_fasta}.fai"):
        sp.call(["samtools", "faidx", ref_fasta])

    # convert SAM to indexed and sorted BAM
    prefix = os.path.splitext(args.sam_file)[0]
    sp.run(["samtools", "view", "-b", f"-o{prefix}.bam", f"{prefix}.sam"])
    sp.run(["samtools", "sort", f"-@ {mp.cpu_count()}", f"-o{prefix}s.bam", 
        f"{prefix}.bam"])
    sp.run(["samtools", "calmd", "-b", f"{prefix}s.bam", ref_fasta], 
            stdout=open(f"{prefix}f.bam", 'w'), stderr=sp.DEVNULL)
    sp.run(["samtools", "index", f"-@ {mp.cpu_count()}", f"{prefix}f.bam"])

    # rename files, remove temp data
    os.remove(f"{prefix}.bam")
    os.remove(f"{prefix}s.bam")
    shutil.move(f"{prefix}f.bam", f"{prefix}.bam")
    shutil.move(f"{prefix}f.bam.bai", f"{prefix}.bam.bai")

    return f"{prefix}.bam"

################################################################################

def coverage_stats(bed_file, bam_file):
    sp.call(["samtools", "bedcov", bed_file, bam_file])

################################################################################

def check_coverage_progress(bed_file, args):

    bam_file = generate_bam(args)
    stats = coverage_stats(bed_file, bam_file)
    # print_progress(stats)
    return

################################################################################

def main(args):
    global ref

    # init
    validate(args)
    bedfile = generate_bedfile(args)
    target_coverage_met = False
    ref = get_reference(args)
    aligner = get_aligner(args)
    write_sam_header(aligner, args)
    if args.bp_type == "dna":
        guppy_config = \
                f"/opt/ont/guppy/data/dna_r9.4.1_450bps_{args.model_type}.cfg"
    else:
        guppy_config = \
                f"/opt/ont/guppy/data/rna_r9.4.1_70bps_{args.model_type}.cfg"

    # perform read-until
    while not target_coverage_met:

        # select next subset of data
        virus_reads = yield_reads(f"{args.virus_dir}/fast5")
        other_reads = yield_reads(f"{args.other_dir}/fast5")
        batch = [next(virus_reads)] + \
                list(itertools.islice(other_reads, args.ratio))

        # create pool and queues
        with mp.Pool() as pool:
            manager = mp.Manager()
            ru_queue = manager.Queue()

            # create writer threads for data output
            ru_writer = pool.apply_async(write_ru_data, 
                    (ru_queue, args.ru_data_file))

            # spawn worker threads to perform alignment
            jobs = []
            reads = []
            for read in batch:
                if not args.basecall:
                    job = pool.apply_async(do_dtw_read_until, 
                            (read, ru_queue, args))
                jobs.append(job)
            for job in jobs: reads.append(job.get())
            reads = list(filter(None, reads))

            # basecall all data
            with pgc.GuppyBasecallerClient(guppy_config, port=1234) as basecaller:
                for read in reads:
                    called = basecaller.basecall(read)
                    try:
                        alignment = next(aligner.map(called.seq))
                        write_sam_data(read.read_id, called.seq, 
                                called.qual, alignment, args)
                    except(StopIteration):
                        pass # no alignment, can ignore for read-until

            # teardown
            ru_queue.put('kill')
            ru_writer.get()

        target_coverage_met = check_coverage_progress(bedfile, args)
        break

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
