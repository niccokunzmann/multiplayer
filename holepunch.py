import socket
import time

class HolePunchMechanism:

    retry_time = 0.1
    
    def __init__(self, from_address, address_family = socket.AF_INET):
        self.socket = socket.socket(address_family, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(from_address)
        self.punched_to = set()
        self.punch_required = set()
        self.port = self.socket.getsockname()[1]

    @property
    def punch_succeeded(self):
        return self.punched_to & self.punch_required

    @property
    def punch_failed(self):
        return self.punch_required - self.punched_to

    def punch_to(self, address):
        if isinstance(address, str):
            address = url_to_address(string)
        self.punch_required.add(address)

    def schedule(self):
        for address in self.punch_required:
            self.socket.sendto(b'', address)
        while select.select([self.socket], [], [], 0)
            data, addr = self.socket.recvfrom(0)
            self.punched_to.add(addr)

    def schedule_for(self, seconds):
        for i in range(int(seconds / self.retry_time)):
            self.schedule()
            time.sleep(self.retry_time)

__all__ = ['HolePunchMechanism']
