# Matthew Sickler 2022

from bcc import BPF
from bcc.utils import printb
import time
import threading
import socket
from ctypes import *

class data_response(Structure):
    _fields_=[("value", c_int), ("port", c_int)]

modifyPort1Entry = data_response()
modifyPort1Entry.value = c_int(1000000)
modifyPort1Entry.port = c_int(0)

modifyPort2Entry = data_response()
modifyPort2Entry.value = c_int(1000000)
modifyPort2Entry.port = c_int(0)

modifyPort3Entry = data_response()
modifyPort3Entry.value = c_int(1000000)
modifyPort3Entry.port = c_int(0)

modifyPort4Entry = data_response()
modifyPort4Entry.value = c_int(1000000)
modifyPort4Entry.port = c_int(0)

NUM_QUEUES = 4

device = "enp0s3" #2
b = BPF(src_file="udp_demultiplex.c") #3
fn = b.load_func("udp_demultiplex", BPF.XDP) #4
b.attach_xdp(device, fn, 0) #5

queue1 = b.get_table("queue1")
queue2 = b.get_table("queue2")
queue3 = b.get_table("queue3")
queue4 = b.get_table("queue4")

b["modify"][c_int(1)] = modifyPort1Entry
b["modify"][c_int(2)] = modifyPort2Entry
b["modify"][c_int(3)] = modifyPort3Entry
b["modify"][c_int(4)] = modifyPort4Entry

ip = "10.0.2.5"
port = 51145

def peekQueue(qToPeek):
    try:
        if qToPeek == 1:
            queue1.peek()
            return True
        elif qToPeek == 2:
            queue2.peek()
            return True
        elif qToPeek == 3:
            queue3.peek()
            return True
        else:
            queue4.peek()
            return True
    except KeyError:
        return False

def getResult(qtype, dataResponse, address):
    if qtype == 1:
        time.sleep(.04)
        dataResponse = str(int(dataResponse))
        sok.sendto(dataResponse.encode('utf-8'), address)
    elif qtype == 2:
        time.sleep(.02)
        dataResponse = str(int(dataResponse))
        sok.sendto(dataResponse.encode('utf-8'), address)
    elif qtype == 3:
        time.sleep(0.004)
        dataResponse = str(int(dataResponse))
        sok.sendto(dataResponse.encode('utf-8'), address)
    else:
        time.sleep(.009)
        dataResponse = str(int(dataResponse))
        sok.sendto(dataResponse.encode('utf-8'), address)

def performQueue():
    dataResponse = data_response()
    for queue in range(NUM_QUEUES):
        if queue+1 == 1 and peekQueue(queue+1):
            dataResponse = queue1.pop()
        elif queue+1 == 2 and peekQueue(queue+1):
            dataResponse = queue2.pop()
        elif queue+1 == 3 and peekQueue(queue+1):
            dataResponse = queue3.pop()
        elif queue+1 == 4 and peekQueue(queue+1):
            dataResponse = queue4.pop()
        else:
            continue
        
        intDataResponse = int(dataResponse.value)
        sendIP = "10.0.2.4"
        sendPort = int(dataResponse.port)
        address = (sendIP,sendPort)
        newThread = threading.Thread(target=getResult, args=((queue+1),intDataResponse,address))
        newThread.start()

try:
    sok = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (ip,port)
    sok.bind(server_addr)
    startTime = time.time()
    while(True):
        performQueue()

except KeyboardInterrupt:
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    dist = b.get_table("counter")
    for k, v in dist.items():
        print("DEST_PORT : %10d, COUNT : %10d" % (k.value, v.value))

dist = b.get_table("counter")
f = open("data.txt", "a")
for k, v in dist.items():
    stringToWrite = "\nPort:" + str(k.value) + "Count:" + str(v.value)
    f.write(stringToWrite)

f.close()
b.remove_xdp(device, 0)
