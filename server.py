
# in remove client
# in propose
# out update
# in get

from socketserver import UDPServer, DatagramRequestHandler
import struct
from io import BytesIO
import time
import socket
import json

COMMANDS = {b'a' : 'add_client',
            b'r' : 'remove_client',
            b'p' : 'propose_element',
            b'u' : 'update_element',
            b'g' : 'get_element',
            b'i' : 'is_there_a_server',
            b't' : 'there_is_a_server'}

for key, command_name in list(COMMANDS.items()):
    COMMANDS[command_name] = key

SERVER_PORT = 6028

def number2bytes(number):
    return struct.pack('>l', number)

LENGTH_OF_NUMBER = len(number2bytes(0))

def read_number(file):
    return struct.unpack('>l', file.read(LENGTH_OF_NUMBER))[0]

class Server(UDPServer):
    # max_packet_size according to
    # http://stackoverflow.com/questions/1098897/what-is-the-largest-safe-udp-packet-size-on-the-internet
    max_packet_size = 65507
    information = {}

    def __init__(self,  server_address, RequestHandlerClass, address_family = socket.AF_INET):
        self.address_family = address_family
        UDPServer.__init__(self, server_address, RequestHandlerClass)
        self.values = {}
        self.clients = set()
        def handle_timeout():
            self.__handle_timeout()
            self._has_pending_requests = False
        self.__handle_timeout = self.handle_timeout
        self.handle_timeout = handle_timeout

    def handle_pending_requests(self):
        self._has_pending_requests = True
        while self._has_pending_requests:
            self.handle_request()

    def server_discovered(self, address, bytes):
        pass
        

class CommandRequestHandler(DatagramRequestHandler):
    
    def handle(self):
        self.clients.add(self.client_address)
        while True:
            command = self.rfile.read(1)
            if not command: break
            name = 'cmd_' + COMMANDS[command]
            method =  getattr(self, name)
            method()

    def write_command(self, name):
        self.wfile.write(COMMANDS[name])

    def write_number(self, number):
        self.wfile.write(number2bytes(number))

    def read_number(self):
        return read_number(self.rfile)

    def write_bytes(self, bytes):
        self.wfile.write(bytes)

    def read_bytes(self):
        return self.rfile.read()

    def reply(self):
        self.socket.sendto(self.wfile.getvalue(), self.client_address)
        self.wfile = BytesIO()

    def finish(self):
        pass

    @property
    def values(self):
        return self.server.values

    @property
    def clients(self):
        return self.server.clients

class ServerRequestHandler(CommandRequestHandler):

    def cmd_propose_element(self):
        """propose an element"""
        number = len(self.values)
        element = self.read_bytes()
        self.values[number] = element
        self.write_update_command(number)
        bytes = self.wfile.getvalue()
        for client in self.clients:
            self.socket.sendto(bytes, client)

    def cmd_get_element(self):
        """reply with the right element"""
        number = read_number(self.rfile)
        if number not in self.values:
            return 
        self.write_update_command(number)
        self.reply()

    def write_update_command(self, number):
        value = self.values[number]
        self.write_command('update_element')
        self.write_number(number)
        self.write_bytes(value)

    def cmd_is_there_a_server(self):
        self.write_command('there_is_a_server')
        self.write_bytes(json.dumps(self.server.information).encode('UTF-8'))
        self.reply()
        
class ClientRequestHandler(CommandRequestHandler):
    
    def cmd_update_element(self):
        """update an element"""
        number = self.read_number()
        bytes = self.read_bytes()
        self.server.values[number] = bytes

class DiscoveryRequestHandler(CommandRequestHandler):

    def cmd_there_is_a_server(self):
        information = json.loads(self.read_bytes().decode('UTF-8'))
        self.server.server_discovered(self.client_address, information)

def create_server(HandlerClass = ServerRequestHandler,
         ServerClass = Server, port=SERVER_PORT):
    import threading
    server_address = ('', port)
    server = ServerClass(server_address, ServerRequestHandler)
    t = threading.Thread(target = server.serve_forever)
    t.deamon = True
    t.start()
    return server
    

def main(HandlerClass = ServerRequestHandler,
         ServerClass = Server, port=SERVER_PORT):
    import sys
    
    server_address = ('', port)

    serverd = ServerClass(server_address, HandlerClass)

    sa = serverd.socket.getsockname()
    print("Serving on", sa[0], "port", sa[1], "...")
    try:
        serverd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        serverd.server_close()
        sys.exit(0)

if __name__ == '__main__':
    main()
