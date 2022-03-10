def getResponse(data):
    if data == b'a':
        return 'aReceived'
    elif data == b'b':
        return 'bReceived'
    elif data == b'c':
        return 'cReceived'
    else:
        return 'otherReceived'