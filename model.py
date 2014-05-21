from execution import *
from FutureProxy import *

def p(transaction, distributor, obj, accessFactory, proxyClass):
    read, write = accessFactory()
    proxy = proxyClass(obj, distributor._executor, read, write, transaction.id)
    distributor._register(proxy, transaction.id)
    return proxy

class Distributor:

    ExecutorClass = Executor
    ProxyClass = FutureProxy

    def __init__(self, client):
        self._client = client
        self._executor = self.ExecutorClass(client)
        self._register = self._executor.register
        self._register(self, self.__class__)

    def proxy(self, obj, accessFactory):
        # TODO: future of self?
        return self._executor.future_call(self._proxy, (self, obj, accessFactory, self.ProxyClass))

    def list(self, from_list = []):
        return self.proxy(from_list[:], listAccess)

    _proxy = staticmethod(p)
    

list_read = set(['count'])
list_write = set(['append'])

def listAccess():
    return list_read, list_write

if __name__ == '__main__':
    from client import test_get_clients
    import time
    import threading
    c1, c2 = test_get_clients()
    d1 = Distributor(c1)
    d2 = Distributor(c2)
    l_f = d1.list()
    while not l_f.done():
        c1.schedule()

    li = l_f.result()

    def t():
        while 1:
            c1.schedule()
            c2.schedule()
            time.sleep(0.01)

    thread = threading.Thread(target = t)
    thread.deamon = True
    thread.start()

    future = li.count(1)
    print('f.exception()', future.exception())
    print('f.result()', future.result())
    li.append(3)
    li.append(2)
    li.append(li)
    for i in (1, 2, 3):
        print('li.count({})'.format(i), li.count(i).result())
    print('li.count(li)', li.count(li).result())
##    print(l.not_an_attribute())

