import sys; sys.path.append('../..')
from multiplayer import *
console_connect_dialog()
@everywhere
def chat(username, words):
    print(username, ":", words)
username = input("Your username:")
while 1:
    text = input("> ")
    chat(username, text)
