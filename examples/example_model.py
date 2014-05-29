from multiplayer.client import test_get_clients
from multiplayer.model import *

import time
import threading
c1, c2 = test_get_clients()
d1 = Model(c1)
d2 = Model(c2)
li = d1.list()

def t():
    while 1:
        c1.schedule()
        c2.schedule()
        time.sleep(0.01)

thread = threading.Thread(target = t)
thread.deamon = True
thread.start()

future = li.count(1)
print('f.exception()', future.exception())
print('f.result()', future.result())
li.append(3)
li.append(3)
li.append(li)
for i in (1, 2, 3):
    print('li.count({})'.format(i), li.count(i).result())
print('li.count(li)', li.count(li).result())
##    print(l.not_an_attribute())

print('isinstance(li, list)', isinstance(li, list))
if bool(li):
    print('li is True')
