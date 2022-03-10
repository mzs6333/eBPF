import os
import time

cmd = "sudo python3 cacheClient.py 10.0.2.5 51141"

NUMBER_OF_TESTS = 15

for test in range(NUMBER_OF_TESTS):
    print("Sending Packets Now")
    f = open("data.txt", "a")
    testNumberString = "\n\n" + str(test) + "\n"
    f.write(testNumberString)
    f.close()
    os.system(cmd)
    # time.sleep(10)
