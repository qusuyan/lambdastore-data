#! /bin/env python3

# pylint: disable=line-too-long,missing-docstring

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import seaborn
from seaborn import lineplot

from matplotlib.font_manager import FontProperties, fontManager

FONT_PATH = '../LinLibertine_Rah.ttf'
fontManager.addfont(FONT_PATH)

# Set the font properties
prop = FontProperties(fname=FONT_PATH)

plt.rcParams.update({
    'font.size': 20, 'lines.markersize': 8, 'font.family':prop.get_name(),
    'figure.figsize': (7,4)
})

df = pd.read_csv('results.csv', header=0, comment='#', skipinitialspace=True)

df["throughput"] = df["throughput"] * df["operations-per-object"]
df = df.groupby(["operations-per-object", "worker-type"])['throughput'].max().reset_index()

df["worker-type"] = np.where((df["worker-type"] == "lambdastore"), "LambdaStore", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "ol-sock"), "OpenLambda\n(SOCK)", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "ol-wasm"), "OpenLambda\n(WASM)", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "openwhisk"), "OpenWhisk", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "faasm"), "Faasm", df["worker-type"])
df["worker-type"] = np.where((df["worker-type"] == "apiary"), "Apiary", df["worker-type"])

df.rename(columns={"worker-type": "Worker Type"}, inplace=True)

hue_order = ["LambdaStore", "OpenLambda\n(WASM)", "OpenLambda\n(SOCK)", "OpenWhisk", "Faasm", "Apiary"]
palette =  {"LambdaStore":"tab:blue", "OpenWhisk":"tab:red", "OpenLambda\n(WASM)":"tab:orange", "OpenLambda\n(SOCK)":"tab:green", "Faasm":"tab:pink", "Apiary":"tab:olive"}
markers= {"LambdaStore":'o', "OpenLambda\n(WASM)":"X", "OpenLambda\n(SOCK)":"s", "OpenWhisk":"^", "Faasm":'v', "Apiary": ">"}

lineplot(data=df, x="operations-per-object", y="throughput", hue="Worker Type",
         palette=palette, style="Worker Type", markers=markers, dashes=False,
         hue_order=hue_order, linewidth=2.5, markersize=15)

plt.ylabel('Throughput (Hashes/s)')
plt.xlabel('Hashes per Function Call')
plt.xscale('log')
plt.yscale('log')
plt.tick_params(axis="both", colors="black")

seaborn.despine()

plt.legend(frameon=False, title="", loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3)

plt.savefig('output.pdf', bbox_inches='tight')
