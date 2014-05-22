from id import IDGenerator
import pickle
import io

class RegistrationError(ValueError):
    pass

class Serializer:

    def __init__(self):
        self.id_generator = IDGenerator()
        self.id_to_object = {}

    def new_id(self):
        return self.id_generator.get_id()

    def get_id(self, obj):
        """return the id of an object. return None if ther is no id."""
        id_function = getattr(obj, 'get_unique_identifier', None)
        if id_function is None:
            return
        return id_function()

    def _check_id(self, id, obj):
        if id not in self.id_to_object:
            raise RegistrationError("{} not registered under {}. The id is not in use.".format(obj, rer(id)), id)
        if self.id_to_object[id] is not obj:
            message = "get_unique_identifier() must return the id of the registered object. {} has not been registered under id {}.".format(obj, repr(id))
            if id in self.id_to_object:
                message += "But {} is registered under id {}.".format(self.id_to_object[id], repr(id))
            raise RegistrationError(message, id)


    def _persistent_id(self, obj):
        id = self.get_id(obj)
        if id is None:
            return
        self._check_id(id, obj)
        return id

    def register(self, obj, id = None, force = False, check = True):
        """register an object under a new id so that it can be serialized.
        if id is None: a new id is created
        Returns the id of the object."""
        _id = self.get_id(obj)
        if id is None:
            if _id is not None and not force:
                raise ValueError("Usually, you do not need to register {} with the id {} under a new random id. Use force = True if you really want to.".format(obj, repr(id)))
            id = self.new_id()
                
        def get_unique_identifier():
            """returns a unique identifier of the object.
            This is used to identify objects across clients."""
            return id
        obj.get_unique_identifier = get_unique_identifier
        self.id_to_object.setdefault(id, obj)
        if check:
            self._check_id(id, obj)
        return id

    def register_default(self, obj, id, force = False):
        self.register(obj, id, force = force, check = False)
        return self.id_to_object[id]

    def _persistent_load(self, id):
        if id not in self.id_to_object:
            raise pickle.UnpicklingError("unsupported persistent id {} encountered".format(id), id)
        return self.id_to_object[id]

    def dumps(self, obj):
        file = io.BytesIO()
        self.dump(obj, file)
        bytes = file.getvalue()
        return bytes

    def dump(self, obj, file):
        p = pickle.Pickler(file)
        p.persistent_id = self._persistent_id
        p.dump(obj)

    def loads(self, bytes):
        file = io.BytesIO(bytes)
        return self.load(file)

    def load(self, file):
        p = pickle.Unpickler(file)
        p.persistent_load = self._persistent_load
        return p.load()


__all__ = ['Serializer', 'RegistrationError']

def test(obj):
    s = Serializer()
    id = s.register(obj)
    b = s.dumps(obj)
    assert id in b
    obj2 = s.loads(b)
    assert obj2 is obj
    

if __name__ == '__main__':

#    test(object()) # TODO
#    test('hallo') # TODO
    class X:pass
    test(X())
