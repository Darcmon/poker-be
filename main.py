import asyncio
import base64
import random
import string
import uuid

from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocket
from pydantic import BaseModel

import auth
from auth import User, get_current_user
from game import Avatar, Game, Player

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

games = {}
current_game_codes = {}


class CreateGame(BaseModel):
    nick_name: str


class JoinGame(BaseModel):
    nick_name: str
    game_code: str


class GetGame(BaseModel):
    game_id: str
    game_code: str


@api.post("/games", response_model=GetGame)
async def create_game(
    req: CreateGame, user: User = Depends(get_current_user)
) -> GetGame:
    print(user)
    print(req)
    game_id = generate_game_id()
    game_code = generate_game_code()

    game = Game(game_id, game_code)
    games[game_id] = game
    game.add_player(Player(avatar=Avatar(name=req.nick_name), user=user))

    current_game_codes[game_code] = game_id

    return GetGame(game_id=game_id, game_code=game_code)


@api.patch("/games", response_model=GetGame)
def join_game(req: JoinGame, user: User = Depends(get_current_user)) -> GetGame:
    if req.game_code not in current_game_codes:
        raise HTTPException(status_code=404, detail="Game not found")
    game_id = current_game_codes[req.game_code]

    # TODO: Don't allow a user to join a game they're already a member of.

    game = games[game_id]
    game.add_player(Player(avatar=Avatar(name=req.nick_name), user=user))

    return GetGame(game_id=game_id, game_code=req.game_code)


@api.get("/games")
def list_games():
    return {"games": games, "current_game_codes": current_game_codes}


@api.get("/games/{game_id}")
def get_game(game_id: str, user=Depends(auth.get_current_user)):
    return games[game_id].to_json()


@app.websocket("/ws/games/{game_id}")
async def game_status(ws: WebSocket, game_id: str):
    await ws.accept()
    game = games[game_id]
    while True:
        await ws.send_json(game.to_json())
        await asyncio.sleep(1)


app.include_router(api)
