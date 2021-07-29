from sklearn import metrics
from itertools import repeat
from numba import njit
from glob import glob
from scipy import stats
from pyguppy_client_lib.pyclient import PyGuppyClient
from pyguppy_client_lib.helper_functions import package_read, basecall_with_pyguppy

import random, h5py, re, os, mappy

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import multiprocessing as mp
import seaborn as sns

### FUNCTIONS ###
def get_fasta(fasta_fn):
    ''' Get sequence from FASTA filename. '''
    with open(fasta_fn, 'r') as fasta:
        return ''.join(fasta.read().split('\n')[1:])

    
    
def rev_comp(bases):
    ''' Get reverse complement of sequence. '''
    return bases.replace('A','t').replace('T','a').replace('G','c').replace('C','g').upper()[::-1]



def load_model(kmer_model_fn):
    ''' Load k-mer model file into Python dict. '''
    kmer_model = {}
    with open(kmer_model_fn, 'r') as model_file:
        for line in model_file:
            kmer, current = line.split()
            kmer_model[kmer] = float(current)
    return kmer_model



def discrete_normalize(seq, bits=8, minval=-4, maxval=4):
    ''' Approximate normalization which converts signal to integer of desired precision. '''
    mean = int(np.mean(seq))
    mean_avg_dev = int(np.mean(np.abs(seq - mean)))
    norm_seq = (seq - mean) / mean_avg_dev
    
    norm_seq[norm_seq < minval] = minval
    norm_seq[norm_seq > maxval] = maxval 
    norm_seq = ( (norm_seq - minval) * (2**(bits)/(maxval-minval)) ).astype(int)
    return norm_seq



def ref_signal(fasta, kmer_model):
    ''' Convert reference FASTA to expected reference signal (z-scores). '''
    signal = np.zeros(len(fasta))
    for kmer_start in range(len(fasta)-k):
        signal[kmer_start] = kmer_model[fasta[kmer_start:kmer_start+k]]
    return discrete_normalize(signal*100) # increase dist between floats before rounding



def get_stall_end(signal, stall_threshold=3, 
                  stall_events=2, stall_event_len=3):
    ''' Determine the end of the DNA stall region. '''
    
    # take average of a few samples to reduce variation
    events = []
    for event in range(0, len(signal), stall_event_len):
        events.append(np.mean(signal[event:event+stall_event_len]))
    
    # find where we exceed threshold for a few consecutive events
    above_threshold_count = 0
    event_pos = 0
    for event in events:
        event_pos += 1
        if event > stall_threshold:
            above_threshold_count += 1
        else:
            above_threshold_count = 0
        if above_threshold_count == stall_events:
            break
            
    # find where we go back below threshold
    below_threshold_count = 0
    for event in events[event_pos:]:
        event_pos += 1
        if event < stall_threshold:
            below_threshold_count += 1
        else:
            below_threshold_count = 0
        if below_threshold_count == stall_events:
            break
            
    return event_pos * stall_event_len



def trim(signal):
    ''' Trims signal by detecting stall (and eventually adapter). '''
    stall_end = get_stall_end(stats.zscore(signal))
    return signal[stall_end+1000 : stall_end+1000+max(prefix_lengths)], stall_end



def filter_outliers(signal, minval=-4, maxval=4):
    
    # return empty signals as-is
    if not len(signal): return signal
    
    # upper threshold
    for idx, x in enumerate(signal):
        if x > maxval:
            # other values above max -> threshold to max
            if (idx+1 < len(signal) and signal[idx+1] > 3) or \
            (idx > 0 and signal[idx-1] > maxval):
                signal[idx] = maxval
            # otherwise, single outlier -> interpolate
            elif idx == 0:
                signal[idx] = signal[1]
            elif idx+1 == len(signal):
                signal[idx] = signal[idx-1]
            else:
                signal[idx] = (signal[idx-1] + signal[idx+1]) / 2
                
    # lower threshold
    for idx, x in enumerate(signal):
        if x < minval:
            # other values below min -> threshold to min
            if (idx+1 < len(signal) and signal[idx+1] < -3) or \
            (idx > 0 and signal[idx-1] < minval):
                signal[idx] = minval
            # otherwise, single outlier -> interpolate
            elif idx == 0:
                signal[idx] = signal[1]
            elif idx+1 == len(signal):
                signal[idx] = signal[idx-1]
            else:
                signal[idx] = (signal[idx-1] + signal[idx+1]) / 2
                
    return signal



