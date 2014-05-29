from .ConnectionFactory import *
from .holepunch import *
from .stun import *
import traceback


def console_connect_dialog():
    return ConsoleConnectDialog().ask_and_return_endpoint()

class NoConnectionChosenError(Exception):
    pass

class ConsoleConnectDialog:

    def __init__(self):
        self.endpoint_factory = None
        self.hole_puncher = 

    def input(self):
        return input('> ')

    def ask(self):
        while 1:
            print('Connection Options:')
            print('0... be a server')
            print('1... LAN (default)')
            print('2... internet')
            print('b... to go back')
            selection = self.input()
            if selection in '0Oo':
                if self.ask_server(): return True
            elif selection in '1Ll':
                if self.ask_LAN(): return True
            elif selection == 'b':
                return False
            elif selection == '2':
                if self.ask_internet(): return True

    def ask_internet(self):
        print('The only option available is hole punching.')
        hole_punch = HolePunchMechanism()
        stun = StunAddressRequester(('', hole_punch.port))
        while 1:
            print(' ...Type in the server url udp://...:...')
            print('b... to go back')
            selection = self.input()
            if selection == 'b':
                return False
            if selection:
                hole_punch.punch_to(selection)
            if hole_punch.punch_failed:
                print('Punching my way to the invited people ...')
                hole_punch.schedule_for(0.5)
            for succeeded in hole_punch.punch_succeeded:
                print('Connected to', address_to_url(succeeded))
                break
            for failed in hole_punch.punch_failed:
                print('Still not connected to', address_to_url(failed))
            print(' ... nothing to retry')
        self.set_endpoint(UDPClientFactory(succeeded, {}, client_address = ('', hole_punch.port)))
        return True

    def ask_server(self):
        endpoint = ServerEndpointFactory()
        hole_punch = HolePunchMechanism(('', endpoint.port))
        stun = StunAddressRequester(('', endpoint.port))
        stun.schedule_for(0.5)
        print('Invite someone?')
        while 1:
            print('start ... to start the game')
            print('b     ... to go back')
            stun.schedule()
            hole_punch.schedule()
            for address in stun.internet_addresses:
                print('Pass "', address_to_url(address), '" to some one to invite.')
            selection = self.input()
            if selection == 'start':
                break
            if selection == 'b':
                return False
            if selection:
                hole_punch.punch_to(selection)
            if hole_punch.punch_failed:
                print('Punching my way to the invited people ...')
                hole_punch.schedule_for(0.5)
            for succeeded in hole_punch.punch_succeeded:
                print('Connected to', address_to_url(succeeded))
            for failed in hole_punch.punch_failed:
                print('Still not connected to', address_to_url(failed))
            print('      ... nothing to retry')
        self.set_endpoint(endpoint)
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
