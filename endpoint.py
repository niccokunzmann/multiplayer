"""endpoints are used to send commands to servers"""

from .server import *
from socket import AF_INET

class UDPEndpoint:
    

    def __init__(self, server_address, client_address = ('', 0), \
                 address_family = AF_INET):
        self.server = Server(client_address, ClientRequestHandler, \
                             address_family = address_family)
        self.server.timeout = 0
        self.socket = self.server.socket
        self.server_address = server_address
        self.values = self.server.values

    def send_to_server(self, bytes):
        self.socket.sendto(bytes,  self.server_address)

    def close(self):
        self.server.server_close()

    def schedule(self):
        self.server.handle_pending_requests()


__all__ = ['UDPEndpoint']
