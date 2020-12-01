from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import h5py
import random
import numpy as np
from ont_fast5_api.fast5_interface import get_fast5_file
import matplotlib
matplotlib.rcParams.update({'font.size': 22})

main_dir = "/home/timdunn/SquiggAlign/data"
max_reads = 1000

for virus, basetype, other in zip(
        ["covid", "lambda"], 
        ["rtDNA", "DNA"],
        ["human", "human"]):
    if basetype == "DNA":
        virus_color = 'red'
        other_color = 'forestgreen'
        scale = 4000 / 450
        maxlen = 20000
    elif basetype == "RNA":
        virus_color = 'orangered'
        other_color = 'limegreen'
        scale = 4000 / 70
        maxlen = 10000
    elif basetype == "rtDNA":
        virus_color = 'firebrick'
        other_color = 'lawngreen'
        scale = 4000 / 450
        maxlen = 5000

    virus_dir = f"{main_dir}/{virus}/{basetype}/0/fast5"
    other_dir = f"{main_dir}/{other}/{basetype}/0/fast5"

    virus_lengths = []
    virus_reads = 0
    for virus_fast5_fn in glob(f"{virus_dir}/*.fast5"):
        virus_fast5 = h5py.File(virus_fast5_fn, 'r')
        virus_read_list = list(virus_fast5)
        random.shuffle(virus_read_list)
        for read in virus_read_list:
            signal = virus_fast5[read]['Raw']['Signal'][:]
            virus_lengths.append(len(signal))
            if virus_reads > max_reads: break
            else: virus_reads += 1
        if virus_reads > max_reads: break

    other_lengths = []
    other_reads = 0
    for other_fast5_fn in glob(f"{other_dir}/*.fast5"):
        other_fast5 = h5py.File(other_fast5_fn, 'r')
        other_read_list = list(other_fast5)
        random.shuffle(other_read_list)
        for read in other_read_list:
            signal = other_fast5[read]['Raw']['Signal'][:]
            other_lengths.append(len(signal))
            if other_reads > max_reads: break
            else: other_reads += 1
        if other_reads > max_reads: break
    print(np.mean(other_lengths))

    fig, ax = plt.subplots()
    virus_lengths = [x/scale for x in virus_lengths]
    other_lengths = [x/scale for x in other_lengths]

    n, x, _ = ax.hist(virus_lengths, bins=np.linspace(0, maxlen, 40), 
                               histtype=u'step', color='r', linewidth=4, alpha=0.6)  
    n, x, _ = ax.hist(other_lengths, bins=np.linspace(0, maxlen, 40), 
                               histtype=u'step', color='g', linewidth=4, alpha=0.6)  
    if virus == "covid":
        ax.legend([f'COVID {basetype}', f'{other} {basetype}'])
    else:
        ax.legend([f'lambda phage {basetype}', f'{other} {basetype}'])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_yticks([])
    fig.savefig(f'../img/read_lengths_{basetype}_0.png')
