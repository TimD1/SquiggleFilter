import pandas as pd
import datetime, csv
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

df = pd.read_csv('../../data/owid-covid-data.csv', header=None)
df[1] = df[1].diff()

ax = df.plot(color="#6eaaef", figsize=(4.5,2), zorder=1)
ax.set_yticks([100_000, 500_000, 1_000_000, 2_000_000])
ax.set_yticklabels(["100,000", "500,000", "1 million", "2 million"])
ax.set_ylim(0, 2_500_000)

ax.set_xticks([0, 196, 366])
ax.set_xticklabels(["Jan 1 2020", "July 15", "Jan 1 2021"])
ax.legend().remove()

# plt.hlines(y=100_000, linestyle=":", xmin=0, xmax=83, color="#ebc100")
# plt.hlines(y=1_000_000, linestyle=":", xmin=0, xmax=196, color="#ebc100")
# plt.vlines(x=83, linestyle=":", ymin=0, ymax=100_000, color="#ebc100")
# plt.vlines(x=196, linestyle=":", ymin=0, ymax=1_000_000, color="#ebc100")

plt.vlines(x=13, linestyle="--", ymin=0, ymax=2_500_000, color="k")
plt.text(14, 1_400_000, 'SARS-CoV-2\nSequenced')

plt.arrow(14, 200_000, 181, 0, fc='k', ec='k', zorder=2)
plt.plot(18, 200_000, marker='<', color='k')
plt.plot(189, 200_000, marker='>', color='k')
plt.text(23, 260_000, 'Insufficient Testing')

plt.vlines(x=196, linestyle='--', ymin=0, ymax=2_500_000, color='k')
plt.text(197, 1_400_000, '1 Million\nDaily Tests')

lines = [Line2D([0], [0], color="#6eaaef", lw=3)]
ax.legend(lines, ["Daily US COVID-19 Tests"], loc='upper right')
# plt.vlines(x=22, linestyle="-", ymin=0, ymax=2_500_000, color="#e82828")
# plt.text(24,1050000, "Initial Primers Released", color="#e82828",rotation=90, horizontalalignment="left", verticalalignment="bottom")

# plt.vlines(x=84, linestyle="-", ymin=0, ymax=2_500_000, color="#e82828")
# plt.text(86,1050000, "Final Primers Released", color="#e82828",rotation=90, horizontalalignment="left", verticalalignment="bottom")



plt.tight_layout()
plt.savefig("../../img/covid_tests.png", dpi=300)
