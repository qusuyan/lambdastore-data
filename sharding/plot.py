#! /bin/env python3

''' Plots application scalability as the number of shards increases '''

import matplotlib.pyplot as plt

import numpy as np
from pandas import read_csv, concat

from seaborn import lineplot, FacetGrid

from matplotlib.font_manager import FontProperties, fontManager

FONT_PATH = '../LinLibertine_Rah.ttf'
fontManager.addfont(FONT_PATH)

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
    df = read_csv(f'{name}.csv', header=0, comment="#", skipinitialspace=True)
    if 'workload' not in df:
        df["workload"] = name
    data.append(df)

df = concat(data)

df = df.groupby(["workload", "worker-type", "num-shards"])['throughput'].max().reset_index()
df['throughput'] = df['throughput'] / 1000.0

for (key, name) in workloads.items():
    df["workload"] = np.where((df["workload"] == key), name, df["workload"])

for (key, name) in worker_types.items():
    df["worker-type"] = np.where((df["worker-type"] == key), name, df["worker-type"])

df.rename(columns={"workload": "Workload"}, inplace=True)

linestyle = {"color": ["tab:blue", "tab:red", "tab:orange", "tab:green"],
             "marker": ["o", "X", "^", "v"]}
g = FacetGrid(df, col="Workload", height=3, aspect=len(workloads)*0.5,
              sharex=True, sharey=False,
              hue="worker-type", legend_out=True, hue_kws=linestyle,
              col_order=col_order)
g.map(lineplot, "num-shards", "throughput")

g.set_titles(col_template="{col_name}")
g.set_ylabels('Throughput (ktps)')
g.set_xlabels('Replica Sets')
g.set(xticks=df["num-shards"].unique())
g.tick_params(axis="both", colors="black")
g.set(ylim=(0,None))

g.add_legend(loc='lower center', ncol=len(worker_types),
             bbox_to_anchor=(0.3, -0.1),#-0.2),
             title="")

g.tight_layout()
g.savefig('output.pdf')
