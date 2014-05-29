from .server import *
import socket
import time
from .endpoint import *
from .client import *
from urllib.parse import urlparse
import socket
from stun import *

class UDPClientFactory:

    def __init__(self, address, information, client_address = ('', 0), address_family = socket.AF_INET):
        self.address = address
        self.address_family = address_family
        self.information = information
        self.client_address = client_address

    def __repr__(self):
        return '<UDP server at {}:{}>'.format(self.address[0], self.address[1])

    # official interface
    
    def get_information(self):
        return self.information

    def get_endpoint(self):
        return UDPEndpoint(self.address, client_address = self.client_address, \
                           address_family = self.address_family)

    def get_simple_description(self):
        return 'udp://{}:{}'.format(self.address[0], self.address[1])


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
        

LANDiscoverer = UDPBroadcastDiscoverer

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

class URLEndpointFactory:

    def __init__(self, string):
        self.host, self.port = url_to_address(string)

    def get_information(self):
        return None

    def get_endpoint(self):
        return UDPEndpoint((self.host, self.port))    

    def get_simple_description(self):
        return 'udp://{}:{}'.format(self.host, self.port)

def url_to_address(string):
    url = urlparse(string)
    port = url.port or SERVER_PORT
    host = url.hostname or url.path
    return host, port

def address_to_url(address):
    return 'udp://{}:{}'.format(address[0], address[1])
        
class ServerEndpointFactory:
    """ create a server and an endpoint for the server"""

    new_server = staticmethod(create_server)

    def __init__(self):
        self.server = self.new_server()
        self.host = socket.gethostname()
        self.port = self.server.server_address[1]

    def get_information(self):
        return None

    def get_endpoint(self):
        return UDPEndpoint((self.host, self.port))    

    def get_simple_description(self):
        s = 'local: udp://{}:{}'.format(self.host, self.port)
        for internet_address in self.internet_addresses:
            s += '\n internet: udp://{}:{}'.format(internet_address[0], internet_address[1])

__all__ = ['ServerEndpointFactory', 'URLEndpointFactory',
           'ConnectionFactory', 'UDPBroadcastDiscoverer',
           'UDPClientFactory', 'address_to_url', 'url_to_address']
