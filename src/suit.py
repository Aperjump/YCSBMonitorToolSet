import sys
sys.path.append("..")
import subprocess
import config
import os
import re
import json
import matplotlib.pyplot as plt
from drawnow import drawnow


class Test_suit(object):

    def __init__(self, test_name, breaktime, memory, threadnum, runtime):
        """
        :param test_name: give name to output files
        :param breaktime: when to kill memcache
        :param memory: memory size for memcache
        :param threadnum: thread number for YCSB
        :param runtime: run how many time and take average
        """
        self.test_name = test_name
        self.memcache_test_file = config.DATA_PATH + "/modified_memcache_" + test_name
        self.origin_mem_test_file = config.DATA_PATH + "/origin_memcache_" + test_name
        if os.path.exists(self.memcache_test_file):
            os.remove(self.memcache_test_file)
        if os.path.exists(self.origin_mem_test_file):
            os.remove(self.origin_mem_test_file)
        self.breakpoint = breaktime
        self.runtime = runtime
        self.memcache_command = config.MEMCACHE_DIR + "/memcached" + " -p " + str(config.MEMCACHE_PORT) + " -m " + str(memory) + " -vv"
        self.YCSB_command1 = "bin/ycsb run jdbc -P workloads/workloadb -P db.properties -s -threads " + str(threadnum) + " -p use_cache=true"
        self.origin_memcache_command = config.ORIGIN_MEMCACHE_DIR + "/memcached" + " -p " + str(config.ORIGIN_MEMCACHE_PORT) + " -m " + str(memory) + " -vv"
        self.YCSB_command2 = "bin/ycsb run jdbc -P workloads/workloadb -P db.properties2 -s -threads " + str(threadnum) + " -p use_cache=true"
        os.chdir(config.YCSB_DIR)
        self.memcache_records = []
        self.origin_memcahce_records = []

    def runmemcache(self):
        """
        run modified memcache
        :return:
        """
        for i in range(self.runtime):
            if os.path.exists(config.BDB_DIR):
                subprocess.run(["rm", "-rf", config.BDB_DIR])
            print("#######ROUND " + str(i) + "#######")
            self.memcache_process = subprocess.Popen(self.memcache_command, encoding='utf-8', shell=True,stderr = subprocess.DEVNULL,
                                            env={"LD_LIBRARY_PATH": "/usr/local/BerkeleyDB.18.1/lib"})
            self.YCSB_process = subprocess.Popen(self.YCSB_command1, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, encoding='utf-8', shell=True,
                                            preexec_fn=os.setsid)
            while self.YCSB_process.poll() is None:
                errs = self.YCSB_process.stderr.readline().strip()
                cur_list = errs.split()
                if len(cur_list) == 45:
                    data_dict = self.parseycsboutput(cur_list, 0, i)
                    self.memcache_records.append(data_dict)
                    print(errs)
                    if (data_dict["time"] >= self.breakpoint):
                        break
            self.memcache_process.kill()
            self.YCSB_process.kill()
            tmp_output = subprocess.run("lsof -i:" + str(config.MEMCACHE_PORT), shell = True,
                                        capture_output= True, encoding = 'utf-8')
            portprocess_num = re.search(".*memcached (\d+).*", tmp_output.stdout).group(1)
            subprocess.run("kill -9 " + portprocess_num, shell = True)
            print("#######Killing Process#######")
            self.memcache_process = subprocess.Popen(self.memcache_command, encoding='utf-8', shell=True, stderr=subprocess.DEVNULL,
                                            env={"LD_LIBRARY_PATH": "/usr/local/BerkeleyDB.18.1/lib"})
            self.YCSB_process = subprocess.Popen(self.YCSB_command1, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, encoding='utf-8', shell=True,
                                            preexec_fn=os.setsid)
            while self.YCSB_process.poll() is None:
                errs = self.YCSB_process.stderr.readline().strip()
                cur_list = errs.split()
                if len(cur_list) == 45:
                    data_dict = self.parseycsboutput(cur_list, self.breakpoint, i)
                    self.memcache_records.append(data_dict)
                    print(errs)
            self.memcache_process.kill()
            self.YCSB_process.kill()
            tmp_output = subprocess.run("lsof -i:" + str(config.MEMCACHE_PORT), shell = True,
                                        capture_output= True, encoding = 'utf-8')
            portprocess_num = re.search(".*memcached (\d+).*", tmp_output.stdout).group(1)
            subprocess.run("kill -9 " + portprocess_num, shell = True)
            with open(self.memcache_test_file + "_" + str(i) + ".json", 'a') as f:
                f.write(json.dumps(self.memcache_records))

    def runorigin_memcache(self):
        """
        run original memcache
        :return:
        """
        for i in range(self.runtime):
            print("#######ROUND " + str(i) + "#######")
            self.memcache_process = subprocess.Popen(self.origin_memcache_command, encoding='utf-8', stderr = subprocess.DEVNULL,
                    shell=True)
            self.YCSB_process = subprocess.Popen(self.YCSB_command2, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, encoding='utf-8', shell=True,
                                            preexec_fn=os.setsid)
            while self.YCSB_process.poll() is None:
                errs = self.YCSB_process.stderr.readline().strip()
                cur_list = errs.split()
                if len(cur_list) == 45:
                    data_dict = self.parseycsboutput(cur_list, 0, i)
                    self.origin_memcahce_records.append(data_dict)
                    print(errs)
                    if (data_dict["time"] >= self.breakpoint):
                        break
            self.memcache_process.kill()
            self.YCSB_process.kill()
            # find listening process
            tmp_output = subprocess.run("lsof -i:" + str(config.ORIGIN_MEMCACHE_PORT), shell = True,
                                        capture_output= True, encoding = 'utf-8')
            portprocess_num = re.search(".*memcached (\d+).*", tmp_output.stdout).group(1)
            subprocess.run("kill -9 " + portprocess_num, shell = True)
            print("#######Killing Process#######")
            self.memcache_process = subprocess.Popen(self.origin_memcache_command, encoding='utf-8', stderr = subprocess.DEVNULL,shell=True)
            self.YCSB_process = subprocess.Popen(self.YCSB_command2, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, encoding='utf-8', shell=True,
                                            preexec_fn=os.setsid)
            while self.YCSB_process.poll() is None:
                errs = self.YCSB_process.stderr.readline().strip()
                cur_list = errs.split()
                if len(cur_list) == 45:
                    data_dict = self.parseycsboutput(cur_list, self.breakpoint, i)
                    self.origin_memcahce_records.append(data_dict)
                    print(errs)
            self.memcache_process.kill()
            self.YCSB_process.kill()
            # find listening process
            tmp_output = subprocess.run("lsof -i:" + str(config.ORIGIN_MEMCACHE_PORT), shell = True,
                                        capture_output= True, encoding = 'utf-8')
            portprocess_num = re.search(".*memcached (\d+).*", tmp_output.stdout).group(1)
            subprocess.run("kill -9 " + portprocess_num, shell = True)
            with open(self.orfigin_mem_test_file + "_" + str(i) + ".json", 'a') as f:
                f.write(json.dumps(self.origin_memcahce_records))

    def parseycsboutput(self, cur_list, offset, round):
        """

        :param cur_list: list(input)
        :param offset: restart memcache we need to calculate time again
        :param round: id of running time
        :return:
        """
        new_data = {
            'round' : round,
            'time' : int(cur_list[2]) + offset,
            'tot_op': int(cur_list[4]),
            'op/sec':float(cur_list[6]),
            'readcount' : int(cur_list[10].split("=")[1][:-1]),
            'readavg': float(cur_list[13].split("=")[1][:-1]),
            'readfcount': int(cur_list[37].split("=")[1][:-1]),
            'readfavg': float(cur_list[40].split("=")[1][:-1]),
            'updatef_count': int(cur_list[19].split("=")[1][:-1]),
            'updatef_avg': float(cur_list[22].split("=")[1][:-1]),
            'update_count':  int(cur_list[28].split("=")[1][:-1]),
            'update_avg': float(cur_list[31].split("=")[1][:-1])
        }
        return new_data

if __name__ == "__main__":
    cur_test = Test_suit("10thread100m", 120, 100, 10, 5)
    cur_test.runmemcache()
    cur_test.runorigin_memcache()
