import sys; sys.path.append('../..')

from multiplayer.ConnectionFactory import *
import time
import multiplayer.server as server
import threading
t = threading.Thread(target = server.main)
t.start()
cf = ConnectionFactory()
import time
while 1:
    cf.schedule()
    new_servers = cf.new_servers()
    if new_servers:
        print(new_servers)
    time.sleep(0.01)
