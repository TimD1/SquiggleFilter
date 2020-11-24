import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1,2)
tools = ['Fast Guppy', 'Minimap2', 'RaCon', 'Medaka']
lambda_times = np.array([74.527, 2.446, 0.338, 24.209])
covid_times = np.array([287.487, 9.013, 0.948, 30.266])
def lambda_value(val):
    a  = str(np.round(val/100.*lambda_times.sum(), 1)) + "s"
    return a
def covid_value(val):
    a  = str(np.round(val/100.*covid_times.sum(), 1)) + "s"
    return a
explode = (0, 0.3, 0.2, 0.1)

axes[0].pie(lambda_times, labels=tools, autopct=lambda_value, explode=explode)
axes[1].pie(covid_times, labels=tools, autopct=covid_value, explode=explode)
axes[0].set_title('Lambdaphage-Human DNA')
axes[1].set_title('COVID-Human rtDNA')
plt.tight_layout()
fig.savefig('../img/pipeline.png')
