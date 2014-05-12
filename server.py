
# in remove client
# in propose
# out update
# in get

from socketserver import UDPServer, DatagramRequestHandler
import struct
from io import BytesIO

COMMANDS = {b'a' : 'add_client',
            b'r' : 'remove_client',
            b'p' : 'propose_element',
            b'u' : 'update_element',
            b'g' : 'get_element'}

for key, command_name in list(COMMANDS.items()):
    COMMANDS[command_name] = key

def number2bytes(number):
    return struct.pack('>l', number)

LENGTH_OF_NUMBER = len(number2bytes(0))

def read_number(file):
    return struct.unpack('>l', file.read(LENGTH_OF_NUMBER))[0]

class Server(UDPServer):
    # max_packet_size according to
    # http://stackoverflow.com/questions/1098897/what-is-the-largest-safe-udp-packet-size-on-the-internet
    max_packet_size = 65507

    def __init__(self,  server_address, RequestHandlerClass):
        UDPServer.__init__(self, server_address, RequestHandlerClass)
        self.values = {}
        self.clients = set()

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

    def received_bytes(self, bytes):
        pass

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
        
class ClientRequestHandler(CommandRequestHandler):
    
    def cmd_update_element(self):
        """update an element"""
        number = self.read_number()
        bytes = self.read_bytes()
        self.server.values[number] = bytes
        self.server.received_bytes(number)


def main(HandlerClass = ServerRequestHandler,
         ServerClass = Server, port=6028):
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
