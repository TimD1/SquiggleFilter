import argparse
import random
import multiprocessing as mp
import itertools
import os, sys, shutil
import subprocess as sp
import time
import copy

from ont_fast5_api.fast5_interface import get_fast5_file
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import mappy
import h5py
import pysam
from numba import njit
from sklearn import metrics

# import pyguppyclient as pgc
# from pyguppyclient.decode import ReadData

from pyguppy_client_lib.pyclient import PyGuppyClient
from pyguppy_client_lib.helper_functions import package_read, basecall_with_pyguppy

ref = None
nregions = 0
nreads_total = 0
nreads_mapped = 0

class TimerError(Exception):
    ''' Custom exception for incorrect Timer usage. '''

class Timer():
    def __init__(self):
        self._time = 0
        self._running = False

    def start(self):
        if self._running: raise TimerError("Cannot start a running timer.")
        self._start_time = time.perf_counter()
        self._running = True

    def stop(self):
        if not self._running: raise TimerError("Cannot stop a stopped timer.")
        elapsed_time = time.perf_counter() - self._start_time
        self._time += elapsed_time
        self._running = False

    def elapsed(self):
        return self._time

################################################################################

class Read():
    def __init__(self, signal, read_id, is_virus, file_name, offset=0, scaling=1.0):
        self.signal = signal
        self.read_id = read_id
        self.is_virus = is_virus
        self.file_name = file_name
        self.total_samples = len(signal)
        self.daq_offset = offset
        self.daq_scaling = scaling
        self.read_tag = random.randint(0, int(2**32 - 1))

def yield_reads(folder, is_virus):
    ''' Yields full-length reads from all FAST5 files in a directory. '''
    for filename in glob(f"{folder}/*.fast5"):
        with h5py.File(filename, 'r') as f5_fh:
            reads = list(f5_fh.keys())
            if is_virus:
                random.seed(42)
                random.shuffle(reads)
            for read in reads:
                signal = f5_fh[read]['Raw']['Signal'][:]
                read_id = f5_fh[read]['Raw'].attrs['read_id'].decode("utf-8")
                channel_info = f5_fh[read]['channel_id'].attrs
                scaling = channel_info['range'] / channel_info['digitisation']
                offset = int(channel_info['offset'])
                yield Read(signal=signal, read_id=read_id, is_virus=is_virus, 
                        file_name=filename, offset=offset, scaling=scaling)

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
    with open(f"../data/{args.basetype}_kmer_model.txt", 'r') as model_file:
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
    k = 6 if args.basetype == "dna" else 5
    for kmer_start in range(len(fasta)-k):
        signal[kmer_start] = kmer_model[fasta[kmer_start:kmer_start+k]]
    return discrete_normalize(signal*100)

################################################################################

@njit()
def sdtw(seq, prev_row, start=False):
    ''' Returns minimum alignment score for subsequence DTW, linear memory. '''

    # initialize cost matrix
    cost_mat_prev = prev_row[:]
    cost_mat_curr = np.zeros(len(ref))

    # compute entire cost matrix
    if start:
        cost_mat_prev[0] = abs(seq[0]-ref[0])
    for i in range(1, len(seq)):
        cost_mat_curr[0] = cost_mat_prev[0] + abs(seq[i]-ref[0])
        for j in range(1, len(ref)):
            cost_mat_curr[j] = abs(seq[i]-ref[j]) + \
                min(cost_mat_prev[j-1], cost_mat_curr[j-1], cost_mat_prev[j])
        cost_mat_prev[:] = cost_mat_curr[:]
    return cost_mat_curr

################################################################################

def get_reference(args):

    # load fasta and generate reference squiggles
    ref_fasta = get_fasta(f"{args.virus_dir}/reference.fasta")
    kmer_model = load_model(args)
    fwd_ref_sig = ref_signal(ref_fasta, kmer_model)
    rev_ref_sig = ref_signal(rev_comp(ref_fasta), kmer_model)
    ref_sig = np.concatenate((fwd_ref_sig, rev_ref_sig))

    # direct RNA seq on ssRNA should only need forward sequence
    if args.basetype == "dna":
        return ref_sig
    elif args.basetype == "rna":
        return fwd_ref_sig
    else:
        return ref_sig