class Read():            
    def __init__(self, signal, read_id, offset=0, scaling=1.0):                                         
        self.signal = signal
        self.read_id = read_id
        self.total_samples = len(signal)
        self.daq_offset = offset
        self.daq_scaling = scaling
        self.read_tag = random.randint(0, int(2**32 - 1))  

        
        
def ba_preprocess_read(uuid, length):
    readname = f"read_{uuid}"
    fast5_file = h5py.File(full_index[uuid], 'r')
    signal = np.array(fast5_file[readname]['Raw']['Signal'][:], dtype=np.int16)
    signal, trimmed = trim(signal)
    if len(signal) < max(prefix_lengths): return None
    signal_dig = fast5_file[readname]['channel_id'].attrs['digitisation']
    signal_offset = fast5_file[readname]['channel_id'].attrs['offset']
    signal_range = fast5_file[readname]['channel_id'].attrs['range']
    signal_scaling = signal_range / signal_dig
    return Read(signal, readname, offset=signal_offset, scaling=signal_scaling)

    
    
def preprocess_read(uuid):
    ''' Return preprocessed read from specified FAST5 file. '''
    readname = f"read_{uuid}"
    fast5_file = h5py.File(full_index[uuid], 'r')
    signal = np.array(fast5_file[readname]['Raw']['Signal'][:], dtype=np.int16)
    length = signal.shape[0]
    signal, trimmed = trim(signal)
    if len(signal) < max(prefix_lengths): return None
    new_signal = np.array(signal, dtype=float)
    for start in range(0, len(signal), 500):
        new_signal[start:start+500] = \
            discrete_normalize(signal[:start+500])[start:start+500]
    return new_signal, trimmed, length



def get_index(index_filename):
    ''' Read index data structure from file. '''
    index_file = open(index_filename, 'r')
    index = {}
    for line in index_file:
        uuid, fname = re.split(r'\t+', line)
        index[uuid] = fname.rstrip()
    index_file.close()
    return index



def create_index(fast5_dir, force=False):
    '''
    Create file which stores read FAST5 to UUID mappings. 
    '''

    # return existing index if possible
    index_fn = f'{fast5_dir}/index.db'
    if not force and os.path.exists(index_fn):
        return get_index(index_fn)

    # remove existing index
    if os.path.exists(index_fn):
        os.remove(index_fn)

    # create new index    
    index_file = open(index_fn, 'w')

    # iterate through all FAST5 files in directory
    for subdir, dirs, files in os.walk(fast5_dir):
        for filename in files:
            ext = os.path.splitext(filename)[-1].lower()
            if ext == ".fast5":

                # print read uuid and filename to index
                fast5_file = h5py.File(os.path.join(subdir, filename), 'r')
                if 'Raw' in fast5_file: # single-FAST5
                    for readname in fast5_file['Raw']['Reads']:
                        uuid = fast5_file['Raw']['Reads'][readname].attrs['read_id']
                        print('{}\t{}'.format(uuid.decode('utf-8'), \
                                os.path.join(subdir, filename)), file=index_file)
                else: # multi-FAST5
                    for readname in fast5_file:
                        uuid = readname[5:] # remove 'read_' naming prefix
                        print('{}\t{}'.format(uuid, \
                                os.path.join(subdir, filename)), file=index_file)

    # cleanup and return results
    index_file.close()
    return get_index(index_fn)



