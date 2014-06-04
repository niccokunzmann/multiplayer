#!/usr/bin/python3
import sys; sys.path.append('../..')
from multiplayer import *
##import multiplayer.hanging_threads
model = console_connect_dialog()

l = model.list(id = 'test')