################################################################################

def init(args):

    # check base type
    basetypes = ["dna", "rna"]
    if args.basetype not in basetypes:
        print(f"ERROR: 'args.basetype' must be one of {basetypes}.")
        exit(1)

    # check Guppy model type
    model_types = ["fast", "hac"]
    if args.model_type not in model_types:
        print(f"ERROR: 'args.model_type' must be one of {model_types}.")
        exit(1)

    # set default filepaths for SAM/FASTQ/RU_DATA files
    if args.ru_data_file == "default":
        args.ru_data_file = f"{args.virus_dir}/read_until_data.txt"
    if args.fastq_file == "default":
        os.makedirs(f"{args.virus_dir}/fastq", exist_ok=True)
        args.fastq_file = f"{args.virus_dir}/fastq/all.fastq"
    if args.sam_file == "default":
        os.makedirs(f"{args.virus_dir}/aligned", exist_ok=True)
        args.sam_file = f"{args.virus_dir}/aligned/calls_to_ref.sam"
    fh = open(args.ru_data_file, 'w'); fh.close()
    fh = open(args.fastq_file, 'w'); fh.close()

    # set Guppy configuration
    if args.basetype == "dna":
        args.guppy_config = f"dna_r9.4.1_450bps_{args.model_type}.cfg"
        args.port = 1234
    else:
        args.guppy_config = f"rna_r9.4.1_70bps_{args.model_type}.cfg"
        args.port = 2345

    return args

################################################################################

def generate_bedfile(args):
    ''' 
    Generate BED-file for ensuring minimum read-until depth over each region.
    '''
    global nregions

    # extract reference length and contig name from reference FASTA
    fasta_fn = f"{args.virus_dir}/reference.fasta"
    fasta_len = len(get_fasta(fasta_fn))
    fasta = pysam.FastaFile(fasta_fn)
    contig = fasta.references[0]

    # generate regions, will enforce minimum avg coverage in each
    bedfile_fn = f"{args.virus_dir}/regions.bed"
    with open(bedfile_fn, 'w') as bedfile:
        for x in range(1, fasta_len, args.region_size):
            bedfile.write(f"{contig}\t{x}\t{min(x+args.region_size-1, fasta_len)}\n")
            nregions += 1
    return bedfile_fn

################################################################################

def do_dtw_read_until(read, ru_queue, args):

    # parse lengths and thresholds
    lengths = [int(l) for l in args.chunk_lengths.split(",")]
    thresholds = [int(t) for t in args.chunk_thresholds.split(",")]
    rejected = False
    prev_length = 0
    prev_row = np.zeros(len(ref))
    first_dtw = True
    for length, threshold in zip(lengths, thresholds):

        # accept read if we've seen it all
        if len(read.signal) < args.trim_start+length:
            break

        # extract region, normalize, calculate score
        signal = read.signal[:args.trim_start+length]
        signal = discrete_normalize(signal)
        signal = signal[args.trim_start+prev_length:]
        row = sdtw(signal, prev_row, first_dtw)
        score = np.min(row)

        # reject read if too dissimilar
        if score > threshold:
            ru_queue.put(f"{read.is_virus}\t{read.file_name}\t{read.read_id}\t" \
                    f"{args.trim_start+length}\t{score}\tFalse\n")
            rejected = True
            break
        prev_row[:] = row[:]
        prev_length = length
        first_dtw = False

    # read passes all checks, basecall and align
    if not rejected:
        ru_queue.put(f"{read.is_virus}\t{read.file_name}\t{read.read_id}\t" \
                f"{len(read.signal)}\t{score}\tTrue\n")
        return read

    return None

################################################################################

