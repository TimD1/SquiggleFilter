import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 20})
fig, ax = plt.subplots(figsize=(15,5))

systems = ['Guppy', 'Guppy\nLite', ' Guppy', ' Guppy\nLite', 'Squiggle\nFilter', ' Squiggle\nFilter']
colors = ['C3', 'C1', 'C3', 'C1', 'C2', 'C2']

titan_thru_hac = 387
titan_thru_fast = 1524
compute_ratio_hac = 480941/222959
compute_ratio_fast = 109888/39656

throughputs = [
        titan_thru_hac/compute_ratio_hac,
        titan_thru_fast/compute_ratio_fast,
        titan_thru_hac,
        titan_thru_fast,
        2.5*10**9 / 107_000,
        5 * 2.5*10**9 / 107_000 ]

ax.bar(systems, throughputs, color=colors)

ax.axhline(y=512*4000/2000, color='k', linestyle='--', linewidth=3)
ax.axhline(y=5*512*4000/2000, color='k', linestyle=':', linewidth=3)
ax.axhline(y=24*3000*4000/2000, color='k', linestyle='-.', linewidth=3)
ax.axhline(y=100*512*4000/2000, color='k', linestyle='-', linewidth=3)
ax.legend(['MinION output', 'GridION output', 'PromethION output', 'Future MinION output'], labelspacing=0.2, loc=(1.04,0.5))

ax.set_ylabel('Throughput (reads/s)')
ax.set_yscale('log')
ax.set_xticklabels(systems)
ax.set_xlim(-0.7, 5.7)


ax.text(0.5, 6000, "Jetson\nXavier\n" + r"$350\mathrm{mm}^2$" + "\n30W", ha='center')
ax.text(2.5, 6000, "Titan\nXP\n" + r"$471\mathrm{mm}^2$" + "\n250W", ha='center')
ax.text(4, 6000, "1-Tile\nASIC\n" + r"$3\mathrm{mm}^2$" + "\n3W", ha='center')
ax.text(5, 6000, "5-Tile\nASIC\n" + r"$13\mathrm{mm}^2$" + "\n14W", ha='center')

plt.tight_layout()
fig.savefig('../../img/throughput.png', dpi=300)
