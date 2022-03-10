import os
import time

cmd = "sudo python3 cacheLoader.py"

NUMBER_OF_TESTS = 5

startTime = time.time()
try:
    for test in range(NUMBER_OF_TESTS):
        print("Running new test")
        f = open("data.txt", "a")
        testNumberString = "\n\n" + str(test) + "\n"
        f.write(testNumberString)
        f.close()
        os.system(cmd)
except KeyboardInterrupt:  
    quit()
