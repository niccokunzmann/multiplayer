from pickle import Pickler, Unpickler

class ObjectBase:

    def __init__(self):
        self._id = 0
        self.persistent_mapping = {}
        
    
