from .ConnectionFactory import *
import traceback


def console_connect_dialog():
    return ConsoleConnectDialog().ask_and_return_endpoint()


class NoConnectionChosenError(Exception):
    pass

class ConsoleConnectDialog:

    def __init__(self):
        self.endpoint_factory = None

    def input(self):
        return input('> ')

    def ask(self):
        while 1:
            print('Connection Options:')
            print('0... be a server')
            print('1... LAN (default)')
            print('b... to go back')
            selection = self.input()
            if selection in '0Oo':
                if self.ask_server(): return True
            elif selection in '1Ll':
                if self.ask_LAN(): return True

    def ask_server(self):
        self.set_endpoint(ServerEndpointFactory())
        return True

    def ask_LAN(self):
        lan = LANDiscoverer()
        while 1:
            lan.schedule()
            print('Choose your LAN connection:')
            servers = lan.new_servers()
            for i, server in enumerate(servers):
                print(i, server.get_simple_description())
            print('b... to go back')
            print('.... press enter to refresh or enter your own connection')
            selection = self.input()
            if selection:
                for i, server in enumerate(servers):
                    if str(i) == selection.strip():
                        self.set_endpoint(server)
                        return True
                try:
                    self.set_endpoint(URLEndpointFactory(selection))
                except:
                    traceback.print_exc()
                else: return True
            if selection.strip() == 'b':
                break

    def set_endpoint(self, server):
        print('connection to', server.get_simple_description())
        self.endpoint_factory = server

    def get_endpoint(self):
        if self.endpoint_factory is None:
            raise NoConnectionChosenError('Did not choose a connection')
        return self.endpoint_factory.get_endpoint()

    def ask_and_return_endpoint(self):
        self.ask()
        return self.get_endpoint()
