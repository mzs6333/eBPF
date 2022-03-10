# Matthew Sickler 2022

from bcc import BPF
from ctypes import *
import time;

class cache_response(Structure):
    _fields_=[("accessedSinceUpdate",c_int), ("responsePayload",c_char)]

device = "enp0s3"
b = BPF(src_file="udp_cache.c")
fn = b.load_func("udp_cache", BPF.XDP)
b.attach_xdp(device, fn, 0)

cache = b.get_table("cache")

# cacheResponseOne = cache_response()
# cacheResponseOne.accessedSinceUpdate = c_int(0)
# cacheResponseOne.responsePayload = c_char(b'y')

# cacheResponseTwo = cache_response()
# cacheResponseTwo.accessedSinceUpdate = c_int(0)
# cacheResponseTwo.responsePayload = c_char(b'n')

# cacheResponseThree = cache_response()
# cacheResponseThree.accessedSinceUpdate = c_int(0)
# cacheResponseThree.responsePayload = c_char(b'A')

# cacheResponseFour = cache_response()
# cacheResponseFour.accessedSinceUpdate = c_int(0)
# cacheResponseFour.responsePayload = c_char(b'A')

# cacheResponseFive = cache_response()
# cacheResponseFive.accessedSinceUpdate = c_int(0)
# cacheResponseFive.responsePayload = c_char(b'A')

# cacheResponseSix = cache_response()
# cacheResponseSix.accessedSinceUpdate = c_int(0)
# cacheResponseSix.responsePayload = c_char(b'A')

cacheSize = cache_response()
cacheSize.accessedSinceUpdate = c_int(0)

cacheAdd = cache_response()
cacheAdd.accessedSinceUpdate = c_int(0)
cacheAdd.responsePayload = c_char(b'p')

# b["cache"][c_char(b'g')] = cacheResponseOne
# b["cache"][c_char(b'p')] = cacheResponseTwo
# b["cache"][c_char(b'c')] = cacheResponseThree
# b["cache"][c_char(b'd')] = cacheResponseFour
# b["cache"][c_char(b'e')] = cacheResponseFive
# b["cache"][c_char(b'f')] = cacheResponseSix
# b["cache"][c_char(b'\0')] = cacheSize
# b["cache"][c_char(b'\n')] = cacheAdd

def cacheMissed():
    if b["cache"][c_char(b'\0')].responsePayload == b'm':
        return True
    return False

def resetCache():
    print("Resetting The Cache -> Flushing!")
    print("Established Cache: \n")   
    for key,value in b["cache"].items():
        print(key.value, ':\t', value.accessedSinceUpdate, ',\t', value.responsePayload)
    # b["cache"][c_char(b'g')] = cacheResponseOne
    # b["cache"][c_char(b'p')] = cacheResponseTwo
    b["cache"][c_char(b'\0')] = cacheSize
    b["cache"][c_char(b'\n')] = cacheAdd
    print("Established Cache After Resets: \n")   
    for key,value in b["cache"].items():
        print(key.value, ':\t', value.accessedSinceUpdate, ',\t', value.responsePayload)

    print("Flushing Cache: \n")
    for key,value in b["cache"].items():
        if key.value != b'\x00' and key.value != b'\n' and key.value != b'g' and key.value != b'p':
            print("Deleting entry: ", key.value)
            del b["cache"][key]

    print("Established Cache After Deletes: \n")   
    for key,value in b["cache"].items():
        print(key.value, ':\t', value.accessedSinceUpdate, ',\t', value.responsePayload)


def addedToCache():
    if b["cache"][c_char(b'\0')].responsePayload == b'p':
        print("Found something to add")
        # print("Established Cache: \n")
        # for key,value in b["cache"].items():
        #     print(key, ':\t', value.accessedSinceUpdate, ',\t', value.responsePayload)
        reset = cache_response()
        reset.responsePayload = c_char(b'\0')
        reset.accessedSinceUpdate = b["cache"][c_char(b'\0')].accessedSinceUpdate
        b["cache"][c_char(b'\0')] = reset
        return True
    return False

def addToCache():
    newRequest = b["cache"][c_char(b'\n')].responsePayload
    newEntry = cache_response()
    newEntry.accessedSinceUpdate = c_int(1)
    newEntry.responsePayload = c_char(b'A')
    b["cache"][c_char(newRequest)] = newEntry
    b["cache"][c_char(b'\n')] = cacheAdd
    # print("Established Cache: \n")
    # for key,value in b["cache"].items():
    #     print(key, ':\t', value.accessedSinceUpdate, ',\t', value.responsePayload)

# This function could be hooked up to a file that can log the outgoing responses to queries, etc.
# Currently it just flips some responses and updates the hits.
def updateCache():
    # if cacheMissed():
    #     resetCache()
    
    if addedToCache():
        addToCache()

TEST_RUNTIME = 35

try:
    b.trace_print()
    # startTime = time.time()
    # time.sleep(TEST_RUNTIME)
    # while(time.time() - startTime < TEST_RUNTIME):
        # updateCache()
        
        
except KeyboardInterrupt:
    # dist = b.get_table("counter")
    # # for k, v in dist.items():
    # #     print("DEST_PORT : %10d, COUNT : %10d" % (k.value, v.value))
    # print("Removing BPF...")
    # f = open("data.txt", "a")
    # f.write("\nCache State:\n")
    # for key,value in b["cache"].items():
    #     f.write(key.value, ':\t', value.accessedSinceUpdate, ',\t', value.responsePayload)
    # f.write("\nPackets Received Total: ")
    # for k, v in dist.items():
    #     f.write("DEST_PORT : %10d, COUNT : %10d" % (k.value, v.value))
    quit()

dist = b.get_table("counter")
print("Removing BPF...")
f = open("data.txt", "a")
f.write("\nCache State:\n")
for key,value in b["cache"].items():
    stringToWrite = str(key.value) + ':\t' + str(value.accessedSinceUpdate) + ',\t' + str(value.responsePayload)
    f.write(stringToWrite)
f.write("\nPackets Received Total: ")
for k, v in dist.items():
    stringToWrite = "PACKETS RECEIVED:" + str(v.value)
    f.write(stringToWrite)

f.close()
b.remove_xdp(device, 0) 