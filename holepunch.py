import socket
import time
import select
from .stun import *
from .server import *
from .ConnectionFactory import url_to_address

import threading

BUFF = 4096

class HolePunchConnector:

    servers_to_try = 5
    unresolved_server_list = server_list
    retry_time = 0.1

    @classmethod
    def from_address(cls, address = ('', 0), address_family = socket.AF_INET):
        sock = socket.socket(address_family, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(address)
        return cls.from_socket(sock)

    @classmethod
    def from_socket(cls, socket):
        return cls(socket)
    
    def __init__(self, socket):
        self.socket = socket
        self._index = 0
        self.internet_addresses = set()
        self.port = self.socket.getsockname()[1]
        self.punched_to = set()
        self.punch_required = set()
        self.stun_server_list = []        
        self.start_address_resolution_thread()

    def start_address_resolution_thread(self):
        family = self.socket.family
        type = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
        self.name_resolver_thread = threading.Thread(target = self.resolve_addresses,
            args = (self.unresolved_server_list, self.stun_server_list, family, type))
        self.name_resolver_thread.deamon = True
        self.name_resolver_thread.start()

    @staticmethod
    def resolve_addresses(from_list, to_list, family, type):
        for host, port in from_list[:]:
            try:
                addresses = socket.getaddrinfo(host, port, family, type)
            except socket.gaierror:
                # socket.gaierror: [Errno 11004] getaddrinfo failed
                continue
            for address_info in addresses:
                to_list.append(address_info[-1])


    @property
    def stun_server_addresses_to_try(self):
        for i in range(min((self.servers_to_try, len(self.stun_server_list)))):
            self._index %= len(self.stun_server_list)
            yield self.stun_server_list[self._index]
            self._index += 1

    @property
    def punch_succeeded(self):
        return self.punched_to & self.punch_required

    @property
    def punch_failed(self):
        return self.punch_required - self.punched_to

    def punch_to(self, address):
        if isinstance(address, str):
            address = url_to_address(address)
        self.punch_required.add(address)

    def schedule_for(self, seconds):
        for i in range(int(seconds / self.retry_time)):
            self.schedule()
            time.sleep(self.retry_time)

    def schedule(self):
        for server_address in self.stun_server_addresses_to_try:
            try:
                self.socket.sendto(GenReq(), server_address)
            except socket.gaierror:
                # socket.gaierror: [Errno 11004] getaddrinfo failed
                # we are not connected to the internet
                pass 
        for address in self.punch_required:
            self.socket.sendto(b'', address)
        while select.select([self.socket], [], [], 0)[0]:
            try:
                resp, addr = self.socket.recvfrom(BUFF)
            except ConnectionResetError:
                continue
            if resp:
                if resp[:1] == COMMANDS['is_there_a_server']:
                    self.socket.sendto(COMMANDS['there_is_a_server'], addr)
                else:
                    try:
                        taddr = GetTAddressByResponse(resp)
                    except IndexError:
                        pass
                    else:
                        if taddr:
                            self.internet_addresses.add(taddr)
            self.punched_to.add(addr)

    def schedule_for(self, seconds):
        for i in range(int(seconds / self.retry_time)):
            self.schedule()
            time.sleep(self.retry_time)

__all__ = ['HolePunchConnector']
