import time
from multiplayer.client import test_get_clients
from multiplayer.execution import *

c1, c2 = test_get_clients()
e1 = Executor(c1)
e2 = Executor(c2)

def test_print(*args):
    print('test_print', args)
    return args

fut = e1.future_call(test_print, args = ('arguments', ))
while not fut.done():
    c2.schedule()
    c1.schedule()
time.sleep(0.1)
c2.schedule()
c1.schedule()

print('result:', fut.result())
