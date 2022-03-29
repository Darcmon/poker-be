import asyncio
from typing import Dict, List, Tuple

from pydantic.main import BaseModel
from starlette.websockets import WebSocket

from auth import User


class Player(BaseModel):
    user: User
    websockets: List[WebSocket] = []

    class Config:
        arbitrary_types_allowed = True


class Game:
    def __init__(self, game_id: str, game_code: str):
        self.game_id = game_id
        self.game_code = game_code
        self.players: Dict[str, Player] = {}

    def to_json(self):
        return {
            "game_id": self.game_id,
            "game_code": self.game_code,
            "players": [p.user.name for p in self.players.values()],
        }

    def add_websocket(self, ws: WebSocket, user: User):
        self.players[user.id].websockets.append(ws)

    def remove_websocket(self, ws: WebSocket, user: User):
        self.players[user.id].websockets.remove(ws)

    async def notify(self, ws: WebSocket, user: User):
        await ws.send_json(self.to_json())

    async def notify_all(self):
        coros = [
            self.notify(ws, player.user)
            for player in self.players.values()
            for ws in player.websockets
        ]
        await asyncio.gather(*coros, return_exceptions=True)

    async def add_player(self, player: Player):
        self.players[player.user.id] = player
        await self.notify_all()

    def is_player(self, user: User):
        return user.id in self.players
