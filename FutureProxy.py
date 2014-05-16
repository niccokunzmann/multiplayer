
def t(transaction, future_proxy, name, args, kw, read, write):
    future_proxy._reset_dependency(name, transaction.id)
    return getattr(future_proxy._obj, name)(*args, **kw)

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

    def __init__(self, obj, executor, read, write, created_id):
        self._obj = obj
        self._read = read
        self._write = write
        self._executor = executor
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
            read = write = False
            if self._is_write_method(name):
                dependencies = (self._last_write_transaction_id,
                                self._last_read_transaction_id)
                write = True
            elif self._is_read_method(name):
                dependencies = (self._last_write_transaction_id,)
                read = True
            else:
                future = self._executor.new_future()
                future.set_to_method_call(self._obj, name, args, kw)
                return future
            return self._executor.future_call(self.transaction, (self, name, args, kw, read, write),
                                              dependencies = dependencies)
        proxy_method.__name__ = name
        return proxy_method

    _transaction = staticmethod(t)

    def _reset_dependency(self, name, id):
        if self._is_read_method(name):
            self._last_read_transaction_id = id
        if self._is_write_method(name): # no elif!
            self._last_write_transaction_id = id
