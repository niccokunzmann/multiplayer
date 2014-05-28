from .id import IDGenerator
import pickle
import io

class RegistrationError(ValueError):
    pass

class Serializer:

    def __init__(self):
        self.id_generator = IDGenerator()
        self.id_to_persistent_id = {}
        self.persistent_id_to_object = {}

    def new_id(self):
        return self.id_generator.get_id()

    def get_id(self, obj):
        """return the id of an object. return None if there is no id."""
        _id = id(obj)
        persistent_id = self.id_to_persistent_id.get(_id)
        if persistent_id is None: return
        default = []
        saved_object = self.persistent_id_to_object.get(persistent_id, default)
        if saved_object is obj:
            return persistent_id

    def _check_id(self, persistent_id, obj):
        if persistent_id not in self.persistent_id_to_object:
            raise RegistrationError("{} not registered under {}. The id is not in use.".format(obj, repr(persistent_id)))
        if self.persistent_id_to_object[persistent_id] is not obj:
            message = "get_unique_identifier() must return the id of the registered object. {} has not been registered under id {}.".format(obj, repr(persistent_id))
            other_object = self.persistent_id_to_object.get(persistent_id)
            if other_object is not obj:
                message += "But {} is registered under id {}.".format(other_object, repr(persistent_id))
            raise RegistrationError(message, persistent_id)
        if self.id_to_persistent_id[id(obj)] != persistent_id:
            # Maybe this is so important that it needs to be checked, always.
            # Maybe an assertion?
            other_persistent_id = self.id_to_persistent_id[id(obj)]
            if self.persistent_id_to_object[other_persistent_id] is not obj:
                other_object = self.persistent_id_to_object[other_persistent_id]
                raise RegistrationError("The object {} can not be registered because the object {} "\
                                        "was registered before and both have the same id {}.".format(obj, other_object, id(obj)), persistent_id)


    def _persistent_id(self, obj):
        id = self.get_id(obj)
        if id is None:
            return
        self._check_id(id, obj)
        return id

    def register(self, obj, persistent_id = None, force = False, check = True):
        """register an object under a new id so that it can be serialized.
        if id is None: a new id is created
        Returns the id of the object."""
        other_presistent_id = self.get_id(obj)
        if persistent_id is None:
            if other_presistent_id is not None and not force:
                raise ValueError("Usually, you do not need to register {} with the id {} under a new random id. Use force = True if you really want to.".format(obj, repr(other_presistent_id)))
            persistent_id = self.new_id()
        self.persistent_id_to_object.setdefault(persistent_id, obj)
        self.id_to_persistent_id.setdefault(id(obj), persistent_id)
        if check:
            self._check_id(persistent_id, obj)
        return persistent_id

    def register_default(self, obj, persistent_id, force = False):
        self.register(obj, persistent_id, force = force, check = False)
        return self.persistent_id_to_object[persistent_id]

    def _persistent_load(self, persistent_id):
        if persistent_id not in self.persistent_id_to_object:
            raise pickle.UnpicklingError("unsupported persistent id {} encountered".format(persistent_id), persistent_id)
        return self.persistent_id_to_object[persistent_id]

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

