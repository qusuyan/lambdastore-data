#! /bin/env python3

''' Plots per-application latencies for a specific number of shards '''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager

from pandas import read_csv, concat
from seaborn import lineplot, FacetGrid

FONT_PATH = '../LinLibertine_Rah.ttf'
fontManager.addfont(FONT_PATH)

# The number of shards we want to display latencies for
NUM_SHARDS = 4

# Set the font properties
prop = FontProperties(fname=FONT_PATH)

plt.rcParams.update({'lines.markersize': 8, 'font.size': 15,
                     'font.family':prop.get_name()})

workloads = {
    "microblog": "Retwis",
    "forum": "CloudForum",
    #"filesystem": "CloudFS"
}
worker_types = {
    "lambdastore": "LambdaStore",
    "ol-wasm": "OpenLambda (WASM)",
}
col_order = [val for (_,val) in workloads.items()]

data = []

for name in workloads:
    df = read_csv(f'../sharding/{name}.csv', header=0,
                  comment="#", skipinitialspace=True)
    if 'workload' not in df:
        df["workload"] = name
    data.append(df)

df = concat(data)

df = df[(df["num-shards"] == NUM_SHARDS)]
df['throughput'] = df['throughput'] / 1000.0

for (key, name) in workloads.items():
    df["workload"] = np.where((df["workload"] == key), name, df["workload"])

for (key, name) in worker_types.items():
    df["worker-type"] = np.where((df["worker-type"] == key),
                                 name, df["worker-type"])

df.rename(columns={"workload": "Workload"}, inplace=True)

hue_kws={"color":["tab:blue", "tab:red"], "marker":['o', 'X']}

g = FacetGrid(df, col="Workload", hue="worker-type",
              height=3, aspect=len(workloads)*0.5,
              sharex=False, sharey=False, legend_out=True, hue_kws=hue_kws,
              col_order=col_order)
g.map(lineplot, "throughput", "latency-mean")

g.set_titles(col_template="{col_name}")
#g.set_xlabels("Throughput (tsd. transactions/s)")
g.set_xlabels("Throughput (ktps)")
g.set_ylabels("Latency\n(ms, mean)")
g.set(ylim=(0,None))

g.add_legend(loc='lower center', ncols=2, bbox_to_anchor=(0.3, -0.1),
             title="")
g.savefig('output.pdf', bbox_inches='tight')
