# Adapated from linuxhint.com/send_receive_udp_python/
import socket
import sys
import random
import time

if len(sys.argv) == 3:
    ip = sys.argv[1]
    port = int(sys.argv[2])
else:
    print("Error: python3 cacheClient.py <arg1 server IP> <arg2 server Port Number>")
    exit(1)

sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
print("Ctrl+c to exit...")

alphabet = ['p', 'g', 'c', 'd', 'e', 'f', 'b', 'h']
receivedCounter = 0
sentCounter = 0

sentDict = {}
sentDict['p'] = 0
sentDict['g'] = 0
sentDict['c'] = 0
sentDict['d'] = 0
sentDict['e'] = 0
sentDict['f'] = 0
sentDict['b'] = 0
sentDict['h'] = 0

TEST_RUNTIME = 30
SERVER_CACHE_SIZE = 4
startTime = time.time()

while (time.time() - startTime < TEST_RUNTIME):
    data = 0
    sendData = alphabet[random.randint(0,3)]
    sentDict[sendData] += 1
    sok.sendto(sendData.encode('utf-8'), (ip,port))
    sentCounter+=1
    data, address = sok.recvfrom(4096)
    if data != 0:
        receivedCounter+=1

f = open("data.txt", "a")
stringToWrite = "\nReceived a total of: " + str(receivedCounter) + " packets, and sent: " + str(sentCounter)
secondStringToWrite = "\nStats: p: " + str(sentDict['p']) + "\t g: " + str(sentDict['g']) + "\t c: " + str(sentDict['c']) + "\t d: " + str(sentDict['d']) + "\t e: " + str(sentDict['e']) + "\t f: " + str(sentDict['f'])
f.write(stringToWrite)
f.write(secondStringToWrite)
f.close()
sok.close()
