import asyncio
from enum import Enum
from time import time
from typing import Dict, List, Optional, Tuple

from fastapi import BackgroundTasks
from pydantic.main import BaseModel
from starlette.websockets import WebSocket

from auth import User


class Player(BaseModel):
    user: User
    websockets: List[WebSocket] = []

    class Config:
        arbitrary_types_allowed = True


class Status(Enum):
    LOBBY = 1
    ANTE = 2
    FLOP = 3
    TURN = 4
    RIVER = 5


class Game:
    game_id: str
    game_code: str
    status: Status
    next_event_time: Optional[float]
    players: Dict[str, Player]

    def __init__(self, game_id: str, game_code: str):
        self.game_id = game_id
        self.game_code = game_code
        self.status = Status.LOBBY
        self.next_event_time = None
        self.players = {}

    def to_json(self):
        next_event_time_delta = None
        if self.next_event_time is not None:
            next_event_time_delta = self.next_event_time - time()

        return {
            "game_id": self.game_id,
            "game_code": self.game_code,
            "status": self.status.name,
            "next_event_time_delta": next_event_time_delta,
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

    async def _start(self, delay: float):
        await asyncio.sleep(delay)
        self.next_event_time = None
        self.status = Status.ANTE
        await self.notify_all()

    async def start(self, delay: float, tasks: BackgroundTasks):
        self.next_event_time = time() + delay
        await self.notify_all()
        tasks.add_task(self._start, delay)
