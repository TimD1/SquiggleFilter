import argparse
import random
import multiprocessing as mp
import os

from ont_fast5_api.fast5_interface import get_fast5_file
from glob import glob
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams.update({'font.size': 20})
import numpy as np
import mappy
import h5py
from numba import njit
from sklearn import metrics
from scipy import stats

from pyguppy_client_lib.pyclient import PyGuppyClient                            
from pyguppy_client_lib.helper_functions import package_read, basecall_with_pyguppy

class Read():
    def __init__(self, signal, read_id, offset=0, scaling=1.0):
        self.signal = signal                                                     
        self.read_id = read_id                                                   
        self.total_samples = len(signal)                                         
        self.daq_offset = offset                                                 
        self.daq_scaling = scaling                                               
        self.read_tag = random.randint(0, int(2**32 - 1))   

def yield_read_chunks(filename, start, length):
    with get_fast5_file(filename, 'r') as f5_fh:
        for read in f5_fh.get_reads():
            raw = read.handle[read.raw_dataset_name][start:start+length]
            if len(raw) < length: continue
            channel_info = read.handle[read.global_key + 'channel_id'].attrs
            scaling = channel_info['range'] / channel_info['digitisation']
            offset = int(channel_info['offset'])
            yield Read(raw, read.read_id, offset=offset, scaling=scaling)

################################################################################

def init(args):

    basetypes = ["RNA", "DNA", "rtDNA"]
    if args.basetype not in basetypes:
        print(f"ERROR: base type '{args.basetype}' not in {basetypes}.")
        exit(1)

    args.virus_dir = f"{args.main_dir}/{args.virus_species}/" \
                     f"{args.basetype}/{args.virus_dataset}"
    args.other_dir = f"{args.main_dir}/{args.other_species}/" \
                     f"{args.basetype}/{args.other_dataset}"
    args.score_dir = f"{args.main_dir}/scores/{args.basetype}/" \
                     f"{args.virus_species}{args.virus_dataset}_" \
                     f"{args.other_species}{args.other_dataset}"
    args.img_dir = f"{args.main_dir}/img/{args.basetype}/" \
                     f"{args.virus_species}{args.virus_dataset}_" \
                     f"{args.other_species}{args.other_dataset}"
    if args.save_scores:
        os.makedirs(args.score_dir, exist_ok=True)
    if args.plot_results:
        os.makedirs(args.img_dir, exist_ok=True)

    if args.basetype[-3:].lower() == "dna":
        args.ru_lengths = list(range(1000, 10001, 1000))
        args.ru_thresholds = [
                3900, 7750, 12000, 16500, 20000, 
                24000, 29500, 33000, 37000, 40000]
        args.guppy_config = f"dna_r9.4.1_450bps_{args.model}.cfg"
        args.port = 1234
        args.preset = "map-ont"
        args.k = 15
    else:
        args.ru_lengths = list(range(5000, 50001, 5000))
        args.ru_thresholds = [x*5 for x in args.ru_lengths] 
        args.guppy_config = f"rna_r9.4.1_70bps_{args.model}.cfg"
        args.port = 2345
        args.preset = "splice"
        args.k = 14

    return args

################################################################################

