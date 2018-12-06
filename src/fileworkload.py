import sys
sys.path.append("..")
import config
import argparse
import random
import time

DATA_FILE = config.PROJECT_DIR + "/data/test.dat"

def write2file(num):
    fd = open(DATA_FILE, "w")
    for i in range(num):
        tmp_num = random.randint(0, num)
        fd.write(str(tmp_num) + "\n")
    print("finish write file")
    fd.close()

def readfromfile(num):
    fd = open(DATA_FILE, "r")
    for line in fd.readlines():
        print(line.strip())
        time.sleep(num)
    fd.close()

def main():
    parser = argparse.ArgumentParser(description="two functions: generate test data or start a process, read every element from the file",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--gen", "-g", nargs = "?", type = int, help="generated file size")
    parser.add_argument("--runinterval", "-r", nargs = '?', type = float, help="run subprocess time interval")
    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))

    if (args.gen):
        write2file(args.gen)
    elif (args.runinterval):
        readfromfile(args.runinterval)
    else:
        print("invalid argument")

main()