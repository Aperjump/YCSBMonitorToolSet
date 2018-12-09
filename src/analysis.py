import json
from typing import List, Any

import pandas as pd
import matplotlib.pyplot as plt

def plot_feature_prop(feature):
    plt.plot(mavgmemcache.index, mavgmemcache[feature] / mavgmemcache["op/sec"], label='modified memcache')
    plt.plot(oavgmemcache.index, oavgmemcache[feature] / oavgmemcache["op/sec"], label='original memcache')
    plt.legend()
    plt.axvline(x = 120, color = "red", linestyle = "dashed")
    plt.title(feature + "/operation per second comparison")
    plt.show()
def plot_feature(feature):
    plt.plot(mavgmemcache.index, mavgmemcache[feature], label='modified memcache')
    plt.plot(oavgmemcache.index, oavgmemcache[feature], label='original memcache')
    plt.legend()
    plt.axvline(x = 120, color  = "red", linestyle = "dashed")
    plot_top = plt.twiny()

    top_stick = [120]
    top_label = ["restart"]
    plot_top.set_xticks(top_stick)
    plot_top.set_xticklabels(top_label)
    plt.title(feature + " comparison")
    plt.show()
mfile_name = "/home/aperjump/Work/YCSBMonitorToolSet/data/modified_memcache_10thread100m_"
ofile_name = "/home/aperjump/Work/YCSBMonitorToolSet/data/origin_memcache_10thread100m_"
mmemcache = []
omemcache = []
for i in range(3):
    cur_data = pd.read_json(mfile_name + str(i) +".json")
    mmemcache.append(cur_data)
for i in range(3):
    cur_data2 = pd.read_json(ofile_name + str(i) + ".json")
    omemcache.append(cur_data2)
mmemcache = pd.concat(mmemcache)
omemcache = pd.concat(omemcache)
mmemcache = mmemcache[mmemcache["round"] != 2]
mavgmemcache = mmemcache.groupby(['time']).mean()
oavgmemcache = omemcache.groupby(['time']).mean()


plot_feature("readfcount")
plot_feature_prop("readfcount")