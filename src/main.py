import sys
sys.path.append("..")
import subprocess
import config

child = subprocess.Popen(["python3", "fileworkload.py", "-r", "0.1"], stdout = subprocess.PIPE,
                         stderr = subprocess.PIPE, encoding= 'utf-8')
while child.poll() is None:
    out = child.stdout.readline().strip()
    print(out)