from logging import error, warning, debug, info
import asyncio

class LineClient(object):
    def __init__(self, connect_cb=None, msg_cb=None, disconnect_cb=None):
        self.connect_cb = connect_cb
        self.msg_cb = msg_cb
        self.disconnect_cb = disconnect_cb

        self.writer = None
        self.host = None
        self.port = None

    @asyncio.coroutine
    def connect(self, host, port):
        while True:
            try:
                reader, writer = yield from asyncio.open_connection(host, port)
            except ConnectionRefusedError as e:
                warning(e)
                yield from asyncio.sleep(2)
            else:
                self.reader = reader
                self.writer = writer
                if self.connect_cb:
                    self.connect_cb()
                asyncio.async(self.read())
                break

    @asyncio.coroutine
    def read(self):
        while True:
            try:
                line = yield from self.reader.readline()
            except ConnectionResetError as e:
                warning(e)
                line = None

            if not line:
                if self.disconnect_cb:
                    self.disconnect_cb()
                break
            if self.msg_cb:
                self.msg_cb(line.decode())

    def send(self, line):
        if not line.endswith('\n'):
            line += '\n'
    
        if self.writer is None:
            #warning('Attempt to write without a connection')
            return

        self.writer.write(line.encode())
