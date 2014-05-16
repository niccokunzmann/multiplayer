
from Executor import *

        
    
def p(transaction, distributor, obj, accessFactory):
    distributor._register(obj, transaction.id)


class Distributor:

    ExecutorClass = Executor

    def __init__(self, client):
        self._client = client
        self._executor = self.ExecutorClass(client)
        self._register = self._executor.register
        self._register(self, self.__class__)

    def local(self, obj, name):
        

    def proxy(self, obj, accessFactory):
        return self._executor.future_call(self._proxy, (self, obj, accessFactory, self.proxyClass))

    def list(self, from_list = []):
        return self.proxy(from_list, listAccess)

    _proxy = staticmethod(p)
    

list_read = set(['get'])
list_write = set(['append'])

def listAccess():
    return list_read, list_write



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
