import asyncio
import base64
import datetime
import random
import string
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException, WebSocket
from pydantic import BaseModel

import auth
import game

app = FastAPI()
api = APIRouter(prefix="/api")
api.include_router(auth.api)
api.include_router(game.api)


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


@api.get("/games")
def list_games():
    return {
        "games": games,
        "current_game_codes": current_game_codes
    }


class NickName(BaseModel):
    nick_name: str


@api.post("/game")
def create_game(nick_name: NickName, user=Depends(auth.get_current_user)):
    print(user)
    print(nick_name)
    game_id = generate_game_id()
    game_code = generate_game_code()

    g = game.Game(game_id, game_code)
    games[game_id] = g
    g.add_player(nick_name.nick_name, user["id"])

    current_game_codes[game_code] = game_id

    return {"game_id": game_id, "game_code": game_code}


class JoinGame(BaseModel):
    nick_name: str
    game_code: str


@api.post("/join")
def join_game(join_game: JoinGame, user=Depends(auth.get_current_user)):
    if join_game.game_code not in current_game_codes:
        raise HTTPException(status_code=404, detail="Game not found")
    game_id = current_game_codes[join_game.game_code]

    game = games[game_id]
    game.add_player(join_game.nick_name, user["id"])

    return {"game_id": game_id, "game_code": join_game.game_code}


@app.websocket("/ws/test")
async def websocket_test(ws: WebSocket):
    await ws.accept()
    end = datetime.datetime.now() + datetime.timedelta(seconds=30)
    while (delta := end - datetime.datetime.now()) > datetime.timedelta():
        await ws.send_json({"timeRemaining": delta.seconds})
        await asyncio.sleep(1)


app.include_router(api)
