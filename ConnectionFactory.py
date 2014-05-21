from server import *
import socket
import time
from endpoint import *
from client import *

class UDPClientFactory:

    def __init__(self, address, address_family, information):
        self.address = address
        self.address_family = address_family
        self.information = information

    def __repr__(self):
        return '<UDP server at {}:{}>'.format(self.address[0], self.address[1])

    # official interface
    
    def get_information(self):
        return self.information

    def get_endpoint(self, client_address = ('', 0)):
        return UDPEndpoint(self.address, client_address = client_address, \
                           address_family = self.address_family)

    def get_client(self):
        return Client(self.get_endpoint())


class UDPBroadcastDiscoverer:

    client_address_udp = ('', 0)
    send_discovery_interval = 0.01

    def create_server(self, address_family):
        server = Server(self.client_address_udp, DiscoveryRequestHandler, address_family = address_family)
        sock = server.socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)    
        server.timeout = 0
        server.server_discovered = lambda address, information: \
            self.server_discovered(address, information, address_family)
        return server
        
    def __init__(self):
        self.ipv4 = self.create_server(socket.AF_INET)
        self.last_discovery_sent = 0
        self.servers = []

    def schedule(self):
        self.ipv4.handle_pending_requests()
        if time.time() > self.last_discovery_sent + self.send_discovery_interval:
            self.send_discovery()

    def send_discovery(self):
        command = COMMANDS['is_there_a_server']
        self.ipv4.socket.sendto(command, ('<broadcast>', SERVER_PORT))
        self.last_packet_sent = time.time()

    def server_discovered(self, address, information, family):
        self.servers.append(UDPClientFactory(address, family, information))

    def new_servers(self):
        servers = self.servers
        self.servers = []
        return servers
        

class ConnectionFactory:

    factories = [UDPBroadcastDiscoverer]

    def __init__(self):
        self.factories = [factory() for factory in self.factories]

    def schedule(self):
        for factory in self.factories:
            factory.schedule()

    def new_servers(self):
        servers = []
        for factory in self.factories:
            servers.extend(factory.new_servers())
        return servers

if __name__ == '__main__':
    import server
    import threading
    t = threading.Thread(target = server.main)
    t.start()
    cf = ConnectionFactory()
    import time
    while 1:
        cf.schedule()
        new_servers = cf.new_servers()
        if new_servers:
            print(new_servers)
        time.sleep(0.01)