

class GameNetwork:

    
    def create_game(self, dedicated = False, internet = True):
        pass

    def create_client(self):
        pass


class OfficialClientInterface:

    @property
    def game(self):
        "=> OfficialGameInterface"
        pass

class GameClient(OfficialClientInterface):

    def connect_to_server(self, url):
        pass

    @property
    def other_clients(self):
        "=> OfficialClientInterface"
        pass

class OfficialGameInterface:


class Player:

    def is_me(self):
        pass


class OfficialGameServerInterface:

    @property
    def informtation_for_clients(self):
        pass

    def get_urls(self, internet = True):
        pass
    

class GameServer(OfficialGameServerInterface):

    def start(self):
        pass

    def stop(self):
        pass

    def create_client(self):
        pass
