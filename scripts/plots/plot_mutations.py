import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({'font.size': 18})

fig, ax = plt.subplots(1, figsize=(8,3))

n_mut = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
f_sub = [0.901, 0.9, 0.902, 0.9, 0.9, 0.902, 0.899, 0.896, 0.891, 0.878, 0.836, 0.662, 0.209, 0.027]
f_ins = [0.901, 0.903, 0.901, 0.901, 0.9, 0.902, 0.9, 0.9, 0.893, 0.883, 0.877, 0.807, 0.604, 0.093]
f_del = [0.901, 0.901, 0.903, 0.9, 0.9, 0.898, 0.9, 0.897, 0.884, 0.867, 0.806, 0.438, 0.031, 0.021]

ax.plot(n_mut, f_sub, linewidth=4, linestyle='-', color='r', alpha=0.5)
ax.plot(n_mut, f_ins, linewidth=4, linestyle='--', color='g', alpha=0.5)
ax.plot(n_mut, f_del, linewidth=4, linestyle=':', color='b', alpha=0.5)
ax.set_ylim(0,1)
ax.set_xscale('log')
ax.set_ylabel('F-score')
ax.set_xlabel('Number of Mutations')
ax.legend(['Substitutions', 'Insertions', 'Deletions'])

plt.tight_layout()
plt.savefig('../../img/mut.png', dpi=300)
