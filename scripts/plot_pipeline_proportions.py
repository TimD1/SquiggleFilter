import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 14})

fig, axes = plt.subplots(1,2)
tools = ['Guppy-lite', 'Minimap2', 'RaCon', 'Medaka']
covid_times100 = np.array([287.487, 9.013, 0.948, 30.266])
covid_times1000 = np.array([2874.87, 90.13, 0.948, 30.266])
explode0 = (0, 0.9, 0.5, 0.1)
explode1 = (0, 0.6, 0.35, 0.1)

axes[0].pie(covid_times100, startangle=90, autopct="%.2f%%", explode=explode0)
axes[1].pie(covid_times1000, startangle=90, autopct="%.2f%%", explode=explode1)
axes[0].legend(tools, loc=(1.04,0))
plt.tight_layout()
fig.savefig('../img/pipeline.png')
