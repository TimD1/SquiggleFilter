import matplotlib as mpl
mpl.use('agg')
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
    ax.text(size, height+0.2, name, {'color': "red" if na == "DNA" else "blue"}, ha="center", va="center")
    ax.plot(size, height, color="red" if na == "DNA" else "blue", markersize=10, marker="+" if strands=="ds" else ".")

virus_genomes = [
    ["Coxsackie", 7200, "RNA", "ss", 0.5],
    ["Polio", 7500, "RNA", "ss", 1],
    ["Borna Disease", 8900, "RNA", "ss", 1.5],
    ["HIV", 9800, "RNA", "ss", 2],
    ["Zika Fever", 10000, "RNA", "ss", 2.5],
    ["Yellow Fever", 11000, "RNA", "ss", 3],
    ["Dengue", 11000, "RNA", "ss", 3.5],
    ["West Nile", 11500, "RNA", "ss", 4],
    ["Influenza A", 13500, "RNA", "ss", 0.5],
    ["Influenza B", 14500, "RNA", "ss", 1.0],
    ["Mumps", 15400, "RNA", "ss", 1.5],
    ["Measles", 15900, "RNA", "ss", 2.0],
    ["Ebola", 19000, "RNA", "ss", 2.5],
    ["Reovirus", 29200, "RNA", "ds", 0.5],
    ["SARS", 29700, "RNA", "ss", 1.0],
    ["Coronavirus", 29900, "RNA", "ss", 1.5],
    ["Herpes Simplex", 152000, "DNA", "ds", 0.5],
    ["Smallpox", 186000, "DNA", "ds", 1],
]

fig, ax = plt.subplots(figsize=(10,4))
ax.set_ylim(0, 5)
ax.set_yticks([])
for v in virus_genomes:
    add_datapoint(ax, v)
plt.axvline(x=50000, color='black', linestyle="--")
ax.set_xscale('log')
# ax.set_xlim(0, 250000)
ax.set_xticks([10000, 50000, 80000])
ax.set_xticklabels([10000,50000,100000])
ax.set_xlabel("Genome length (bases)")
ax.add_patch(Rectangle((67000 - 100, 3.6), 140000, 1.3, fill=None, alpha=1))

ax.plot(70000, 4.6, color="blue", marker=".")
ax.text(73000, 4.6, "single stranded RNA", color="blue", va="center")
ax.plot(70000, 4.2, color="blue", marker="+")
ax.text(73000, 4.2, "double stranded RNA", color="blue", va="center")
ax.plot(70000, 3.8, color="red", marker="+")
ax.text(73000, 3.8, "double stranded DNA", color="red", va="center")
# adjust_text(texts, only_move={'points':'y', 'texts':'y'}, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
plt.tight_layout()
plt.savefig('../img/genome_sizes.png')