def segment(signal):
    width = 5
    min_obs = 1
    npts = int((len(signal)*450)/4000)

    # get difference between all neighboring 'width' regions
    cumsum = np.cumsum(np.concatenate([[0.0], signal]))
    cand_poss = np.argsort(np.abs( (2 * cumsum[width:-width]) -
        cumsum[:-2*width] - cumsum[2*width:])).astype(int)[::-1]
    vals = np.abs( (2 * cumsum[width:-width]) - cumsum[:-2*width] - cumsum[2*width:])

    # keep 'npts' best checkpoints
    chkpts = []
    cand_idx = 0
    ct = 0
    blacklist = set()
    while ct < npts:
        edge_pos = cand_poss[cand_idx]
        if edge_pos not in blacklist:
            chkpts.append(edge_pos+width)
            ct += 1

            # blacklist nearby values (only use peaks)
            right = 0
            while edge_pos+right+1 < len(vals) and vals[edge_pos + right] > vals[edge_pos + right+1]:
                right += 1
                blacklist.add(edge_pos+right)
            left = 0
            while edge_pos+left > 0 and vals[edge_pos + left] > vals[edge_pos + left-1]:
                left -= 1
                blacklist.add(edge_pos+left)
        cand_idx += 1

    chkpts = np.sort(chkpts)
    new_signal = [np.mean(signal[0:chkpts[0]])]
    for i in range(len(chkpts)-1):
        new_signal.append(np.mean(signal[chkpts[i]:chkpts[i+1]]))
    return np.array(new_signal)



@njit()
def sdtw(seq):
    ''' Returns minimum alignment score for subsequence DTW. '''
    
    # initialize cost matrix
    cost_mat = np.zeros((len(seq), len(ref)))
    cost_mat[0, 0] = abs(seq[0]-ref[0])
    for i in range(1, len(seq)):
        cost_mat[i, 0] = cost_mat[i-1, 0] + abs(seq[i]-ref[0])
    
    prev_consec = np.zeros((len(seq)))
    curr_consec = np.zeros((len(seq)))
    
    # compute entire cost matrix
    for j in range(1, len(ref)):
        bonus = 10
        for i in range(1, len(seq)):
            move = cost_mat[i-1, j-1] - prev_consec[i-1]*bonus < cost_mat[i-1, j]
            if move:
                curr_consec[i] = 0
                cost_mat[i, j] = cost_mat[i-1, j-1] - prev_consec[i-1]*bonus + abs(seq[i]-ref[j])
            else:
                curr_consec[i] = min(10, prev_consec[i] + 1)
                cost_mat[i, j] = cost_mat[i-1, j] + abs(seq[i]-ref[j])
        prev_consec = curr_consec[:]
        curr_consec = np.zeros((len(seq)))
    
    # return cost of optimal alignment
    cost_mins = np.zeros((len(prefix_lengths),))
    for i in range(len(prefix_lengths)):
        if prefix_lengths[i] <= len(seq):
            cost_mins[i] = min(cost_mat[prefix_lengths[i]-1,:])
    return cost_mins



def get_stats(virus_scores, other_scores, thresh):
    ''' Return F-scores (assumes sorted input). '''
    fscores = np.zeros(nprefixes)
    precs = np.zeros(nprefixes)
    recalls = np.zeros(nprefixes)
    for i in range(nprefixes):
        # short reads don't receive a score, so ignore in accuracy metrics
        long_virus = np.count_nonzero(virus_scores[i])
        short_virus = virus_scores.shape[1]-long_virus
        tp = np.searchsorted(virus_scores[i], thresh) - short_virus
        fn = long_virus - tp
        long_other = np.count_nonzero(other_scores[i])
        short_other = other_scores.shape[1]-long_other
        fp = np.searchsorted(other_scores[i], thresh) - short_other
        precs[i] = 0 if not tp+fp else tp / (tp+fp)
        recalls[i] = 0 if not tp+fn else tp / (tp+fn)  
        fscores[i] = 0 if not tp+fp+fn else tp / (tp + 0.5*(fp + fn))
    return fscores, precs, recalls



