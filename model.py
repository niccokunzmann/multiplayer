from .execution import *
from .FutureProxy import *
from .updater import ManualUpdater
from .access_mapping import get_access_mapping

from functools import wraps


def p(distributor, obj, accessFactory, proxyClass, id = None):
    return distributor._get_proxy(obj, accessFactory, proxyClass, id,
                                  transaction().id)

def call(function, args, kw):
    return function(*args, **kw)

class Model:

    ExecutorClass = Executor
    ProxyClass = staticmethod(FutureProxy)

    MODEL_STATE_ID = 'MODEL_STATE'

    update_interval = 0.002

    def __init__(self, client):
        self._client = client
        self._executor = self.ExecutorClass(client)
        self._register = self._executor.register
        self._register_default = self._executor.register_default
        self._register(self, self.__class__)
        self._updater = ManualUpdater(client)
        self._everywhere_proxy = None
        self._state = self.proxy(self._new_model_state(), id = self.MODEL_STATE_ID)

    @property
    def state(self):
        return self._state

    def _new_model_state(self):
        return {}

    def proxy(self, obj, accessFactory = None, id = None):
        if accessFactory is None:
            accessFactory = self._find_access_factory_for(obj)
        future_to_proxy = self._executor.future_call(self._proxy, (self, obj, accessFactory, self.ProxyClass, id))
        return self._get_proxy(obj, accessFactory, self.ProxyClass, id,
                               future_to_proxy.id)

    def _get_proxy(self, obj, accessFactory, proxyClass, id, dependency):
        if id is None:
            id = dependency
        read, const = accessFactory()
        proxy = proxyClass(obj, self._executor, read, const, dependency)
        return self._register_default(proxy, id)

    def _find_access_factory_for(self, obj):
        return get_access_mapping(type(obj))

    def list(self, from_list = [], id = None):
        return self.proxy(list(from_list), id = id)

    def everywhere(self, callable):
        assert hasattr(callable, '__call__')
        if self._everywhere_proxy is None:
            self._everywhere_proxy = self.proxy(call)
        @wraps(callable)
        def _call(*args, **kw):
            if transaction():
                return callable(*args, **kw)
            return self._everywhere_proxy(_call, args, kw)
        _call.__module__ = callable.__module__
        return _call

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

__all__ = ['Model']
