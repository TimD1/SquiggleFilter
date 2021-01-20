import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 14})

fig, axes = plt.subplots(1,2)
tools = ['Guppy-lite', 'Minimap2', 'RaCon', 'Medaka']
# covid_times100 = np.array([287.487, 9.013, 0.948, 30.266])
# covid_times1000 = np.array([2874.87, 90.13, 0.948, 30.266])
covid_prop100 = [87.72, 2.75, 0.29, 9.24]
covid_prop1000 = [95.95, 3.01, 0.03, 1.01]
labels0 = [f'{tool} ({pct}%)' for tool, pct in zip(tools, covid_prop100)]
labels1 = [f'{tool} ({pct}%)' for tool, pct in zip(tools, covid_prop1000)]

patches0, _ = axes[0].pie(covid_prop100, startangle=90)
patches1, _ = axes[1].pie(covid_prop1000, startangle=90)
axes[0].legend(patches0, labels0, loc=(0,-0.3))
axes[1].legend(patches1, labels1, loc=(0,-0.3))
plt.tight_layout()
fig.savefig('../img/pipeline.png')
