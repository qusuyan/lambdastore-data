#! /bin/env python3

'''
Plots how object creation scales with the number of shards
'''

import pandas as pd
import matplotlib.pyplot as plt

import seaborn
from seaborn import lineplot

from matplotlib.font_manager import FontProperties, fontManager

FONT_PATH = '../LinLibertine_Rah.ttf'
fontManager.addfont(FONT_PATH)

# Set the font properties
prop = FontProperties(fname=FONT_PATH)

plt.rcParams.update({'font.size': 16, 'lines.markersize': 8,
                     'font.family':prop.get_name()})

df = pd.read_csv('results.csv', header=0, comment='#', skipinitialspace=True)
df = df.groupby(["num-shards"])['throughput'].max().reset_index()
df['throughput'] = df['throughput'] / 1000.0

fig = plt.figure(figsize=(6,2))
axes = fig.add_subplot(1, 1, 1)

lineplot(data=df, x="num-shards", y="throughput", ax=axes,
         color="tab:blue", marker='o')

axes.set_ylabel('Throughput\n(tsd. new objects/s)')
axes.set_xlabel('Number of Shards')
axes.tick_params(axis="both", colors="black")

axes.set_ylim(bottom=0)
axes.set_xticks(df["num-shards"].unique())

seaborn.despine(ax=axes)

fig.savefig('output.pdf', bbox_inches='tight')
