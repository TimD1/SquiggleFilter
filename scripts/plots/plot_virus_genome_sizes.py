import matplotlib as mpl
import numpy as np
# mpl.use('agg')
mpl.rcParams.update({'font.size': 17})
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

def add_datapoint(ax, data):
    name = data[0]
    size = data[1]
    na = data[2]
    strands = data[3]
    height = data[4]
    ax.text(size, height+0.2, name, {'color': "#ebc100" if na == "DNA" else "#1a4099"}, ha="left", va="center")
    ax.plot(size, height, color="#ebc100" if na == "DNA" else "#1a4099", markersize=12, marker="P" if strands=="ds" else ".")

virus_genomes = [
    ["Coxsackie", 7200, "RNA", "ss", 0.7],
    ["Polio", 7500, "RNA", "ss", 1.4],
    ["HIV", 9800, "RNA", "ss", 2.1],
    ["Zika", 10000, "RNA", "ss", 2.8],
    ["Dengue", 11000, "RNA", "ss", 3.5],
    ["Yellow Fever", 11000, "RNA", "ss", 4.2],
    ["Borna Disease", 8900, "RNA", "ss", 4.9],
    ["West Nile", 11500, "RNA", "ss", 5.6],
    ["Influenza A", 13500, "RNA", "ss", 0.7],
    ["Influenza B", 14500, "RNA", "ss", 1.4],
    ["Mumps", 15400, "RNA", "ss", 2.1],
    ["Measles", 15900, "RNA", "ss", 2.8],
    ["Ebola", 19000, "RNA", "ss", 3.5],
    ["Reovirus", 29200, "RNA", "ds", 0.7],
    ["SARS", 29700, "RNA", "ss", 1.4],
    ["Coronavirus", 29900, "RNA", "ss", 2.1],
    ["Herpes Simplex", 152000, "DNA", "ds", 0.7],
    ["Smallpox", 186000, "DNA", "ds", 1.4],
]

fig, ax = plt.subplots(figsize=(10,4))
ax.set_ylim(0, 6.5)
ax.set_yticks([])
for v in virus_genomes:
    add_datapoint(ax, v)
ax.set_xscale('log')
ax.set_xlim(5000, 500000)
ax.set_xticks([5_000, 10_000, 50_000, 100_000, 250_000])
ax.set_xticklabels(["5,000","10,000","50,000","100,000", "250,000"])
ax.set_xlabel("Genome length (bases)")

# legend
ax.add_patch(Rectangle((110_000, 4), 375_000, 2.3, fill=None, alpha=1))
ax.plot(120000, 5.8, color="#1a4099", marker=".", markersize=15)
ax.text(130000, 5.8, "single stranded RNA", color="#1a4099", va="center")
ax.plot(120000, 5.1, color="#1a4099", marker="P", markersize=15)
ax.text(130000, 5.1, "double stranded RNA", color="#1a4099", va="center")
ax.plot(120000, 4.4, color="#ebc100", marker="P", markersize=15)
ax.text(130000, 4.4, "double stranded DNA", color="#ebc100", va="center")

# lines
for x in np.arange(0, 6.5, 0.4):
    ax.plot(50_000, x, marker='P', markersize=5, color='k')
    ax.plot(100_000, x, marker='.', markersize=5, color='k')

plt.tight_layout()
plt.savefig('../../img/virus_genomes.png')
