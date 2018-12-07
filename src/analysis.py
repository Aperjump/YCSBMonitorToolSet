import json
import pandas as pd
import matplotlib.pyplot as plt
mmemcache = pd.read_json("/home/aperjump/Work/YCSBMonitorToolSet/data/modified_memcache_10thread100m.json")
omemcache = pd.read_json("/home/aperjump/Work/YCSBMonitorToolSet/data/origin_memcache_10thread100m.json")

mavgmemcache = mmemcache.groupby(['time']).mean()
oavgmemcache = omemcache.groupby(['time']).mean()


plt.plot(mavgmemcache.index, mavgmemcache['op/sec'], label= 'modified memcache')
plt.plot(oavgmemcache.index, oavgmemcache['op/sec'], label = 'original memcache')
plt.legend()
plt.show()
def plot_feature(feature):
    plt.plot(mavgmemcache.index, mavgmemcache[feature], label='modified memcache')
    plt.plot(oavgmemcache.index, oavgmemcache[feature], label='original memcache')
    plt.legend()
    plt.show()