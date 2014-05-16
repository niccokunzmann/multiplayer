
from serialization import Serializer
import collections
from concurrent.futures import Future
from weakref import WeakValueDictionary
import sys
import traceback

class PointInTranstactionChain:

    def __init__(self, executor, id, transaction_number, dependencies,
                 future, function, args, kw):
        self.executor = executor
        self.id = id
        self.transaction_number = transaction_number
        self.dependencies = dependencies
        assert not self.executor.was_executed(id)
        self.future = future
        self.function = function
        self.args = args
        self.kw = kw
        self.unfulfilled_dependencies = set()
        self._append_to_dependencies()

    def __str__(self):
        return '<{self.__class__.__name__} at {self.transaction_number} id: {self.id}>'.format(
            self = self)

    __repr__ = __str__

    def execute(self):
        assert self.can_execute()
        try:
            future = self.future
            if future is None:
                try:
                    self.function(self, *self.args, **self.kw)
                except:
                    self.print_exc()
            else:
                try:
                    result = self.function(self,  *self.args, **self.kw)
                except:
                    ty, err, tb = sys.exc_info()
                    if hasattr(err, 'with_traceback'):
                        future.set_exception(err.with_traceback(tb))
                    else:
                        future.set_exception(err)
                else:
                    future.set_result(result)
        finally:
            self.executor.dependency_fulfilled(self.id)


    def print_exc(self):
        traceback.print_exc()

    def can_execute(self):
        return not self.unfulfilled_dependencies

    def dependency_fulfilled(self, id):
        self.unfulfilled_dependencies.remove(id)

    def _append_to_dependencies(self):
        for id in self.dependencies:
            if not self.executor.was_executed(id):
                self.executor.add_dependency(id, self)
                self.unfulfilled_dependencies.add(id)
        


class Executor:

    futures = {}
    dependencies = collections.defaultdict(list)
    PointInTranstactionChainClass = PointInTranstactionChain

    def __init__(self, client):
        self.client = client
        self.serializer = Serializer()
        self.client.execute_command = self._execute_command
        self.ready_transactionPoints = []

    def _execute_command(self, bytes, id, transaction_number):
        try:
            command = self.serializer.loads(bytes)
            function, dependencies, args, kw = command
            future = self._get_future(id)
            transactionPoint = self.PointInTranstactionChainClass(
                self, id, transaction_number, dependencies, future, function,
                args, kw)
            if transactionPoint.can_execute():
                transactionPoint.execute()
            while self.ready_transactionPoints:
                transactionPoint = self.ready_transactionPoints.pop()
                transactionPoint.execute()
        finally:
            self._del_future_reference(id)

    def get_command(self, function, args = (), kw = {}, dependencies = ()):
        command = (function, dependencies, args, kw)
        message = self.serializer.dumps(command)
        return self.client.create_proposal(message)

    def send_future(self, function, args = (), kw = {}, dependencies = ()):
        command = self.get_command(function, args, kw)
        id = command.id
        future = self._create_future(id)
        command.send()
        return future

    def was_executed(self, id):
        return self.client.was_executed(id)

    def _create_future(self, id):
        future = Future()
        self.futures[id] = future
        future.id = id
        return future

    def _get_future(self, id):
        return self.futures.get(id)

    def _del_future_reference(self, id):
        if id in self.futures:
            del self.futures[id]

    def add_dependency(self, id, pointInTransactionChain):
        self.dependencies[id].append(pointInTransactionChain)

    def dependency_fulfilled(self, id):
        if id in self.dependencies:
            for waitingTransactionPoint in self.dependencies.pop(id):
                waitingTransactionPoint.dependency_fulfilled(id)
                if waitingTransactionPoint.can_execute():
                    self.ready_transactionPoints.append(waitingTransactionPoint)

if __name__ == '__main__':
    import time
    from client import test_get_clients
    c1, c2 = test_get_clients()
    e1 = Executor(c1)
    e2 = Executor(c2)

    def test_print(*args):
        print('test_print', args)
        return args

    fut = e1.send_future(test_print, args = ('arguments', ))
    while not fut.done():
        c2.schedule()
        c1.schedule()
    time.sleep(0.1)
    c2.schedule()
    c1.schedule()

    print('result:', fut.result())
    
