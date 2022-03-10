# Adapted from linuxhint.com/send_receive_udp_python
import socket
import sys
import baseServerRequest
import time

if len(sys.argv) == 3:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    print(ip)
    print(port)
else:
    print("Error: use: python3 serverBase.py <arg1: server IP/this machine's IP> <arg2: server port>")
    exit(1)

sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = (ip,port)
sok.bind(server_addr)
print("Ctrl+c to exit... ")

print("Listening on: ", ip, "port: ", port)
receivedCounter = 0

try:
    while True:
        data, address = sok.recvfrom(4096)
        dataResponse = baseServerRequest.getResponse(data)
        time.sleep(0.002)
        receivedCounter+=1
        sok.sendto(dataResponse.encode('utf-8'), address)
except KeyboardInterrupt:
    print("Done.")
    print("Received: ", receivedCounter)
    exit(0)
