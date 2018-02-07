import socket
import selectors
selector = selectors.DefaultSelector()


class Future():
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        self.result = result
        print('res', self.result)
        for fn in self._callbacks:
            if fn: fn(self)


class Task():
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            print('done')
            return
        next_future.add_done_callback(self.step)

class Client():
    def __init__(self):
        self.sock = socket.socket()
        self.resp = b''

    def connect(self):
        self.sock.setblocking(False)
        try:
            print('connecting...')
            self.sock.connect(('www.baidu.com', 80))
        except BlockingIOError:
            print('connected')
        f = Future()

        def on_connection():
            f.set_result(None)

        selector.register(self.sock, selectors.EVENT_WRITE, on_connection)
        yield f
        selector.unregister(self.sock)
        self.sock.send(b'GET / HTTP/1.0\r\nHost: www.baidu.com\r\n\r\n')

        while True:
            f = Future()

            def on_read():
                f.set_result(self.sock.recv(1024))

            selector.register(self.sock, selectors.EVENT_READ, on_read)
            chunk = yield f
            selector.unregister(self.sock)
            if chunk:
                self.resp += chunk
            else:
                break

c = Client()
Task(c.connect())
while True:
    try:
        event = selector.select()
        for key, mask in event:
            callback = key.data
            callback()

    except OSError:
        break