import sys
sys.path.append("..")
import subprocess
import config
import os
import re
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
from drawnow import drawnow

port = 11213
mem = 10
BDB_DIR = config.BDB_DIR
memcache_command = config.MEMCACHE_DIR + "/memcached" + " -p " + str(port) + " -m " + str(mem) + " -vv"
YCSB_command = "bin/ycsb run jdbc -P workloads/workloadb -P db.properties -s -threads 2 -p use_cache=true"

def meta_graph_wrapper(plot_new):
    time_seq = []
    observe_seq = []
    plt.ion()
    plt.show()
    def plot_func(next_time, next_obs):
        time_seq.append(next_time)
        observe_seq.append(next_obs)
        #print(str(next_time) + " " + str(next_obs))
        plot_new(time_seq, observe_seq)
    return plot_func

@meta_graph_wrapper
def plot_new(x, y):
    plt.plot(x, y, '-r')
    plt.draw()

def hyper_metric(section, field):
    def meta_metric(func):
        time_pattern = re.compile(".*?(\d+)\ssec.*")
        if section == "META":
            if field == "ops/sec":
                pattern = re.compile(".*?(\d+)\scurrent\sops/sec.*")
            else:
                pattern = re.compile(".*?(\d+)\s" + field + ".*")
        elif section in ["READ", "UPDATE", "READ-FAILED", "UPDATE_FAILED"]:
            pattern = re.compile(".*?\[" + section + ".*?" + field + "=(\d+).*")
        def func_inner(flag):
            func(time_pattern, pattern, flag)
        return func_inner
    return meta_metric

@hyper_metric(section = "READ-FAILED", field = "Count")
def getresponse(time_part, search_pattern, flag):
    while YCSB_process.poll() is None:
        # out = child.stdout.readline()
        errs = YCSB_process.stderr.readline().strip()
        cur_list = errs.split()
        plt.show()
        if len(cur_list) == 45:
            cur_time = int(re.search(time_part, errs).group(1))
            obsv = float(re.search(search_pattern, errs).group(1))
            if flag == 0:
                plot_new(cur_time, obsv)
                if int(cur_time) >= 60:
                    #plt.axvline(60, color = 'g')
                    break
            else:
                plot_new(60 + cur_time, obsv)
            print(errs)

if __name__ == "__main__":
    if os.path.exists(BDB_DIR):
        subprocess.run(["rm", "-rf", BDB_DIR])
    os.chdir(config.YCSB_DIR)
    memcache_process = subprocess.Popen(memcache_command, encoding='utf-8', shell=True, stderr=subprocess.DEVNULL,
                                        env={"LD_LIBRARY_PATH": "/usr/local/BerkeleyDB.18.1/lib"})
    YCSB_process = subprocess.Popen(YCSB_command, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, encoding='utf-8', shell=True,
                                    preexec_fn=os.setsid)
    getresponse(0)
    memcache_process.kill()
    YCSB_process.kill()
    print("#######Killing Process#######")
    memcache_process = subprocess.Popen(memcache_command, encoding='utf-8', shell=True, stderr=subprocess.DEVNULL,
                                        env={"LD_LIBRARY_PATH": "/usr/local/BerkeleyDB.18.1/lib"})
    YCSB_process = subprocess.Popen(YCSB_command, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, encoding='utf-8', shell=True,
                                    preexec_fn=os.setsid)
    getresponse(1)
    memcache_process.kill()
    YCSB_process.kill()
    