def basecall_align(read_type, length, args):

    folder = args.virus_dir if read_type == "virus" else args.other_dir
    max_reads = args.max_virus_reads if read_type == "virus" else args.max_other_reads

    # initialize mappy aligner
    aligner = mappy.Aligner(
            fn_idx_in = args.virus_dir+"/reference.fasta",
            preset = args.preset,
            best_n = 1,
            k = args.k
    )

    # initialize basecaller
    basecaller = PyGuppyClient(address=f"127.0.0.1:{args.port}",     
            config=args.guppy_config, server_file_load_timeout=100000)  
    basecaller.connect() 

    # generate all packets
    all_packets = []
    read_count = 0
    for fast5_fn in glob(folder + "/fast5/*.fast5"):
        for read in yield_read_chunks(fast5_fn, args.trim_start, length):
            read_count += 1
            if read_count >= max_reads: break
            all_packets.append( package_read(
                read_tag = read.read_tag,
                read_id = read.read_id,
                raw_data = read.signal,
                daq_offset = float(read.daq_offset),
                daq_scaling = float(read.daq_scaling)
                )
            )
        if read_count >= max_reads: break

    # basecall all packets
    all_calls = []                                               
    sent, rcvd = 0, 0                                            
    while sent < len(all_packets):                               
        success = basecaller.pass_read(all_packets[sent])        
        if not success:                                          
            print('ERROR: Failed to basecall read.')             
            break                                                
        else:                                                    
            sent += 1                                            
    while rcvd < len(all_packets):                               
        result = basecaller.get_completed_reads()                
        rcvd += len(result)                                      
        all_calls.extend(result)                                 

    # align all basecalls
    scores = np.zeros(max_reads)
    for idx, call in enumerate(all_calls):
        try:
            alignment = next(aligner.map(call['datasets']['sequence']))
            scores[idx] = alignment.mapq
        except(StopIteration):
            pass # no alignment
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

def load_model(args):
    ''' Load k-mer model file into Python dict. '''
    kmer_model = {}
    with open(f"{args.main_dir}/{args.basetype[-3:].lower()}_kmer_model.txt", 'r') as model_file:
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

def ref_signal(fasta, kmer_model, args):
    ''' Convert reference FASTA to expected reference signal (z-scores). '''
    signal = np.zeros(len(fasta))
    k = 6 if args.basetype[-3:].lower() == "dna" else 5
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
    kmer_model = load_model(args)
    fwd_ref_sig = ref_signal(ref_fasta, kmer_model, args)
    rev_ref_sig = ref_signal(rev_comp(ref_fasta), kmer_model, args)
    ref_sig = np.concatenate((fwd_ref_sig, rev_ref_sig))
    if args.basetype[-3:].lower() == "dna":
        ref = ref_sig
    else:
        ref = fwd_ref_sig

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
    if args.virus_species == 'covid':
        virus_name = "SARS-CoV-2"
    else:
        virus_name = "lambda phage"

    # plot raw Basecall-Align Histograms
    fig, ax = plt.subplots(figsize=(10,5))
    ax.set_xlim((0, 61))
    ax.hist(ba_virus, bins=list(range(61)), histtype=u'step', facecolor='r', alpha=0.6)
    ax.hist(ba_other, bins=list(range(61)), histtype=u'step', facecolor='g', alpha=0.6)
    ax.legend([f'{virus_name}', f'{args.other_species}', 'threshold'])
    ax.set_xlabel('MiniMap2 Mapping Quality')
    ax.set_yticks([])
    fig.savefig(f"{args.img_dir}/ba_hist_{length}.png")

    # plot raw DTW Histograms
    fig, ax = plt.subplots()
    ax.set_xlim((0, threshold*2))
    ax.hist(dtw_virus, histtype=u'step', bins=list(range(0,threshold*2, int(threshold/25))), 
            color='r', alpha=0.6, linewidth=4)
    ax.hist(dtw_other, histtype=u'step', bins=list(range(0,threshold*2, int(threshold/25))), 
            color='g', alpha=0.6, linewidth=4)
    ax.axvline(threshold, color='k', linestyle='--')
    # ax.legend(['threshold', f'{virus_name}', f'{args.other_species}'], loc=(1,1))
    # ax.set_xlabel('DTW Alignment Score')
    # ax.set_ylabel('Read Count')
    ax.set_ylim((0,150))
    plt.tight_layout()
    fig.savefig(f"{args.img_dir}/dtw_hist_{length}.png")

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
    ax.set_xlabel(f'{virus_name} Discard Rate')
    ax.set_ylabel(f'{args.other_species} Discard Rate')
    ax.set_xlim((-0.1, 1.1))
    ax.set_ylim((-0.1, 1.1))
    fig.savefig(f'{args.img_dir}/ba_discard_{length}.png')

    # plot dtw-align discard rate
    fig, ax = plt.subplots()
    ax.plot(dtw_virus_discard_rate, dtw_other_discard_rate, marker='o', alpha=0.5)
    ax.set_xlabel(f'{virus_name} Discard Rate')
    ax.set_ylabel(f'{args.other_species} Discard Rate')
    ax.set_xlim((-0.1, 1.1))
    ax.set_ylim((-0.1, 1.1))
    fig.savefig(f'{args.img_dir}/dtw_discard_{length}.png')

