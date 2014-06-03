
class Gamer:


    # auto connect to game network


class GameNetwork:

    @property
    def is_in_internet(self):
        pass

    @property
    def open_games(self):
        pass # => [GameInformation]

    @property
    def available_games(self):
        pass # => [GameInformation]

    def connect_to(self, url):
        pass

    @property
    def open_game(self):
        pass# => Game

    def find_client(self, public_key):
        pass

class Client:

    @property
    def display_name(self):
        pass

    @property
    def game_information(self):
        pass # => [GameInformation]

    def urls(self):
        pass

    def public_key(self):
        pass

    @property
    def friends(self):
        pass

class GameInformation:

    def number_of_joint_players(self):
        pass

    def join(self):
        pass # => Game

class Game:

    @property
    def urls(self):
        pass

    @property
    def joint_clients(self):
        pass

    def own_client(self):
        # element of joint_clients
        pass

    @property
    def state(self):
        pass

    @property
    def time(self):
        pass

    @property
    def start(self):
        pass

    @property
    def timed_out(self):
        pass

    @property
    def timeout(self):
        return 60

class JointClient(Client):
    # has synchronized game state

    @property
    def ping(self):
        pass

    def timed_out(self):
        pass

    def name(self):
        pass

class OwnClient(JointClient):

    def leave_game(self):
        pass



        
class GameTime:

    def start(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def slow_down(self, multiplier):
        pass


    


