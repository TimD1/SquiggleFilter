import matplotlib.pyplot as plt
fig, ax = plt.subplots()
systems = ['High-Acc\nJetson Xavier', 'High-Acc\nTitan XP', 'Fast\nJetson Xavier', 'Fast\nTitan XP', 'SquiggleFilter']

titan_thru_hac = 387
titan_thru_fast = 1524
compute_ratio_hac = 480941/222959
compute_ratio_fast = 109888/39656
print(compute_ratio_hac, compute_ratio_fast)
colors = ['C0', 'C5', 'C0', 'C5', 'C2']
throughputs = [
        titan_thru_hac/compute_ratio_hac,
        titan_thru_hac,
        titan_thru_fast/compute_ratio_fast,
        titan_thru_fast,
        15318
        ]

ax.bar(systems, throughputs, color=colors)
# 512 pores * 4000 signals/sec / 2000 signals decision
ax.axhline(y=1024, color='k', linestyle='--')
ax.legend(['worst-case MinION output'])
ax.set_ylabel('Throughput (reads/sec, length 2000 signals)')
plt.tight_layout()
fig.savefig('../img/throughput.png')
