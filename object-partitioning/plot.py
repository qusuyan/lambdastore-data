#! /bin/env python3

'''
Plots how object partitioning affects read/write performance
'''

import numpy as np
import matplotlib.pyplot as plt

from pandas import read_csv
from seaborn import lineplot, FacetGrid
from matplotlib.font_manager import FontProperties, fontManager

FONT_PATH = '../LinLibertine_Rah.ttf'
fontManager.addfont(FONT_PATH)

# Set the font properties
prop = FontProperties(fname=FONT_PATH)
plt.rcParams.update({'font.size': 18, 'lines.markersize': 8,
                     'font.family':prop.get_name()})

labels = ["Read Only", "50% Read, 50% Write"]#, "Write Only"]

df = read_csv('results.csv', header=0, skipinitialspace=True, comment='#')

#Remove write only (for now)
df = df[(df["write-chance"] == 0) | (df["write-chance"] == 50)]

df["workload"] = ""
for (pos, share) in enumerate([0,50]): #,100]):
    df["workload"] = np.where((df["write-chance"] == share), labels[pos], df["workload"])

df = df.groupby(["workload", "num-guards"])['throughput'].max().reset_index()
df['throughput'] = df['throughput'] / 1000.0

hue_kws={"color":["tab:blue"], "marker":['o']}

linestyle = {"marker": "o"}

g = FacetGrid(df, col="workload", height=3, aspect=1.2,
              sharex=True, sharey=False, hue_kws=hue_kws, col_order=labels)
g.map(lineplot, "num-guards", "throughput", markersize=10)

g.set_titles(col_template="{col_name}")
g.set_xlabels("Number of Guards")
g.set_ylabels("Throughput (ktps)")
g.set(xscale='log')
g.set(xticks=df["num-guards"].unique())

for (pos, label) in enumerate(labels):
    max_val = np.max(df[(df["workload"] == label)]["throughput"])
    g.axes[0][pos].set_ylim((0,max_val*1.1))

plt.savefig('output.pdf', bbox_inches='tight')
