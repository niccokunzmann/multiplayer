
from serialization import Serializer, RegistrationError
import collections
import concurrent.futures
from weakref import WeakValueDictionary
import sys
import traceback

class Future(concurrent.futures.Future):

    def set_to_function_call(self, function, args, kw):
        try:
            result = function(*args, **kw)
        except:
            self.set_to_exception()
        else:
            self.set_result(result)

    def set_to_exception(self):
        ty, err, tb = sys.exc_info()
        if hasattr(err, 'with_traceback'):
            self.set_exception(err.with_traceback(tb))
        else:
            self.set_exception(err)

    def set_to_method_call(self, obj, name, args, kw):
        try:
            set_to_function_call(getattr(obj, name), args, kw)
        except:
            self.set_to_exception()



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
                future.set_to_function_call(self.function, (self,) + self.args, self.kw)
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

    PointInTranstactionChainClass = PointInTranstactionChain
    new_future = Future

    def __init__(self, client):
        self.client = client
        self.serializer = Serializer()
        self.ready_transactionPoints = []
        self.client.add_executor(self) # register at client
        self.dependencies = collections.defaultdict(list)
        self.futures = {}
        self.register = self.serializer.register

    def execute_command(self, bytes, id, transaction_number):
        """called by the client"""
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

    def future_call(self, function, args = (), kw = {}, dependencies = ()):
        command = self.get_command(function, args, kw)
        id = command.id
        future = self._create_future(id)
        command.send()
        return future

    def was_executed(self, id):
        return self.client.was_executed(id)

    def _create_future(self, id):
        future = self.new_future()
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

__all__ = ['Executor', 'RegistrationError']

if __name__ == '__main__':
    import time
    from client import test_get_clients
    c1, c2 = test_get_clients()
    e1 = Executor(c1)
    e2 = Executor(c2)

    def test_print(*args):
        print('test_print', args)
        return args

    fut = e1.future_call(test_print, args = ('arguments', ))
    while not fut.done():
        c2.schedule()
        c1.schedule()
    time.sleep(0.1)
    c2.schedule()
    c1.schedule()

    print('result:', fut.result())
    
