import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 11})
fig, ax = plt.subplots()
# systems = ['Guppy\nJetson', 'Guppy-lite\nJetson', 'Guppy\nTitan', 'Guppy-lite\nTitan', 'SquiggleFilter']
systems = ['Guppy', 'Guppy-lite', ' Guppy', ' Guppy-lite', 'SquiggleFilter']

titan_thru_hac = 387
titan_thru_fast = 1524
compute_ratio_hac = 480941/222959
compute_ratio_fast = 109888/39656
print(compute_ratio_hac, compute_ratio_fast)
colors = ['C3', 'C1', 'C3', 'C1', 'C2']
throughputs = [
        titan_thru_hac/compute_ratio_hac,
        titan_thru_fast/compute_ratio_fast,
        titan_thru_hac,
        titan_thru_fast,
        15318
        ]

ax.bar(systems, throughputs, color=colors)
# 512 pores * 4000 signals/sec / 2000 signals decision
ax.axhline(y=1024, color='gray', linestyle='--')
ax.axhline(y=1024*5, color='k', linestyle='--')
ax.legend(['MinION output specification', 'GridION output specification'])
ax.set_ylabel('Throughput (reads/second)')


ax.text(0.5, 10000, "Jetson Xavier", ha='center')
ax.text(0.5, 9000, r"$350mm^2$", ha='center')
ax.text(0.5, 8000, "30W", ha='center')

ax.text(2.5, 10000, "Titan XP", ha='center')
ax.text(2.5, 9000, r"$471mm^2$", ha='center')
ax.text(2.5, 8000, "250W", ha='center')

ax.text(4, 10000, "PathFinder", ha='center')
ax.text(4, 9000, r"$1.67mm^2$", ha='center')
ax.text(4, 8000, "0.936W", ha='center')
plt.tight_layout()

fig.savefig('../img/throughput.png')
