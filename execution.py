from contextlib import contextmanager
from serialization import Serializer, RegistrationError
import collections
import concurrent.futures
from weakref import WeakValueDictionary
import sys
import traceback
from threading import current_thread

allow_errors = False

class Future(concurrent.futures.Future):

    def set_to_function_call(self, function, args = (), kw = {}):
        try:
            result = function(*args, **kw)
        except:
            if not allow_errors:
                raise
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
            self.set_to_function_call(getattr(obj, name), args, kw)
        except:
            if not allow_errors:
                raise
            self.set_to_exception()



def transaction():
    """=> the current active transaction"""
    return _transactions.get(_thread_id())

_transactions = {}

_thread_id = lambda: id(current_thread())

@contextmanager
def in_transaction(transaction):
    thread_id = _thread_id()
    saved_transaction = _transactions.get(thread_id)
    _transactions[thread_id] = transaction
    try:
        yield
    finally:
        if saved_transaction is None:
            del _transactions[thread_id]
        else:
            _transactions[thread_id] = saved_transaction

class PointInTranstactionChain:

    def __init__(self, executor, id, transaction_number, dependencies,
                 future, serializer, function_args_kw):
        self.executor = executor
        self.id = id
        self.transaction_number = transaction_number
        self.dependencies = dependencies
        assert not self.executor.was_executed(id)
        self.future = future
        self.function_args_kw = function_args_kw
        self.unfulfilled_dependencies = set()
        self._append_to_dependencies()
        self.serializer = serializer

    def __str__(self):
        dependencies = (' after: {self.dependencies}'.format(self = self) if self.dependencies else '')
        return '<{self.__class__.__name__} at {self.transaction_number} id: {self.id}{dependencies}>'.format(
            self = self, dependencies = dependencies)

    __repr__ = __str__

    def execute(self):
        assert self.can_execute()
        try:
            with in_transaction(self):
                future = self.future
                if future is None:
                    try:
                        self._execute()
                    except:
                        self.print_exc()
                else:
                    future.set_to_function_call(self._execute)
        finally:
            self.executor.dependency_fulfilled(self.id)

    def _execute(self):
        function, args, kw = self.serializer.loads(self.function_args_kw)
        return function(*args, **kw)
        

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

    def is_from_here(self):
        return self.future is not None

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
        self.register_default = self.serializer.register_default

    def execute_command(self, transaction):
        """called by the client"""
        try:
            command = self.serializer.load(transaction.get_reader())
            dependencies, function_args_kw = command
            future = self._get_future(transaction.id)
            transactionPoint = self.PointInTranstactionChainClass(
                self, transaction.id, transaction.number, dependencies,
                future, self.serializer, function_args_kw)
            if transactionPoint.can_execute():
                transactionPoint.execute()
            while self.ready_transactionPoints:
                transactionPoint = self.ready_transactionPoints.pop()
                transactionPoint.execute()
        finally:
            self._del_future_reference(id)

    def get_command(self, function, args = (), kw = {}, dependencies = ()):
        command = dependencies, self.serializer.dumps((function, args, kw))
        message = self.serializer.dumps(command)
        return self.client.create_proposal(message)

    def future_call(self, function, args = (), kw = {}, dependencies = ()):
        command = self.get_command(function, args, kw, dependencies = dependencies)
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

__all__ = ['Executor', 'RegistrationError', 'transaction']

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
    
