#! /bin/env python3

# pylint: disable=line-too-long,missing-docstring

import numpy as np
import matplotlib.pyplot as plt

from pandas import read_csv
from seaborn import lineplot, FacetGrid
from matplotlib.font_manager import FontProperties, fontManager

font_path = '../LinLibertine_Rah.ttf'
fontManager.addfont(font_path)

# Set the font properties
prop = FontProperties(fname=font_path)
plt.rcParams.update({'font.size': 18, 'lines.markersize': 8, 'font.family':prop.get_name()})

df = read_csv('results.csv', header=0, skipinitialspace=True, comment='#')
df["workload"] = ""

df["workload"] = np.where((df["write-chance"] == 50), "50% read, 50% write", df["workload"])
df["workload"] = np.where((df["write-chance"] == 0), "read only", df["workload"])

df = df.groupby(["workload", "guard-creation-chance"])['throughput'].max().reset_index()
df['throughput'] = df['throughput'] / 1000.0

df.rename(columns={"workload": "Workload"}, inplace=True)

linestyle = {"marker": "o"}
g = FacetGrid(df, col="Workload", height=3, aspect=1.5, sharex=True, sharey=False, hue_kws=linestyle)
g.map(lineplot, "guard-creation-chance", "throughput")

g.set_titles(col_template="{col_name}")
g.set_xlabels("Guard Creation Chance\n(% of writes)")
g.set_ylabels("Throughput\n(tsd. transactions/s)")
g.set(ylim=(0,None))

g.tight_layout()
g.savefig('output.eps')
