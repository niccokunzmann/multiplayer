
access_mapping = {}

def _best_mapping_type(x):
    if isinstance(x, str):
        x = str.split()
    # todo: estimate size according to benchmark
    if len(x) > 10:
        return set(x)
    return list(x)

def map(cls, read, constant = ()):
    def access(read = read, constant = constant):
        return read, constant
    access.__name__ = cls.__name__ + '_access'
    access_mapping[cls] = access
    globals(access.__name__) = access
    access.__doc__ = "access for {}.{} objects".format(cls.__module__, cls.__name__)

map(list, ['__add__', '__contains__', '__dir__', '__doc__', '__eq__',
           '__format__', '__ge__', '__getitem__', '__gt__', '__hash__',
           '__iter__', '__le__', '__len__', '__lt__', '__mul__', '__ne__',
           '__reduce__', '__reduce_ex__', '__repr__', '__reversed__',
           '__rmul__', '__sizeof__', '__str__', 'append', 'copy', 'count',
           'index'], ['__class__', '__subclasshook__'])

def default_access():
    return (), ('__class__', '__subclasshook__')

def get_access_mapping(cls, default = default_access):
    if cls in access_mapping:
        return access_mapping[cls]
    return default
