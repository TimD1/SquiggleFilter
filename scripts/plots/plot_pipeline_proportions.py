import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 14})

fig, axes = plt.subplots(1,2)
tools = ['Basecalling', 'Alignment', 'Variant Calling']
covid_prop100 = [87.72, 2.75, 9.53]
covid_prop1000 = [95.95, 3.01, 1.04]
colors = ["#1a4099", "#ebc100", "#9c9c9c"]
labels0 = [f'{tool} ({pct}%)' for tool, pct in zip(tools, covid_prop100)]
labels1 = [f'{tool} ({pct}%)' for tool, pct in zip(tools, covid_prop1000)]

patches0, _ = axes[0].pie(covid_prop100, startangle=90, colors=colors)
patches1, _ = axes[1].pie(covid_prop1000, startangle=90, colors=colors)
axes[0].legend(patches0, labels0, loc=(0,-0.3))
axes[1].legend(patches1, labels1, loc=(0,-0.3))
plt.tight_layout()
fig.savefig('../img/pipeline.png')
