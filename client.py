from server import Server, ClientRequestHandler, COMMANDS, number2bytes
from threading import Thread
import time

from statistics import ECDF
import queue

from id import *

class Proposal:
    def __init__(self, message_bytes, id, client):
        self.__message_bytes = message_bytes
        self.__id = id
        self.__sent = False
        self.__client = client

    @property
    def id(self):
        return self.__id

    @property
    def bytes(self):
        return self.__message_bytes

    @property
    def is_sent(self):
        return self.__sent

    def send(self):
        if not self.__sent:
            self.__client._propose_to_server(self.__message_bytes, self.id)
            self.__sent = True
        return self

    def __del__(self):
        self.send()


class Client:

    # 0.95 = packet as lost with 95% probability
    packet_was_lost_probability = 0.95

    def __init__(self, server_address, client_address = ('', 0)):
        self.server = Server(client_address, ClientRequestHandler)
        self.server.timeout = 0
        self.socket = self.server.socket
        self.server_address = server_address
        self.pending_proposals = []
        self.ping_statistics = ECDF()
        self.ping_statistics.add(0.01)
        self.number_queue = queue.Queue()
        self.server.received_bytes = self.number_queue.put
        self.last_executed_number = -1
        self.executed = IDSet()
        self.proposal_ids = IDGenerator()
        self.last_get_request = -1
        self.executor = None

    def send_to_server(self, bytes):
        self.socket.sendto(bytes,  self.server_address)

    def create_proposal(self, message_bytes, id = None):
        if id is None:
            id = self.proposal_ids.get_id()
        return Proposal(message_bytes, id, self)

    def propose_to_server(self, message_bytes, id = None):
        return self.create_proposal(message_bytes, id).send()
        
    def _propose_to_server(self, message_bytes, id):
        self.pending_proposals.append((time.time(), id, message_bytes))
        self.send_to_server(COMMANDS['propose_element'] + id + message_bytes)
        return id

    def schedule(self):
        self.server.handle_pending_requests()
        self.retransmit_packets()
        try:
            number = self.number_queue.get_nowait()
        except queue.Empty:
            return
        if number in self.server.values: # possible - race condition
            bytes = self.server.values[number]
            id = bytes[:ID_LENGTH]
            message_bytes = bytes[ID_LENGTH:]
            for i, pending_proposal in enumerate(self.pending_proposals):
                if pending_proposal[1] == id:
                    sending_time = self.pending_proposals.pop(i)[0]
                    self.ping_statistics.add(time.time() - sending_time)
                    break
        self.execute_commands()

    def ping(self):
        return self.ping_statistics.inverse(self.packet_was_lost_probability)

    def retransmit_packets(self):
        # retransmit proposals
        delta = self.ping()
        now = time.time()
        while self.pending_proposals and self.pending_proposals[0][0] + delta <= now:
            proposal = self.pending_proposals.pop(0)
            self.propose_to_server(proposal[2], proposal[1])
        # transmit get requests for lost updates
        if now - self.last_get_request > self.ping():
            self.last_get_request = now
            self.send_get_request()

    def send_get_request(self):
        self.send_to_server(COMMANDS['get_element'] + number2bytes(self.last_executed_number + 1))

    def execute_commands(self):
        while self.last_executed_number + 1 in self.server.values:
            number = self.last_executed_number + 1
            bytes = self.server.values[number]
            id = bytes[:ID_LENGTH]
            if id not in self.executed:
                message_bytes = bytes[ID_LENGTH:]
                self.execute_command(message_bytes, id, number)
                self.executed.add(id)
            self.last_executed_number += 1
        for key in list(self.server.values.keys()):
            if key <= self.last_executed_number:
                self.server.values.pop(key)

    def was_executed(self, id):
        return id in self.executed

    def add_executor(self, executor):
        assert self.executor is None, 'there is only one executor supported'
        self.executor = executor

    def execute_command(self, bytes, id, transaction_number):
        if self.executor:
            self.executor.execute_command(bytes, id, transaction_number)
        else:
            print('execute_command:', bytes, id, transaction_number)

    def close(self):
        self.server.server_close()

def test_get_clients():
    from server import main as server_main
    from threading import Thread
    t = Thread(target = server_main)
    t.deamon = True
    t.start()
    c = Client(('localhost', 6028))
    c2 = Client(('localhost', 6028))
    return c, c2

__all__ = ['Client', 'test_get_clients']

if __name__ == '__main__':
    c, c2 = test_get_clients()

    c.propose_to_server(b'NANANANANANANANANANANANANANANNANNANNANANANANANANA')

    then = time.time()
    time.sleep(0.1)
    while time.time() - 1 < then:
        c.schedule()
        time.sleep(0.001)
        
    print('scheduled')

    then = time.time()
    while time.time() - 1 < then:
        c2.schedule()
        time.sleep(0.001)
    
