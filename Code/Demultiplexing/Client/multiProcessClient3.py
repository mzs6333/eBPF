# Adapated from linuxhint.com/send_receive_udp_python/
import socket
import sys
import random
import time

if len(sys.argv) == 4:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    testLen = int(sys.argv[3])
else:
    print("Error: python3 multiProcessClient3.py <arg1 server IP> \
        <arg2 server Port Number> <arg3 test runtime>")
    exit(1)

pktCounter = 0
sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
print("Ctrl+c to exit...")

startTime = time.time()
while(time.time() - startTime < testLen):
    randData = random.randint(100000, 10000000)
    sendData = str(randData)
    sok.sendto(sendData.encode('utf-8'), (ip,port))
    pktCounter+=1
    data, address = sok.recvfrom(4096)

f = open("data3.txt", "a")
writeString = "\nPackets Sent: " + str(pktCounter) + "\n"
f.write(writeString)
f.close()
sok.close()
