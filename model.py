
from Executor import *

class Distributor:

    ExecutorClass = Executor

    def __init__(self, client):
        self.client = client
        self.executor = self.ExecutorClass(client)
        self.register = self.executor.register
        self.new_future = self.executor.new_future
        

def t()

class FutureProxy:

    class ProxyAttribute:
        def __init__(self, name, proxiedMethod):
            self.name = name
            self.proxiedMethod = proxiedMethod

        def __get__(self, dist, cls):
            return proxiedMethod.__get__(dist, cls)

        def __set__(self, obj, cls):
            raise NotImplementedError('Can not set attribute {} of {}'.format(self.name, cls))
            # TODO

        def __del__(self, obj, cls):
            raise NotImplementedError('Can not delete attribute {} of {}'.format(self.name, cls))

    def __init__(self, obj, distributor, read, write, created_id):
        self._obj = obj
        self._read = read
        self._write = write
        self._distributor = distributor
        self._last_write_transaction_id = created_id
        self._last_read_transaction_id = created_id

    def _is_read_method(self, name):
        return name in self._read

    def _is_write_method(self, name):
        return name in self._write

    def __getattr__(self, name):
        self._create_proxy_attribute(name)
        return getattr(self, name)

    def _create_proxy_attribute(self, name):
        setattr(self.__class__, name, self.ProxyAttribute(name, self.get_proxy_method(name)))

    @staticmethod
    def get_proxy_method(name):
        def proxy_method(self, *args, **kw):
            if self._is_write_method(name):
                dependencies = (self._last_write_transaction_id,
                                self._last_read_transaction_id)
            elif self._is_read_method(name):
                dependencies = (self._last_write_transaction_id,)
            else:
                future = self._distributor.new_future()
                future.set_to_method_call(self._obj, name, args, kw)
                return future
            return self._distributor.future_call(self.transaction, (self, name, args, kw))
            
        proxy_method.__name__ = name
        return proxy_method

    transaction = staticmethod(t)
    
        
    



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
