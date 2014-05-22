from server import Server, ClientRequestHandler, COMMANDS, number2bytes
from endpoint import *
from threading import Thread
import time

from statistics import ECDF
import queue
import io

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

class Transaction:

    def __init__(self, number, bytes):
        self.number = number
        self._bytes = bytes

    @property
    def id(self):
        return self._bytes[:ID_LENGTH]

    @property
    def bytes(self):
        return self._bytes[ID_LENGTH:]

    def get_reader(self):
        file = io.BytesIO(self._bytes)
        file.seek(ID_LENGTH)
        return file


class Client:

    # 0.95 = packet as lost with 95% probability
    packet_was_lost_probability = 0.95
    ping_probability = 0.5

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.pending_proposals = []
        self.ping_statistics = ECDF()
        self.ping_statistics.add(0.01)
        self.number_queue = queue.Queue()
        self.last_executed_number = -1
        self.executed = IDSet()
        self.proposal_ids = IDGenerator()
        self.last_get_request = -1
        self.executor = None
        self.transactions = {} # number : transaction
        self._closed = False

    def send_to_server(self, bytes):
        self.endpoint.send_to_server(bytes)

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
        self.endpoint.schedule()
        self.copy_new_transactions()
        self.retransmit_packets()
        self.execute_commands()

    def copy_new_transactions(self):
        while self.endpoint.values:
            transaction_number, bytes = self.endpoint.values.popitem()
            transaction = Transaction(transaction_number, bytes)
            self.transactions[transaction_number] = transaction
            self._remove_pending_proposal(transaction.id)

    def _remove_pending_proposal(self, id):
        for i, pending_proposal in enumerate(self.pending_proposals):
            if pending_proposal[1] == id:
                sending_time = self.pending_proposals.pop(i)[0]
                self.ping_statistics.add(time.time() - sending_time)
                break

    def ping(self):
        return self.ping_statistics.inverse(self.ping_probability)

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
        while self.last_executed_number + 1 in self.transactions:
            number = self.last_executed_number + 1
            transaction = self.transactions[number]
            id = transaction.id
            if id not in self.executed:
                self.execute_command(transaction)
                self.executed.add(id)
            self.last_executed_number += 1
        for key in list(self.transactions.keys()):
            if key <= self.last_executed_number:
                self.transactions.pop(key)

    def was_executed(self, id):
        return id in self.executed

    def add_executor(self, executor):
        assert self.executor is None, 'there is only one executor supported'
        self.executor = executor

    def execute_command(self, transaction):
        if self.executor:
            self.executor.execute_command(transaction)
        else:
            print('execute_command:', transaction.id, transaction.number)

    def close(self):
        self.endpoint.close()
        self._closed = True

    def is_closed(self):
        return self._closed

    def set_endpoint(self, endpoint):
        self.endpoint = endpoint

def test_get_clients():
    from server import main as server_main
    from threading import Thread
    t = Thread(target = server_main)
    t.deamon = True
    t.start()
    c = Client(UDPEndpoint(('localhost', 6028)))
    c2 = Client(UDPEndpoint(('localhost', 6028)))
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
    
