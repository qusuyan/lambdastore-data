#! /bin/env python3

# pylint: disable=missing-docstring,line-too-long

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager

from pandas import read_csv
from seaborn import lineplot, FacetGrid

FONT_PATH = '../LinLibertine_Rah.ttf'
fontManager.addfont(FONT_PATH)

# Set the font properties
prop = FontProperties(fname=FONT_PATH)

workload_labels = ["Read Only", "50% Read, 50% Write", "Write Only"]

plt.rcParams.update({'font.size': 16, 'lines.markersize': 8, 'font.family':prop.get_name()})

df = read_csv('results.csv', header=0, skipinitialspace=True, comment='#')

df["worker-type"] = np.where((df["worker-type"] == "lambdastore"), "LambdaStore", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "ol-sock"), "OpenLambda\n(SOCK)", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "ol-wasm"), "OpenLambda\n(WASM)", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "openwhisk"), "OpenWhisk", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "faasm"), "Faasm", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "apiary"), "Apiary", df["worker-type"])

df = df[((df["write-chance"]==0) | (df["write-chance"]==50) | (df["write-chance"]==100))]

df["workload"] = ""
for (pos, share) in enumerate([0,50,100]):
    df["workload"] = np.where((df["write-chance"] == share), workload_labels[pos], df["workload"])

df.rename(columns={"workload": "Workload"}, inplace=True)
df["throughput"] = df["throughput"] / 1000

hue_order = ["LambdaStore", "OpenLambda\n(WASM)", "OpenLambda\n(SOCK)", "OpenWhisk", "Faasm", "Apiary"]
palette =  {"LambdaStore":"tab:blue", "OpenWhisk":"tab:red", "OpenLambda\n(WASM)":"tab:orange", "OpenLambda\n(SOCK)":"tab:green", "Faasm":"tab:pink", "Apiary":"tab:olive"}
markers= {"LambdaStore":'o', "OpenLambda\n(WASM)":"X", "OpenLambda\n(SOCK)":"s", "OpenWhisk":"^", "Faasm": "v", "Apiary": ">"}

hue_kws={"color":["tab:blue", "tab:green", "tab:orange", "tab:red", "tab:pink", "tab:olive"], "marker":['o', 's', 'X', '^', 'v', '>']}

g = FacetGrid(df, col="Workload", hue="worker-type", height=3, aspect=1.5,
              sharex=False, sharey=False, legend_out=True, hue_order=hue_order,
              hue_kws=hue_kws, col_order=workload_labels)
g.map(lineplot, "throughput", "latency-mean")

g.set_titles(col_template="{col_name}")
g.set_xlabels("Throughput (ktps)")
g.set_ylabels("Latency\n(ms, mean)")

for i, ax in enumerate(g.axes.flat):
        if i == 0:  # For Read Only
            ax.set_ylim(0, 140)
            ax.set_xlim(0, None)
        elif i == 1:  # For 50% Read, 50% Write
            ax.set_ylim(0, 140)
            ax.set_xlim(0, 14)
        elif i == 2:  # For Write Only
            ax.set_ylim(0, 140)
            ax.set_xlim(0, 14)


g.add_legend(loc='lower center', ncol=len(hue_order), bbox_to_anchor=(0.3, -0.2), title="")
g.savefig('output.pdf', bbox_inches='tight')
