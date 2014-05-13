
from serialization import Serializer
import collections
from concurrent.futures import Future
from weakref import WeakValueDictionary
import sys


class Executor:

    futures = WeakValueDictionary()

    def __init__(self, client):
        self.client = client
        self.serializer = Serializer()
        self.client.execute_command = self._execute_command

    def _execute_command(self, bytes, id, transaction_number):
        command = self.serializer.loads(bytes)
        function = command[0]
        if len(command) >= 2:
            args = command[1]
        else:
            args = ()
        if len(command) >= 3:
            kw = command[2]
        else:
            kw = {}
        future = self._get_future(id)
        if future is None:
            function(id, transaction_number, *args, **kw)
        else:
            try:
                result = function(id, transaction_number,  *args, **kw)
            except:
                ty, err, tb = sys.exc_info()
                if hasattr(err, 'with_traceback'):
                    future.set_exception(err.with_traceback(tb))
                else:
                    future.set_exception(err)
            else:
                future.set_result(result)

    def get_command(self, function, args = (), kw = {}):
        if kw:
            command = (function, args, kw)
        elif args:
            command = (function, args)
        else:
            command = (function,)
        message = self.serializer.dumps(command)
        return self.client.create_proposal(message)

    def send_command(self, function, args = (), kw = {}):
        return self._get_command(function, args, kw).send()

    def send_future(self, function, args = (), kw = {}):
        command = self.get_command(function, args, kw)
        id = command.id
        future = self._create_future(id)
        command.send()
        return future

    def _create_future(self, id):
        future = Future()
        self.futures[id] = future
        return future

    def _get_future(self, id):
        return self.futures.get(id)

if __name__ == '__main__':
    from client import test_get_clients
    c1, c2 = test_get_clients()
    e1 = Executor(c1)
    e2 = Executor(c2)

    def test_print(*args):
        print('test_print', args)
        return args

    fut = e1.send_future(test_print, args = ('args', ))
    while not fut.done():
        c1.schedule()
        c2.schedule()

    print(fut.result())
    

##class Model:
##
##    def __init__(self, obj, shared_model):
##        self.obj = obj
##        self.shared_model = shared_model
##
##    def future_call(self, name, args, kw):
##        
##
##class ModelList(collections.UserList):
##
##    # these methods change the state
##
##    def __init__(self, initlist = ):
####    def __setitem__(self, i, item): self.data[i] = item
####    def __delitem__(self, i): del self.data[i]
####    def __iadd__(self, other):
####    def __imul__(self, n):
##    def append(self, item): self.data.append(item)
####    def insert(self, i, item): self.data.insert(i, item)
####    def pop(self, i=-1): return self.data.pop(i)
####    def remove(self, item): self.data.remove(item)
####    def clear(self): self.data.clear()
####    def reverse(self): self.data.reverse()
####    def sort(self, *args, **kwds): self.data.sort(*args, **kwds)
####    def extend(self, other):
##    
##    # these methods use __class__ to create new objects
####    def __add__(self, other):
####        if isinstance(other, UserList):
####            return self.__class__(self.data + other.data)
####        elif isinstance(other, type(self.data)):
####            return self.__class__(self.data + other)
####        return self.__class__(self.data + list(other))
####    def __radd__(self, other):
####        if isinstance(other, UserList):
####            return self.__class__(other.data + self.data)
####        elif isinstance(other, type(self.data)):
####            return self.__class__(other + self.data)
####        return self.__class__(list(other) + self.data)
####    def __mul__(self, n):
####        return self.__class__(self.data*n)
####    __rmul__ = __mul__
####    def copy(self): return self.__class__(self)
##    
