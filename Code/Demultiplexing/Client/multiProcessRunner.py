# Adapted from Martin Konecy on stackoverflow

from subprocess import Popen

commands = ['python3 multiProcessClient4.py 10.0.2.5 51141 30']

print("Starting Tests Now...")

TESTS_TO_RUN = 15

for test in range(TESTS_TO_RUN):
    processes = [ Popen(i, shell=True) for i in commands ]
    for process in processes:
        process.wait()
