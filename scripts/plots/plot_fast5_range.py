import h5py
import numpy as np
import re
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt


file_name = "/home/timdunn/datasets/lambdaphage/FAL11227_8bb4695a85a5e3a621c58f18f47290ee50a12ebc_0.fast5"
fast5_file = h5py.File(file_name, 'r')                  

# get signal from single-FAST5 file                                      
all_signals = []
for read_name in fast5_file:
    signal = np.array(fast5_file[read_name]['Raw']['Signal'][:], dtype=np.int32)
    signal += int(fast5_file[read_name]['channel_id'].attrs['offset'])
    all_signals.extend(signal)

plt.hist(all_signals, bins=100, range=[0,1000], facecolor='g', alpha=0.6)
plt.xlabel('ADC Value')
plt.ylabel('Counts')
plt.savefig('../img/signal_range.png')
