import sys; sys.path.append('../..')

from multiplayer.client import *
import time

c, c2 = test_get_clients()

c.propose_to_server(b'NANANANANANANANANANANANANANANNANNANNANANANANANANA')

then = time.time()
time.sleep(0.1)
while time.time() - 1 < then:
    c.schedule()
    time.sleep(0.001)
    
print('scheduled')

then = time.time()
while time.time() - 1 < then:
    c2.schedule()
    time.sleep(0.001)
