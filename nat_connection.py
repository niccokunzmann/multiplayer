"""

Idea from
    https://github.com/samyk/pwnat
    http://samy.pl/pwnat/pwnat.pdf

"""

from socket import AF_INET

class NatConnector:

    def __init__(self, address, address_family = AF_INET):
        self.address = address
        self.address_family = address_family

    def get_nat_addresses(self):
        return set()

    def get_incoming_connections(self):
        return set()

    def schedule(self):
        pass