def write_ru_data(ru_queue, ru_data_fn):
    '''
    Writes all read-until data to file.
    '''

    with open(ru_data_fn, 'a') as ru_data:
        ru_data.write("is_virus\tsource_fast5\tread_id\t"
                "final_len\tlast_score\tkeep\n")
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
    global nreads_mapped
    nreads_mapped += 1
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

def write_fastq_data(read_id, sequence, qstring, args):
    with open(args.fastq_file, 'a') as fastq_file:
        fastq_file.write(f"@{read_id}\n{sequence}\n+\n{qstring}\n")
        fastq_file.flush()
    return

################################################################################

def generate_bam(args):
    '''
    Converts SAM file to indexed and sorted BAM.
    '''

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

def update_coverage(bed_file, bam_file, args):

    # read coverage in each region
    proc = sp.Popen(["samtools", "bedcov", bed_file, bam_file], 
                stdout=sp.PIPE)
    bedcov = proc.stdout.read()

    # print overview
    os.system('clear')
    print("Run-Until Update")

    # calculate distribution of coverages
    print("\n  Regions", end="")
    regions_per_line = 4
    covs = [0] * (args.target_coverage+1)
    for idx, region in enumerate(bedcov.decode('ascii').split('\n')[:-1]):
        if not idx % regions_per_line:
            print("\n", end ="")
        contig, start, stop, bases = region.split()
        cov = float(bases)/(float(stop)-float(start)+1)
        covs[min(args.target_coverage, int(cov))] += 1
        print(f"\treg {idx}:\t{cov:.3f}x", end="")

    # print read-until update to screen
    print("\n\n  Coverage")
    for cov, regions in enumerate(covs):
        print(f"\tcoverage {cov}: {regions}")

    print("\n  Overview")
    print(f"\t{nreads_mapped} of {nreads_total} reads mapped")
    print(f"\t{covs[-1]} of {nregions} regions covered")

    # stop read until once target met in all regions
    return covs[-1] == nregions

################################################################################

def merge_calls(call_chunk, new_call_chunk):
    ''' Merge consecutive read chunks called by Guppy. '''
    if call_chunk == None: # first chunk
        return new_call_chunk
    elif new_call_chunk['metadata']['duration'] == 0: # no new data
        return call_chunk
    else:
        full_call = call_chunk
        full_call['datasets']['sequence'] += new_call_chunk['datasets']['sequence']
        full_call['datasets']['qstring'] += new_call_chunk['datasets']['qstring']
        full_call['metadata']['duration'] += new_call_chunk['metadata']['duration']
        full_call['metadata']['num_events'] += new_call_chunk['metadata']['num_events']
        full_call['metadata']['sequence_length'] += new_call_chunk['metadata']['sequence_length']
        return full_call

################################################################################

