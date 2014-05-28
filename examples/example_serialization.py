import sys; sys.path.append('../..')

from multiplayer.serialization import *


def test(obj):
    s = Serializer()
    id = s.register(obj)
    b = s.dumps(obj)
    assert id in b, b
    obj2 = s.loads(b)
    assert obj2 is obj, obj
    

# TODO?
test(object()) # TODO
test('hallo') # TODO
class X:pass
test(X())
