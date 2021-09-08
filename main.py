import asyncio
import base64
import datetime
import random
import string
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, WebSocket
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


class NickName(BaseModel):
    nickName: str


@api.post("/game")
def create_game(nickName: NickName, user=Depends(auth.get_current_user)):
    print(user)
    print(nickName)
    game_id = generate_game_id()
    game_code = generate_game_code()
    return {"game_id": game_id, "game_code": game_code}


@app.websocket("/ws/test")
async def websocket_test(ws: WebSocket):
    await ws.accept()
    end = datetime.datetime.now() + datetime.timedelta(seconds=30)
    while (delta := end - datetime.datetime.now()) > datetime.timedelta():
        await ws.send_json({"timeRemaining": delta.seconds})
        await asyncio.sleep(1)


app.include_router(api)