def sub_fasta(fasta, n):
    positions = random.sample(range(len(fasta)), n)
    bases='ACGT'
    for pos in positions:
        fasta = fasta[:pos] + \
                bases[ (bases.find(fasta[pos]) + random.randint(0, 3)) % 4 ] + \
                fasta[pos+1:]
    return fasta



def ins_fasta(fasta, n):
    positions = sorted(random.sample(range(len(fasta)), n))
    bases='ACGT'
    new_fasta = ''
    prev_pos = 0
    for pos in positions:
        new_fasta += fasta[prev_pos:pos] + random.sample(bases, 1)[0]
        prev_pos = pos
    new_fasta += fasta[prev_pos:] # works if positions == []
    return new_fasta



def del_fasta(fasta, n):
    lfasta = list(fasta)
    for i in range(n):
        lfasta.pop(random.randrange(len(lfasta)))
    return ''.join(lfasta)



### PROGRAM ###

if __name__ == "__main__":

    # globals for data
    data_dir = "../data"
    kmer_model_fn, k = f"{data_dir}/dna_kmer_model.txt", 6 # 6-mer model
    virus, other, virus_dna_type, other_dna_type, virus_ds, other_ds = "lambda", "human", "DNA", "DNA", "0", "2"
    ref_fn = f"{data_dir}/{virus}/{virus_dna_type}/{virus_ds}/reference.fasta"
    virus_fast5_dir = f"{data_dir}/{virus}/{virus_dna_type}/{virus_ds}/fast5"
    other_fast5_dir = f"{data_dir}/{other}/{other_dna_type}/{other_ds}/fast5"
    results_dir = f"./results/mutations"
    virus_max_reads = 1000
    other_max_reads = 1000
    prefix_lengths = np.array([2000])
    nprefixes = 1

    # create read UUID -> FAST5 filename mapping
    print('Creating indices...', end='')
    virus_index = create_index(virus_fast5_dir)
    other_index = create_index(other_fast5_dir)
    full_index = {**virus_index, **other_index}
    print('done!')

    # select random subset of reads
    random.seed(42)
    virus_readnames = random.choices(list(virus_index.keys()), k=virus_max_reads*2)
    random.seed(11)
    other_readnames = random.choices(list(other_index.keys()), k=other_max_reads*2)

    # trim all reads
    print('Trimming reads...', end='')
    with mp.Pool() as pool:
        virus_reads, virus_trims, virus_lengths = \
            list(map(list, zip(*filter(None, pool.map(preprocess_read, virus_readnames)))))
        other_reads, other_trims, other_lengths = \
            list(map(list, zip(*filter(None, pool.map(preprocess_read, other_readnames)))))
    if len(virus_reads) < virus_max_reads:
        print(f'ERROR: only {len(virus_reads)} virus reads long enough, requested {virus_max_reads}')
    if len(other_reads) < other_max_reads:
        print(f'ERROR: only {len(other_reads)} other reads long enough, requested {other_max_reads}')
    virus_reads, virus_trims, virus_lengths = virus_reads[:virus_max_reads], \
        virus_trims[:virus_max_reads], virus_lengths[:virus_max_reads]
    other_reads, other_trims, other_lengths = other_reads[:other_max_reads], \
        other_trims[:other_max_reads], other_lengths[:other_max_reads]
    print('done!')



    # iterate over different number of ref mutations
    for mut_type in ['del']:
        print(' ')
        for n_mut in [0,2,5,10,20,50,100,200,500,1000,2000,5000,10000,20000]:
            print(f'{n_mut} reference {mut_type}s...,', end='')

            # mutate reference
            ref_fasta = get_fasta(ref_fn)
            if mut_type == 'sub':
                ref_fasta = sub_fasta(ref_fasta, n_mut)
            elif mut_type == 'ins':
                ref_fasta = ins_fasta(ref_fasta, n_mut)
            elif mut_type == 'del':
                ref_fasta = del_fasta(ref_fasta, n_mut)
            kmer_model = load_model(kmer_model_fn)
            fwd_ref_sig = ref_signal(ref_fasta, kmer_model)
            rev_ref_sig = ref_signal(rev_comp(ref_fasta), kmer_model)
            ref = np.concatenate((fwd_ref_sig, rev_ref_sig))

            # limit cores since each aligner takes ~4GB of RAM to align
            print('aligning,', end='')
            with mp.Pool(15) as pool:
                virus_scores_list = pool.map(sdtw, virus_reads)
                other_scores_list = pool.map(sdtw, other_reads)

            # move data to numpy array for easy sorting/calculations
            virus_scores = np.zeros((nprefixes, len(virus_scores_list)))
            for idx, scores in enumerate(virus_scores_list):
                for i in range(nprefixes):
                    virus_scores[i,idx] = scores[i]
            other_scores = np.zeros((nprefixes, len(other_scores_list)))
            for idx, scores in enumerate(other_scores_list):
                for i in range(nprefixes):
                    other_scores[i,idx] = scores[i]

            # save results
            os.makedirs(results_dir, exist_ok=True)
            print('saving,', end='')
            np.save(f"{results_dir}/prefix_lengths{n_mut}{mut_type}", prefix_lengths)
            np.save(f"{results_dir}/virus_trims{n_mut}{mut_type}", virus_trims)
            np.save(f"{results_dir}/virus_lengths{n_mut}{mut_type}", virus_lengths)
            np.save(f"{results_dir}/virus_scores{n_mut}{mut_type}", virus_scores)
            np.save(f"{results_dir}/other_trims{n_mut}{mut_type}", other_trims)
            np.save(f"{results_dir}/other_lengths{n_mut}{mut_type}", other_lengths)
            np.save(f"{results_dir}/other_scores{n_mut}{mut_type}", other_scores)

            # load results
            print('loading,', end='')
            prefix_lengths = np.load(f"{results_dir}/prefix_lengths{n_mut}{mut_type}.npy")
            virus_trims = np.load(f"{results_dir}/virus_trims{n_mut}{mut_type}.npy")
            virus_lengths = np.load(f"{results_dir}/virus_lengths{n_mut}{mut_type}.npy")
            virus_scores = np.load(f"{results_dir}/virus_scores{n_mut}{mut_type}.npy")
            other_trims = np.load(f"{results_dir}/other_trims{n_mut}{mut_type}.npy")
            other_lengths = np.load(f"{results_dir}/other_lengths{n_mut}{mut_type}.npy")
            other_scores = np.load(f"{results_dir}/other_scores{n_mut}{mut_type}.npy")

            # sort arrays (for fast f-score calculation)
            print('sorting,', end='')
            virus_scores = np.sort(virus_scores)
            other_scores = np.sort(other_scores)
            min_score = min(np.min(virus_scores), np.min(other_scores))
            max_score = max(np.max(virus_scores), np.max(other_scores))

            # calculate all f-scores, and save the best thresholds
            print('f-scoring,', end='')
            best_fscores = np.zeros(nprefixes)
            best_precs = np.zeros(nprefixes)
            best_recalls = np.zeros(nprefixes)
            fscores, precs, recalls = get_stats(virus_scores, other_scores, 13274)
            for i in range(nprefixes):
                if fscores[i] > best_fscores[i]:
                    best_fscores[i] = fscores[i]
                    best_precs[i] = precs[i]
                    best_recalls[i] = recalls[i]

            np.save(f"{results_dir}/fscores{n_mut}{mut_type}", best_fscores)
            np.save(f"{results_dir}/precisions{n_mut}{mut_type}", best_precs)
            np.save(f"{results_dir}/recalls{n_mut}{mut_type}", best_recalls)
            print(f'{best_fscores}done!')
