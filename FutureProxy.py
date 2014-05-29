
from .execution import transaction
from .magicMethods import magicMethods, noMagicMethods

import types

def t(proxy, name, args, kw):
    guts = proxy._guts()
    guts.reset_dependency(name, transaction().id)
    return guts.call(proxy, name, args, kw)

class ProxyGuts:

    # see https://docs.python.org/3.3/reference/datamodel.html
    future_free_attributes = set("""__subclasscheck__ __bool__ __int__ __length_hint__ __hash__ __format__ __dir__ __index__ __contains__""".split())

    def __init__(self, obj, executor, read, const, created_id):
        """
        obj
            the object that shall be proxied to
        executor
            the object that executes the commands and returns futures
        read
            set of method names that to not change the state of the object
        const
            set of method names that do not depend on the state of the object
        created_id
            the first transaction id after which is object is created"""
        self.obj = obj
        self.read = read
        self.local = const
        self.executor = executor
        self.last_write_transaction_id = created_id
        self.last_read_transaction_id = created_id

    def set_attribute(self, proxy, name, value):
        raise NotImplementedError('Can not set attributes of proxied objects. Use function calls for that.')

    def delete_attribute(self, proxy, name):
        raise NotImplementedError('Can not delete attributes of proxied objects. Use function calls for that.')

    def call_attribute_future(self, proxy, name, args, kw):
        if transaction():
            return self.call_attribute_in_transaction(proxy, name, args, kw)
        if self.is_write_method(name):
            return self.call_write_attribute(proxy, name, args, kw)
        if self.is_read_method(name):
            return self.call_write_attribute(proxy, name, args, kw)
        return self.call_const_attribute(proxy, name, args, kw)

    def call_attribute(self, proxy, name, args, kw):
        future = self.call_attribute_future(proxy, name, args, kw)
        if self.is_future_free_attribute(name):
            return future.result() # TODO: maliciously blocking if no threads
        return future

    def is_future_free_attribute(self, name):
        return name.startswith('__') and name in self.future_free_attributes

    def call_const_attribute(self, proxy, name, args, kw):
        future = self.executor.new_future()
        future.set_to_method_call(self.obj, name, args, kw)
        return future

    call_attribute_in_transaction = call_const_attribute

    def call_write_attribute(self, proxy, name, args, kw):
        dependencies = (self.last_write_transaction_id,
                        self.last_read_transaction_id)
        return self.executor.future_call(self.transaction,
                                          (proxy, name, args, kw),
                                          dependencies = dependencies)

    def call_read_attribute(self, proxy, name, args, kw):
        dependencies = (self.last_write_transaction_id,)
        return self.executor.future_call(self.transaction,
                                          (proxy, name, args, kw),
                                          dependencies = dependencies)

    def call(self, proxy, name, args, kw):
        method = getattr(self.obj, name)
        return method(*args, **kw)

    def is_read_method(self, name):
        return name in self.read

    def is_write_method(self, name):
        return name not in self.local and name not in self.read

    transaction = staticmethod(t)

    def reset_dependency(self, name, id):
        if self.is_read_method(name):
            self.last_read_transaction_id = id
        if self.is_write_method(name): # no elif!
            self.last_write_transaction_id = id

class FutureProxyBase:
    """use FutureProxy.new(...) to create instances"""

    _ProxyGutsClass = ProxyGuts

    def __init__(self, *args, **kw):
        guts = type(self)._ProxyGutsClass(*args, **kw)
        object.__setattr__(self, '__guts', guts)

    __getattribute__ = object.__getattribute__

    def __getattr__(self, name):
        type(type(self)).add_method(type(self), name)
        return getattr(self, name)

    def __setattr__(self, name, value):
        return object.__getattribute__(self, '__guts').set_attribute(self, name, value)
        
    def __delattr__(self, name):
        return object.__getattribute__(self, '__guts').delete_attribute(self, name)

    def _guts(self):
        return object.__getattribute__(self, '__guts')

    def __dir__(self):
        return object.__dir__(self)

    def __reduce__(self):
        raise NotImplementedError('You can not pickle this object. Register it in the serailizer to make it picklable.')

class FutureProxyMeta(type):
    class_to_proxy_class = {}
    base = FutureProxyBase
    _initialized = False

    # __prepare__
    @classmethod
    def get_dict(mcls, proxied_class):
        return dict(__name__ = proxied_class.__name__,
                    __module__ = mcls.__module__)

    def __new__(mcls, proxied_class):
        if proxied_class not in mcls.class_to_proxy_class:
            proxy_class = type.__new__(mcls, proxied_class.__name__, (mcls.base,), mcls.get_dict(proxied_class))
            mcls.class_to_proxy_class.setdefault(proxied_class, proxy_class)
        return mcls.class_to_proxy_class[proxied_class]

    def add_method(cls, name):
        proxied_method = getattr(cls.ProxiedClass, name) # TODO: what is not present
        if name not in cls.__dict__ and name not in noMagicMethods and name not in cls.base.__dict__:
            def method(self, *args, **kw):
                return object.__getattribute__(self, '__guts').call_attribute(self, name, args, kw)
            method.__name__ = name
            method.__qualname__ = cls.__qualname__ + '.' + name
            method.__doc__ = proxied_method.__doc__
            setattr(cls, name, method)

    def __init__(cls, ProxiedClass):
        if not cls._initialized:
            cls.ProxiedClass = ProxiedClass
            for method_name in dir(ProxiedClass):
                cls.add_method(method_name)
            cls._initialized = True


def FutureProxy(obj, *args):
    return FutureProxyMeta(type(obj))(obj, *args)

__all__ = ['FutureProxy', 'FutureProxyMeta']
