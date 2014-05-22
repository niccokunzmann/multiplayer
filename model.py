from .execution import *
from .FutureProxy import *
from .updater import ManualUpdater


def p(distributor, obj, accessFactory, proxyClass):
    id = transaction().id
    return distributor._get_proxy(obj, accessFactory, proxyClass, id)


class Model:

    ExecutorClass = Executor
    ProxyClass = FutureProxy

    update_interval = 0.002

    def __init__(self, client):
        self._client = client
        self._executor = self.ExecutorClass(client)
        self._register = self._executor.register
        self._register_default = self._executor.register_default
        self._register(self, self.__class__)
        self._updater = ManualUpdater(client)

    def proxy(self, obj, accessFactory):
        future_to_proxy = self._executor.future_call(self._proxy, (self, obj, accessFactory, self.ProxyClass))
        id = future_to_proxy.id
        return self._get_proxy(obj, accessFactory, self.ProxyClass, id)

    def _get_proxy(self, obj, accessFactory, proxyClass, id):
        read, write = accessFactory()
        proxy = proxyClass(obj, self._executor, read, write, id)
        return self._register_default(proxy, id)

    def list(self, from_list = []):
        return self.proxy(from_list[:], listAccess)

    def everywhere(self, callable):
        assert hasattr(callable, '__call__')
        return ModelFunction(self, callable)

    transaction = staticmethod(transaction)

    _proxy = staticmethod(p)

    def set_updater(self, update_strategy):
        """set the updater strategy. see the updater module."""
        self._updater.stop()
        self._updater = update_strategy(self._client)
        self._updater.start()

    def update(self):
        """update the model. receive calls from the server and send lost calls.
        check is_updating_automatically before you call it."""
        self._updater.update()

    def is_updating_automatically(self):
        """=> if False you need to call update() yourself.
        if True the model will update itself without you needing to do anything"""
        return self._updater.is_updating()
    

list_read = set(['count'])
list_write = set(['append'])

def listAccess():
    return list_read, list_write

def functionAccess():
    return (), ('__call__',)

class ModelFunction:

    def __init__(self, model, function):
        self.proxy = None
        self.model = model
        self.function = function
        self.__name__ = function.__name__
        self.__qualname__ = getattr(function, '__qualname__', None)
        self.__module__ = function.__module__

    def __reduce__(self):
        return self.function.__name__

    def __call__(self, *args, **kw):
        if transaction():
            return self.function(*args, **kw)
        if self.proxy is None:
            self.proxy = self.model.proxy(self, functionAccess)
        return self.proxy(*args, **kw)
