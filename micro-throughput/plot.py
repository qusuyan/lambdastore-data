#! /bin/env python3

# pylint: disable=line-too-long,missing-docstring

import numpy as np
import matplotlib.pyplot as plt

import seaborn
from pandas import read_csv
from seaborn import barplot

from matplotlib.font_manager import FontProperties, fontManager

FONT_PATH = '../LinLibertine_Rah.ttf'
fontManager.addfont(FONT_PATH)

# Set the font properties
prop = FontProperties(fname=FONT_PATH)

plt.rcParams.update({'font.size': 15, 'lines.markersize': 8, 'font.family':prop.get_name()})

df = read_csv('results.csv', header=0, skipinitialspace=True, comment='#')
df["workload"] = ""

workload_names = ["0%", "25%", "50%", "75%", "100%"]

df["worker-type"] = np.where((df["worker-type"] == "lambdastore"), "LambdaStore", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "ol-sock"), "OpenLambda\n(SOCK)", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "ol-wasm"), "OpenLambda\n(WASM)", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "openwhisk"), "OpenWhisk", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "faasm"), "Faasm", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "apiary"), "Apiary", df["worker-type"])

for (pos, share) in enumerate([0,25,50,75,100]):
    df["workload"] = np.where((df["write-chance"] == share), workload_names[pos], df["workload"])

df = df.groupby(["workload", "worker-type"])['throughput'].max().reset_index()
df['throughput'] = df['throughput'] / 1000.0

df['reference'] = df.groupby('workload')['throughput'].transform(lambda x: x.iloc[0])
df['normalized-tpt'] = df['throughput'] / df['reference']

df.rename(columns={"worker-type": "Worker Type"}, inplace=True)

num_workloads = len(df["workload"].unique())

fig = plt.figure(figsize=(6, 3))
axes = fig.add_subplot(1, 1, 1)

#barplot(data=df, x="workload", y="normalized-tpt", hue="Worker Type", ax=axes, order=workload_names, palette=["tab:blue", "tab:red", "tab:orange", "tab:green"])

hue_order = ["LambdaStore", "OpenLambda\n(WASM)", "OpenLambda\n(SOCK)", "OpenWhisk", "Faasm", "Apiary"]

barplot(data=df, x="workload", y="throughput", hue="Worker Type", ax=axes, order=workload_names, hue_order=hue_order,
        palette=["tab:blue", "tab:green", "tab:orange", "tab:red", "tab:pink", "tab:olive"])

seaborn.despine()

hatch_patterns = ['/', '\\', '|', '-', '+', 'x']
for idx, bar in enumerate(axes.patches):
    # The factor in set hatch changes the pattern size
    pos = idx // num_workloads

    if pos < len(hue_order):
        pattern = hatch_patterns[pos]
    else:
        # Special case for setting the legend
        pattern = hatch_patterns[idx - num_workloads*len(hue_order)]

    bar.set_hatch(2 * pattern)
    bar.set_edgecolor('black')

axes.legend(frameon=False, bbox_to_anchor=(0.4, 1.2), loc="center", ncol=3)

axes.set_xlabel("Write Chance")
axes.set_ylabel("Throughput (ktps)")
axes.set_yscale('log')

fig.savefig('output.pdf', bbox_inches='tight')