################################################################################

def print_cm(threshold, ba_virus_scores, ba_other_scores, 
        dtw_virus_scores, dtw_other_scores):

    print("\nBasecall-Align")
    ba_pred = [x >= 1 for x in ba_virus_scores] + \
              [x >= 1 for x in ba_other_scores]
    ba_truth = [True]*len(ba_virus_scores) + [False]*len(ba_other_scores)
    ba_cm = metrics.confusion_matrix(ba_pred, ba_truth)
    print(ba_cm)

    print("\nDTW-Align")
    dtw_pred = [x < threshold for x in dtw_virus_scores] + \
              [x < threshold for x in dtw_other_scores]
    dtw_truth = [True]*len(dtw_virus_scores) + [False]*len(dtw_other_scores)
    dtw_cm = metrics.confusion_matrix(dtw_pred, dtw_truth)
    print(dtw_cm)

################################################################################

def save_scores(length, threshold, ba_virus_scores, ba_other_scores, 
        dtw_virus_scores, dtw_other_scores, args):

    # save raw scores
    np.save(f"{args.score_dir}/{length}sigs_ba_virus_scores", 
            ba_virus_scores)
    np.save(f"{args.score_dir}/{length}sigs_ba_other_scores", 
            ba_other_scores)
    np.save(f"{args.score_dir}/{length}sigs_dtw_virus_scores", 
            dtw_virus_scores)
    np.save(f"{args.score_dir}/{length}sigs_dtw_other_scores", 
            dtw_other_scores)

    # save accuracy
    ba_virus_discard_rate = sum(ba_virus_scores < 1) / len(ba_virus_scores)
    np.save(f"{args.score_dir}/{length}sigs_ba_virus_discard_rate", 
            ba_virus_discard_rate)
    ba_other_discard_rate = sum(ba_other_scores < 1) / len(ba_other_scores)
    np.save(f"{args.score_dir}/{length}sigs_ba_other_discard_rate", 
            ba_other_discard_rate)
    dtw_virus_discard_rate = sum(dtw_virus_scores > threshold) / len(dtw_virus_scores)
    np.save(f"{args.score_dir}/{length}sigs_dtw_virus_discard_rate", 
            dtw_virus_discard_rate)
    dtw_other_discard_rate = sum(dtw_other_scores > threshold) / len(dtw_other_scores)
    np.save(f"{args.score_dir}/{length}sigs_dtw_other_discard_rate", 
            dtw_other_discard_rate)

    return

def load_scores(read_type, method, length, args):
    filename = f"{args.score_dir}/{length}sigs_{method}_{read_type}_scores.npy"
    if not os.path.exists(filename):
        print(f"ERROR: cannot load scores from '{filename}', not found.")
        exit(1)
    else:
        return np.load(filename)

################################################################################

def main(args):

    args = init(args)
    for length, threshold in zip(args.ru_lengths, args.ru_thresholds):

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

    parser.add_argument("--main_dir", default="/home/timdunn/SquiggAlign/data")
    parser.add_argument("--basetype", default="rtDNA")
    parser.add_argument("--virus_species", default="covid")
    parser.add_argument("--other_species", default="human")
    parser.add_argument("--virus_dataset", default="0")
    parser.add_argument("--other_dataset", default="0")

    parser.add_argument("--model", default="fast")

    parser.add_argument("--trim_start", type=int, default=1000)
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
