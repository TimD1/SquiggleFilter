import matplotlib.pyplot as plt

def add_datapoint(ax, data):
    name = data[0]
    size = data[1]
    na = data[2]
    strands = data[3]
    height = data[4]
    ax.text(size*0.98, height, name, {'color': "red" if na == "DNA" else "blue"}, rotation=90)
    ax.plot(size, height-0.25, color="red" if na == "DNA" else "blue", marker="+" if strands=="ds" else ".")

virus_genomes = [
    ["Coxsackie", 7200, "RNA", "ss", 1],
    ["Polio", 7500, "RNA", "ss", 3.5],
    ["Borna Disease", 8900, "RNA", "ss", 1],
    ["HIV", 9800, "RNA", "ss", 1],
    ["Zika Fever", 10000, "RNA", "ss", 2],
    ["Yellow Fever", 11000, "RNA", "ss", 3.5],
    ["Dengue", 11000, "RNA", "ss", 6.5],
    ["West Nile", 11500, "RNA", "ss", 1],
    ["Influenza A", 13500, "RNA", "ss", 1],
    ["Influenza B", 14500, "RNA", "ss", 1],
    ["Mumps", 15400, "RNA", "ss", 1],
    ["Measles", 15900, "RNA", "ss", 3],
    ["Ebola", 19000, "RNA", "ss", 1],
    ["Reovirus", 29200, "RNA", "ds", 1],
    ["SARS", 29700, "RNA", "ss", 3],
    ["Coronavirus", 29900, "RNA", "ss", 4.5],
    ["Herpes Simplex", 152000, "DNA", "ds", 1],
    ["Smallpox", 186000, "DNA", "ds", 1],
]

fig, ax = plt.subplots()
ax.set_ylim(0, 10)
ax.set_yticks([])
for v in virus_genomes:
    add_datapoint(ax, v)
plt.axvline(x=50000, color='black', linestyle="--")
ax.set_xscale('log')
# ax.set_xlim(0, 250000)
ax.set_xticks([10000, 50000, 100000])
ax.set_xlabel("Genome length (in base pairs)")
ax.set_title('Genome size of deadly viruses')

ax.plot(100000, 8.2, color="blue", marker=".")
ax.text(105000, 8, "ssRNA", color="blue")
ax.plot(100000, 7.7, color="blue", marker="+")
ax.text(105000, 7.5, "dsRNA", color="blue")
ax.plot(100000, 7.2, color="red", marker="+")
ax.text(105000, 7, "dsDNA", color="red")

plt.show()
