
import asyncio
from logging import error, warning, info, debug

import array
import struct

class PilotClient:
    def __init__(self, receive_cb=None):
        self.receive_cb = receive_cb
        self.send_port = 5501
        self.recv_port = 5502
        self.pilot_host = 'localhost'
        asyncio.async(self.start())

    def connection_made(self, transport):
        debug('Pilot connection made')
        self.transport = transport

    def datagram_received(self, data, addr):
        debug('Pilot received data.')
        vals = array.array('H', data)
        if self.receive_cb:
            self.receive_cb(vals)

    def __call__(self):
        debug('self.__call__()')
        return self

    @asyncio.coroutine
    def start(self):
        loop = asyncio.get_event_loop()
        transport, protocol = yield from loop.create_datagram_endpoint(self, local_addr=('127.0.0.1', self.recv_port))

    def send(self, data):
        self.transport.sendto(data, (self.pilot_host, self.send_port))

