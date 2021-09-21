import asyncio
import base64
import datetime
import random
import string
import uuid

from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocket
from pydantic import BaseModel

import auth
from game import Game

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
def create_game(req: CreateGame, user=Depends(auth.get_current_user)) -> GetGame:
    print(user)
    print(req)
    game_id = generate_game_id()
    game_code = generate_game_code()

    game = Game(game_id, game_code)
    games[game_id] = game
    game.add_player(req.nick_name, user["id"])

    current_game_codes[game_code] = game_id

    return GetGame(game_id=game_id, game_code=game_code)


@api.patch("/games", response_model=GetGame)
def join_game(req: JoinGame, user=Depends(auth.get_current_user)) -> GetGame:
    if req.game_code not in current_game_codes:
        raise HTTPException(status_code=404, detail="Game not found")
    game_id = current_game_codes[req.game_code]

    #TODO: Don't allow a user to join a game they're already a member of.

    game = games[game_id]
    game.add_player(req.nick_name, user["id"])

    return GetGame(game_id=game_id, game_code=req.game_code)


@api.get("/games")
def list_games():
    return {
        "games": games,
        "current_game_codes": current_game_codes
    }


@api.get("/games/{game_id}")
def get_game(game_id: str, user=Depends(auth.get_current_user)):
    return games[game_id]


@app.websocket("/ws/test")
async def websocket_test(ws: WebSocket):
    await ws.accept()
    end = datetime.datetime.now() + datetime.timedelta(seconds=30)
    while (delta := end - datetime.datetime.now()) > datetime.timedelta():
        await ws.send_json({"timeRemaining": delta.seconds})
        await asyncio.sleep(1)


app.include_router(api)
