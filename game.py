from typing import List

from pydantic.main import BaseModel

from auth import User


class Avatar(BaseModel):
    name: str


class Player(BaseModel):
    user: User
    avatar: Avatar


class GameState(BaseModel):
    game_id: str
    game_code: str
    players: List[Player]


class Game:
    def __init__(self, game_id: str, game_code: str):
        self.game_id = game_id
        self.game_code = game_code
        self.players: List[Player] = []

    def to_json(self):
        return {
            "game_id": self.game_id,
            "game_code": self.game_code,
            "players": [p.avatar.name for p in self.players],
        }

    def add_player(self, player: Player):
        self.players.append(player)
