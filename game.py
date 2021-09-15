class Game:
    def __init__(self, game_id, game_code):
        self.game_id = game_id
        self.game_code = game_code
        self.players = {}
    
    def add_player(self, name, id):
        self.players[name] = id
