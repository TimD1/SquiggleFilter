import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 20})
fig, ax = plt.subplots()

tools = ['Guppy', 'Guppy\nLite', 'Squiggle\nFilter']
colors = ['C3', 'C1', 'C2']
latencies = [ 1.304, 0.149, (107_000) / (2.5 * 10**9) ]

ax.bar(tools, latencies, color=colors)

base_lines = [1, 10, 100, 500]
base_latencies = [.0025, .025, .25, 1.25]
for latency, base in zip(base_latencies, base_lines):
    plt.hlines(y=latency, xmin=-0.5, xmax=1.5, color='k', linestyle=':', linewidth=3)
    label = " 1 base" if base == 1 else f' {base} bases'
    plt.text(1.5, latency, label, ha='left', va='center')
    
ax.set_ylabel('Latency (s)')
ax.set_yscale('log')
plt.tight_layout()
fig.savefig('../../img/latency.png', dpi=300)
