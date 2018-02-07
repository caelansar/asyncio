import socket
import selectors
selector = selectors.DefaultSelector()


class Client:
    def __init__(self):
        self.sock = socket.socket()
        self.resp = b''

    def connect(self):
        self.sock.setblocking(False)
        try:
            print('connecting...')
            self.sock.connect(('www.baidu.com',80))
        except BlockingIOError:
            print('connected')
        selector.register(self.sock, selectors.EVENT_WRITE, self.write)

    def read(self, key, mask):
        chunk = self.sock.recv(1024)
        print('read......')
        if chunk:
            self.resp += chunk
        else:
            selector.unregister(key)
            print(self.resp.decode())
            print('done')
            return


    def write(self, key, mask):
        print('start write')
        selector.unregister(key)
        request = b'GET / HTTP/1.0\r\nHost: www.baidu.com\r\n\r\n'
        self.sock.send(request)
        print('finish write')
        selector.register(key, selectors.EVENT_READ, self.read)

if __name__ == '__main__':
    c = Client()
    c.connect()
    while True:
        try:
            evevt = selector.select()
            for key, mask in evevt:
                callback = key.data
                callback(key.fd, mask)
        except OSError:
            break
