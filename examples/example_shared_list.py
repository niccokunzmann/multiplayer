#!/usr/bin/python3
import sys; sys.path.append('../..')
from multiplayer import *
model = console_connect_dialog()

l = model.list(id = 'test')