def main(args):
    global ref, nreads_total

    # init
    args = init(args)
    bed_file = generate_bedfile(args)
    ref = get_reference(args)
    aligner = get_aligner(args)
    write_sam_header(aligner, args)
    done = False
    virus_reads = yield_reads(f"{args.virus_dir}/fast5", True)
    other_reads = yield_reads(f"{args.other_dir}/fast5", False)

    dtw_timer = Timer()
    bc_timer = Timer()
    data_timer = Timer()
    aln_timer = Timer()

    with mp.Pool() as pool:

        # create writer thread for data output
        manager = mp.Manager()
        ru_queue = manager.Queue()
        ru_writer = pool.apply_async(write_ru_data, 
                (ru_queue, args.ru_data_file))

        # initialize basecaller
        basecaller = PyGuppyClient(address=f"127.0.0.1:{args.port}",
                config=args.guppy_config, server_file_load_timeout=100000)
        basecaller.connect()

        # perform read-until
        while not done:

            # select next subset of data
            batch = list(itertools.islice(virus_reads, args.batch_size)) + \
                    list(itertools.islice(other_reads, args.ratio*args.batch_size))

            if not args.basecall:
                ########################
                ######## DTW ###########
                ########################

                # spawn DTW worker threads
                dtw_timer.start()
                jobs = []
                reads = []
                for read in batch:
                    job = pool.apply_async(do_dtw_read_until, 
                            (read, ru_queue, args))
                    jobs.append(job)
                for job in jobs: reads.append(job.get())
                reads = list(filter(None, reads))
                dtw_timer.stop()

                # generate all packets
                packets = []
                for read in reads:
                    packets.append( package_read(
                        read_tag = read.read_tag,
                        read_id = read.read_id,
                        raw_data = read.signal,
                        daq_offset = float(read.daq_offset),
                        daq_scaling = float(read.daq_scaling)
                        )
                    )

                # basecall all packets
                bc_timer.start()
                calls = []                                               
                sent, rcvd = 0, 0                                            
                while sent < len(packets):                               
                    success = basecaller.pass_read(packets[sent])        
                    if not success:                                          
                        print(packets[sent])
                        print('ERROR: Failed to basecall read.')             
                        break                                                
                    else:                                                    
                        sent += 1                                            
                while rcvd < len(packets):                               
                    result = basecaller.get_completed_reads()                
                    rcvd += len(result)                                      
                    calls.extend(result)                                 
                bc_timer.stop()

                # align all basecalls
                aln_timer.start()
                alns = []
                for call in calls:
                    try:
                        alignment = next(aligner.map(call['datasets']['sequence']))
                        alns.append(alignment)
                    except(StopIteration):
                        pass # no alignment, can ignore for read-until
                aln_timer.stop()

                for read, call, aln in zip(reads, calls, alns):
                    write_fastq_data(read.read_id, call['datasets']['sequence'], call['datasets']['qstring'], args)
                    write_sam_data(read.read_id, call['datasets']['sequence'], call['datasets']['qstring'], aln, args)

            else:
                ########################
                ####### Basecall #######
                ########################

                read_status_call = {}
                for read in batch:
                    # keep track of read data, if in progress, calls thus far
                    read_status_call[read.read_tag] = [read, True, None]
                prev_length = 0
                lengths = [int(l) for l in args.chunk_lengths.split(",")]
                for length in lengths:

                    # generate all packets
                    all_packets = []
                    for read_tag, [read, status, call] in read_status_call.items():
                        if not status: continue
                        if len(read.signal) <= prev_length: continue
                        all_packets.append( package_read(
                            read_tag = read.read_tag,
                            read_id = read.read_id,
                            raw_data = read.signal \
                                    [prev_length:args.trim_start+length],
                            daq_offset = float(read.daq_offset),
                            daq_scaling = float(read.daq_scaling)
                            )
                        )

                    # basecall all packets
                    bc_timer.start()
                    sent, rcvd = 0, 0
                    while sent < len(all_packets):
                        success = basecaller.pass_read(all_packets[sent])
                        if not success: 
                            print('ERROR: Failed to basecall read.')
                            break
                        else: 
                            sent += 1
                    while rcvd < len(all_packets):
                        calls = basecaller.get_completed_reads()
                        rcvd += len(calls)
                        for call in calls:
                            read_status_call[call['read_tag']][2] = \
                                 merge_calls(read_status_call[call['read_tag']][2], call)
                    bc_timer.stop()

                    # align
                    for read_tag, [read, status, call] in read_status_call.items():
                        if not status: continue
                        try:
                            aln_timer.start()
                            aln = next(aligner.map(call['datasets']['sequence']))
                            aln_timer.stop()
                            if len(read.signal) <= args.trim_start+length: # read finished
                                ru_queue.put(f"{read.is_virus}\t{read.file_name}\t{read.read_id}\t" \
                                        f"{len(read.signal)}\t{aln.mapq}\tTrue\n")
                                write_fastq_data(read.read_id, call['datasets']['sequence'], call['datasets']['qstring'], args)
                                write_sam_data(read.read_id, call['datasets']['sequence'], call['datasets']['qstring'], aln, args)
                                read_status_call[read_tag][1] = False
                        except(StopIteration): # fail
                            aln_timer.stop()
                            read_status_call[read_tag][1] = False
                            ru_queue.put(f"{read.is_virus}\t{read.file_name}\t{read.read_id}\t" \
                                    f"{length}\t0\tFalse\n")

                    prev_length = args.trim_start + length

                # finish calling all reads which succeeded
                all_packets = []
                for [read, status, call] in read_status_call.values():
                    if len(read.signal) <= lengths[-1]+args.trim_start: continue
                    if status: # passed all thresholds
                        all_packets.append( package_read(
                            read_tag = read.read_tag,
                            read_id = read.read_id,
                            raw_data = read.signal[prev_length:],
                            daq_offset = float(read.daq_offset),
                            daq_scaling = float(read.daq_scaling)
                            )
                        )
                # basecall all packets
                bc_timer.start()
                sent, rcvd = 0, 0
                while sent < len(all_packets):
                    success = basecaller.pass_read(all_packets[sent])
                    if not success: 
                        print('ERROR: Failed to basecall read.')
                        break
                    else: 
                        sent += 1
                while rcvd < len(all_packets):
                    calls = basecaller.get_completed_reads()
                    rcvd += len(calls)
                    for call in calls:
                        try:
                            read_status_call[call['read_tag']][2] = \
                                 merge_calls(read_status_call[call['read_tag']][2], call)
                        except KeyError: pass
                bc_timer.stop()
                for read_tag, [read, status, call] in read_status_call.items():
                    if not status: continue
                    try:
                        aln_timer.start()
                        aln = next(aligner.map(call['datasets']['sequence']))
                        aln_timer.stop()
                        ru_queue.put(f"{read.is_virus}\t{read.file_name}\t{read.read_id}\t" \
                                f"{len(read.signal)}\t{aln.mapq}\tTrue\n")
                        write_fastq_data(read.read_id, call['datasets']['sequence'], call['datasets']['qstring'], args)
                        write_sam_data(read.read_id, call['datasets']['sequence'], call['datasets']['qstring'], aln, args)
                    except(StopIteration): # fail
                        aln_timer.stop()
                        read_status_call[read_tag][1] = False
                        ru_queue.put(f"{read.is_virus}\t{read.file_name}\t{read.read_id}\t" \
                                f"{length}\t0\tFalse\n")

            nreads_total += (1 + args.ratio) * args.batch_size
            bam_file = generate_bam(args)
            done = update_coverage(bed_file, bam_file, args)
            done = done or nreads_total > args.max_reads

        # stop read-until writer
        ru_queue.put('kill')
        ru_writer.get()

    print(f"\nDTW Timer:\t{dtw_timer.elapsed()} seconds")
    print(f"Guppy Timer:\t{bc_timer.elapsed()} seconds")
    print(f"Minimap2 Timer:\t{aln_timer.elapsed()} seconds")

################################################################################

def parser():
    parser = argparse.ArgumentParser()

    # guppy parameters
    parser.add_argument("--basetype", default="dna")
    parser.add_argument("--model_type", default="hac")

    # read-until parameters
    parser.add_argument("--virus_dir", default="../data/lambda/DNA/0")
    parser.add_argument("--other_dir", default="../data/human/DNA/0")
    parser.add_argument("--basecall", action="store_true", default=False)
    parser.add_argument("--ratio", type=int, default=10)

    # run-until parameters
    parser.add_argument("--target_coverage", type=int, default=1)
    parser.add_argument("--max_reads", type=int, default=500)
    parser.add_argument("--region_size", type=int, default=10000)
    parser.add_argument("--batch_size", type=int, default=10)

    # output data parameters
    parser.add_argument("--ru_data_file", default="default")
    parser.add_argument("--fastq_file", default="default")
    parser.add_argument("--sam_file", default="default")

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
