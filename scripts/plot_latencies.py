import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

fig, ax = plt.subplots()                                                     

batch_sizes = [1, 10, 50, 100, 250, 300, 400, 512]
fast_max_latency = [28.34, 59.01, 80.45, 87.85, 122.06, 148.12, 196.87, 263.76]
fast_avg_latency = [28.34, 51.37, 68.24, 72.28, 87.63, 98.89, 117.6, 154.64]
hac_max_latency = [327.34, 792.75, 1346.19, 1437.64, 1746.21, 1809.07, 1983.35, 2051.68]
hac_avg_latency = [327.34, 705.74, 1211.62, 1248.14, 1510.44, 1543.21, 1679.6, 1735.13]
sqf_max_latency = [0.06528, 0.6528, 3.264, 6.528, 16.32, 19.58, 26.11, 33.42]
sqf_avg_latency = [0.01728, 0.0864, 0.432, 0.864, 2.160, 2.592, 3.456, 4.423]

ax.plot(batch_sizes, [x/1000 for x in fast_max_latency], color='C1', marker='o', alpha=0.5) 
ax.plot(batch_sizes, [x/1000 for x in fast_avg_latency], color='C1', marker='.', alpha=0.5) 
ax.plot(batch_sizes, [x/1000 for x in hac_max_latency], color='C3', marker='o', alpha=0.5) 
ax.plot(batch_sizes, [x/1000 for x in hac_avg_latency], color='C3', marker='.', alpha=0.5) 
ax.plot(batch_sizes, [x/1000 for x in sqf_max_latency], color='C2', marker='o', alpha=0.5) 
ax.plot(batch_sizes, [x/1000 for x in sqf_avg_latency], color='C2', marker='.', alpha=0.5) 
# ax.plot(batch_sizes, basic_runtimes, color='k', linestyle='--' )

ax.set_xlabel(f'Batch Size (reads, length 2000 signals)')                          
ax.set_ylabel(f'Latency (seconds)')                          
ax.set_yscale('log')
lines = [Line2D([0],[0], color='C3', marker='o'),
        Line2D([0],[0], color='C1', marker='o'),
        Line2D([0],[0], color='C2', marker='o'),
        Line2D([0],[0], color='k', marker='o'),
        Line2D([0],[0], color='k', marker='.')]
labels = [f'High-Acc Guppy', f'Fast Guppy', 'SquiggleFilter', 'maximum latency', 'average latency']
ax.legend(lines, labels)
fig.savefig(f'../img/latency.png')                     
