import argparse
import random
import multiprocessing as mp
import os

from ont_fast5_api.fast5_interface import get_fast5_file
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import mappy
import h5py
from numba import njit
from sklearn import metrics

import pyguppyclient
from pyguppyclient.decode import ReadData

def yield_read_chunks(filename, start, length):
    with get_fast5_file(filename, 'r') as f5_fh:
        for read in f5_fh.get_reads():
            raw = read.handle[read.raw_dataset_name][start:start+length]
            if len(raw) < length: continue
            channel_info = read.handle[read.global_key + 'channel_id'].attrs
            scaling = channel_info['range'] / channel_info['digitisation']
            offset = int(channel_info['offset'])
            yield ReadData(raw, read.read_id, scaling=scaling, offset=offset)

################################################################################

def init(args):

    # parse input lengths and thresholds
    lengths = [int(l) for l in args.chunk_lengths.split(",")]
    thresholds = [int(t) for t in args.chunk_thresholds.split(",")]

    return lengths, thresholds

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
    if args.nucleotide_type == "dna":
        guppy_config = f"/opt/ont/guppy/data/dna_r9.4.1_450bps_{args.model}.cfg"
    else:
        guppy_config = f"/opt/ont/guppy/data/rna_r9.4.1_70bps_{args.model}.cfg"

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
    with open(f"../data/{args.nucleotide_type}_kmer_model.txt", 'r') as model_file:
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
    k = 6 if args.nucleotide_type == "dna" else 5
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
            if len(signal) < args.trim_start+length: continue
            if read_type=="virus" and read_name[5:] not in [x.split()[0] for x in \
                    open(folder+"/aligned/calls_to_ref.sam").readlines()]: continue
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

def plot_data(length, threshold, ba_virus, ba_other, dtw_virus, dtw_other):

    # plot raw Basecall-Align Histograms
    fig, ax = plt.subplots()
    ax.set_xlim((0, 61))
    ax.hist(ba_virus, bins=list(range(61)), facecolor='r', alpha=0.5)
    ax.hist(ba_other, bins=list(range(61)), facecolor='g', alpha=0.5)
    ax.legend(['COVID', 'Human'])
    ax.set_xlabel('MiniMap Map Quality')
    ax.set_ylabel('Read Count')
    ax.set_title(f"Basecall-Align MapQ: {length} signals")
    fig.savefig(f"../img/accuracy/ba_hist_{length}.png")

    # plot raw DTW Histograms
    fig, ax = plt.subplots()
    ax.set_xlim((0, threshold*2))
    ax.hist(dtw_virus, bins=list(range(0,threshold*2, 1000)), 
            facecolor='r', alpha=0.5)
    ax.hist(dtw_other, bins=list(range(0,threshold*2, 1000)), 
            facecolor='g', alpha=0.5)
    ax.legend(['COVID', 'Human'])
    ax.set_xlabel('DTW Alignment Score')
    ax.set_ylabel('Read Count')
    ax.axvline(threshold, color='k', linestyle='--')
    ax.set_title(f"DTW-Align Score: {length} signals")
    fig.savefig(f"../img/accuracy/dtw_hist_{length}.png")

    # create thresholds for plotting
    ba_thresholds = np.linspace(
            min(np.min(ba_virus), np.min(ba_other))-1, 
            max(np.max(ba_virus), np.max(ba_other))+1, num=100)
    dtw_thresholds = np.linspace(
            min(np.min(dtw_virus), np.min(dtw_other))-1, 
            max(np.max(dtw_virus), np.max(dtw_other))+1, num=100)

    # calculate discard rate of each
    ba_virus_discard_rate, ba_other_discard_rate = [], []
    dtw_virus_discard_rate, dtw_other_discard_rate = [], []
    for t in ba_thresholds:
        ba_virus_discard_rate.append(sum(ba_virus < t) / len(ba_virus))
        ba_other_discard_rate.append(sum(ba_other < t) / len(ba_other))
    for t in dtw_thresholds:
        dtw_virus_discard_rate.append(sum(dtw_virus > t) / len(dtw_virus))
        dtw_other_discard_rate.append(sum(dtw_other > t) / len(dtw_other))

    # plot basecall-align discard rate
    fig, ax = plt.subplots()
    ax.plot(ba_virus_discard_rate, ba_other_discard_rate, marker='o', alpha=0.5)
    ax.set_xlabel('Virus Discard Rate')
    ax.set_ylabel('Human Discard Rate')
    ax.set_title(f'Basecall-Align Accuracy: {length} signals')
    ax.set_xlim((-0.1, 1.1))
    ax.set_ylim((-0.1, 1.1))
    fig.savefig(f'../img/accuracy/ba_discard_{length}.png')

    # plot dtw-align discard rate
    fig, ax = plt.subplots()
    ax.plot(dtw_virus_discard_rate, dtw_other_discard_rate, marker='o', alpha=0.5)
    ax.set_xlabel('Virus Discard Rate')
    ax.set_ylabel('Human Discard Rate')
    ax.set_title(f'DTW-Align Accuracy: {length} signals')
    ax.set_xlim((-0.1, 1.1))
    ax.set_ylim((-0.1, 1.1))
    fig.savefig(f'../img/accuracy/dtw_discard_{length}.png')

