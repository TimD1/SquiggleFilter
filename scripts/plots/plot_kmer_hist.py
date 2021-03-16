import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt

with open('../data/kmer_model.txt') as kmers:
    currents = []
    for line in kmers:
        kmer, current = line.split()
        currents.append(float(current))

    plt.hist(currents, bins=100, facecolor='b', alpha=0.6)
    plt.xlabel('expected current level (pA)')
    plt.ylabel('k-mer counts')
    plt.title('k-mer current model distribution')
    plt.savefig('../img/kmer_range.png')
