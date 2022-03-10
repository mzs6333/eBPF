# Adapted from https://dev.to/satrobit/absolute-beginner-s-guide-to-bcc-xdp-and-ebpf-47oi

from bcc import BPF #1
from bcc.utils import printb
import time

device = "enp0s3" #2
b = BPF(src_file="udp_counter.c") #3
fn = b.load_func("udp_counter", BPF.XDP) #4
b.attach_xdp(device, fn, 0) #5

try:
    start = time.time()
    while(time.time()-start < 25):
        continue
except KeyboardInterrupt: #7
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    dist = b.get_table("counter") #8
    for k, v in dist.items(): #9
        print("DEST_PORT : %10d, COUNT : %10d" % (k.value, v.value)) #10

dist = b.get_table("counter")
f = open("data.txt", "a")
for k, v in dist.items():
    stringToWrite = "Port:" + str(k.value) + "Count:" + str(v.value)
    f.write(stringToWrite)

f.close()

b.remove_xdp(device, 0) #11