################################################################################

def print_cm(threshold, ba_virus_scores, ba_other_scores, 
        dtw_virus_scores, dtw_other_scores):

    print("\nBasecall-Align")
    # print(ba_virus_scores)
    # print(ba_other_scores)

    ba_pred = [x >= 1 for x in ba_virus_scores] + \
              [x >= 1 for x in ba_other_scores]
    ba_truth = [True]*len(ba_virus_scores) + [False]*len(ba_other_scores)
    ba_cm = metrics.confusion_matrix(ba_pred, ba_truth)
    print(ba_cm)

    print("\nDTW-Align")
    # print(dtw_virus_scores)
    # print(dtw_other_scores)

    dtw_pred = [x < threshold for x in dtw_virus_scores] + \
              [x < threshold for x in dtw_other_scores]
    dtw_truth = [True]*len(dtw_virus_scores) + [False]*len(dtw_other_scores)
    dtw_cm = metrics.confusion_matrix(dtw_pred, dtw_truth)
    print(dtw_cm)

################################################################################

def save_scores(length, threshold, ba_virus_scores, ba_other_scores, 
        dtw_virus_scores, dtw_other_scores, args):
    np.save(args.out_data_dir + 
            f"/{args.max_virus_reads}reads_{length}sigs_ba_virus", ba_virus_scores)
    np.save(args.out_data_dir + 
            f"/{args.max_virus_reads}reads_{length}sigs_ba_other", ba_other_scores)
    np.save(args.out_data_dir + 
            f"/{args.max_virus_reads}reads_{length}sigs_dtw_virus", dtw_virus_scores)
    np.save(args.out_data_dir + 
            f"/{args.max_virus_reads}reads_{length}sigs_dtw_other", dtw_other_scores)
    return

def load_scores(read_type, method, length, args):
    filename = f"{args.out_data_dir}/{args.max_virus_reads}reads_{length}sigs_{method}_{read_type}.npy"
    if not os.path.exists(filename):
        print(f"ERROR: cannot load scores from '{filename}', not found.")
        exit(1)
    else:
        return np.load(filename)

################################################################################

def main(args):

    lengths, thresholds = init(args)
    for length, threshold in zip(lengths, thresholds):

        print(f"\nChunk length: {length}")
        if args.load_scores:
            ba_virus_scores = load_scores('virus', 'ba', length, args)
            ba_other_scores = load_scores('other', 'ba', length, args)
            dtw_virus_scores = load_scores('virus', 'dtw', length, args)
            dtw_other_scores = load_scores('other', 'dtw', length, args)
        else:
            ba_virus_scores = basecall_align('virus', length, args)
            ba_other_scores = basecall_align('other', length, args)
            dtw_virus_scores = dtw_align('virus', length, args)
            dtw_other_scores = dtw_align('other', length, args)

        if args.save_scores:
            print("Saving Scores...")
            save_scores(length, threshold, ba_virus_scores, ba_other_scores, 
                    dtw_virus_scores, dtw_other_scores, args)
        if args.plot_results:
            print("Plotting Results...")
            plot_data(length, threshold, ba_virus_scores, ba_other_scores, 
                    dtw_virus_scores, dtw_other_scores)

        print_cm(threshold, ba_virus_scores, ba_other_scores, 
                dtw_virus_scores, dtw_other_scores)

################################################################################

def parser():
    parser = argparse.ArgumentParser()

    # guppy parameters
    parser.add_argument("--nucleotide_type", default="dna")
    parser.add_argument("--model", default="hac")

    parser.add_argument("--virus_dir", default="/x/squiggalign_data/lambda")
    parser.add_argument("--other_dir", default="/x/squiggalign_data/human")
    parser.add_argument("--out_data_dir", default="/home/timdunn/SquiggAlign/data/accuracy")

    parser.add_argument("--trim_start", type=int, default=1000)
    parser.add_argument("--chunk_lengths", 
            default="1000,2000,3000,4000,5000,6000,7000")
    parser.add_argument("--chunk_thresholds", 
            default="5500,11000,15000,19000,24000,29000,34000")
    parser.add_argument("--max_virus_reads", type=int, default=1000)
    parser.add_argument("--max_other_reads", type=int, default=1000)
    parser.add_argument("--save_scores", action="store_true", default=False)
    parser.add_argument("--load_scores", action="store_true", default=False)
    parser.add_argument("--plot_results", action="store_true", default=False)

    return parser

################################################################################

if __name__ == "__main__":
    parser = parser()
    args = parser.parse_args()
    main(args)
