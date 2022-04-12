import base64
import random
import string
import uuid
from typing import Dict

from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocket
from fastapi.logger import logger
from pydantic import BaseModel
from starlette.websockets import WebSocketState

import auth
from auth import User, bearer_user, query_user
from game import Game, Player

app = FastAPI()
api = APIRouter(prefix="/api")
api.include_router(auth.api)


def generate_game_id():
    game_id = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return game_id.decode("utf-8").replace("=", "")


def generate_game_code():
    return "".join(random.choice(string.ascii_uppercase) for _ in range(4))


# Things we need:
# - A mapping between the game code and the game ID.
# - Which players are participating in a given game.
# - A mapping between the player's nickname and their user ID.

games: Dict[str, Game] = {}
current_game_codes: Dict[str, str] = {}


class CreateGame(BaseModel):
    pass


class JoinGame(BaseModel):
    game_code: str


class GetGame(BaseModel):
    game_id: str
    game_code: str


@api.post("/games", response_model=GetGame)
async def create_game(req: CreateGame, user: User = Depends(bearer_user)) -> GetGame:
    game_id = generate_game_id()
    game_code = generate_game_code()

    game = Game(game_id, game_code)
    games[game_id] = game
    await game.add_player(Player(user=user))

    current_game_codes[game_code] = game_id

    return GetGame(game_id=game_id, game_code=game_code)


@api.patch("/games", response_model=GetGame)
async def join_game(req: JoinGame, user: User = Depends(bearer_user)) -> GetGame:
    if req.game_code not in current_game_codes:
        raise HTTPException(status_code=404, detail="Game not found")

    game_id = current_game_codes[req.game_code]
    game = games[game_id]

    if not game.is_player(user):
        await game.add_player(Player(user=user))

    return GetGame(game_id=game_id, game_code=req.game_code)


@api.post("/games/{game_id}/start")
def start_game(game_id: str, user: User = Depends(bearer_user)):
    game = games[game_id]
    if not game.is_player(user):
        raise HTTPException(status_code=403, detail="User has not joined the game")
    game.start(5)
    return game.to_json()


@api.get("/games")
def list_games():
    # TODO: Add games back to the list of games response.
    return {"current_game_codes": current_game_codes}


@api.get("/games/{game_id}")
def get_game(game_id: str, user=Depends(bearer_user)):
    return games[game_id].to_json()


@app.websocket("/ws/games/{game_id}")
async def game_status(ws: WebSocket, game_id: str, user: User = Depends(query_user)):
    await ws.accept()

    if game_id not in games:
        await ws.send_json({"detail": "Game not found"})
        return

    game = games[game_id]
    game.add_websocket(ws, user)
    await game.notify(ws, user)
    print(f"Connected: {user.email} {game_id}")
    try:
        while ws.client_state == WebSocketState.CONNECTED:
            await ws.receive()
    finally:
        game.remove_websocket(ws, user)
        print(f"Disconnected: {user.email} {game_id}")


app.include_router(api)
