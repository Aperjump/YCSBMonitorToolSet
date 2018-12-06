import sys
sys.path.append("..")
import subprocess
import config
import os
port = 11213
mem = 1000
import re
import matplotlib.pyplot as plt

memcache_command = config.MEMCACHE_DIR + "/memcached" + " -p " + str(port) + " -m " + str(mem) + " -vv"
os.chdir(config.YCSB_DIR)
YCSB_command = "bin/ycsb run jdbc -P workloads/workloadb -P db.properties -s -threads 2 -p use_cache=true"

child1 = subprocess.Popen(memcache_command, encoding= 'utf-8', shell = True, stderr = subprocess.DEVNULL,
                          env = {"LD_LIBRARY_PATH" : "/usr/local/BerkeleyDB.18.1/lib"})
child2 = subprocess.Popen(YCSB_command, stdout = subprocess.PIPE,
                         stderr = subprocess.PIPE, encoding= 'utf-8', shell = True,
                         preexec_fn=os.setsid)
time_seq = []
tot_num_seq = []
opsec_seq = []
plt.ion()

while child2.poll() is None:
    # out = child.stdout.readline()
    errs = child2.stderr.readline().strip()
    cur_list = errs.split()
    #2018-12-05 22:46:03:883 2 sec: 8888 operations;
    # 6239 current ops/sec; [READ: Count=4587, Max=7811, Min=72, Avg=238.17, 90=313, 99=1138, 99.9=4431, 99.99=7811]
    # [UPDATE-FAILED: Count=76, Max=1553, Min=465, Avg=714.63, 90=861, 99=1320, 99.9=1553, 99.99=1553]
    # [UPDATE: Count=218, Max=4379, Min=577, Avg=1276.05, 90=1631, 99=3085, 99.9=4379, 99.99=4379]
    # [READ-FAILED: Count=1349, Max=9015, Min=169, Avg=385.18, 90=519, 99=968, 99.9=5795, 99.99=9015]
    plt.figure(1)
    plt.show()
    if len(cur_list) == 45:
        cur_sec = cur_list[2]
        tot_op = cur_list[4]
        opsec = cur_list[6]
        time_seq.append(int(cur_sec))
        tot_num_seq.append(float(tot_op))
        opsec_seq.append(float(opsec))
        plt.plot(time_seq, opsec_seq, '-r')
        plt.draw()
        readcount = cur_list[10].split("=")[1][:-1]
        readavg = cur_list[13].split("=")[1][:-1]
        readfcount = cur_list[37].split("=")[1][:-1]
        readfavg = cur_list[40].split("=")[1][:-1]
        updatef_count = cur_list[19].split("=")[1][:-1]
        updatef_avg = cur_list[22].split("=")[1][:-1]
        update_count = cur_list[28].split("=")[1][:-1]
        update_avg = cur_list[31].split("=")[1][:-1]
        print("good")
    # print(errs)

child1.kill()