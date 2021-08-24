import asyncio
import base64
import datetime
import itertools
import random
import string
import uuid
from typing import Optional

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse


def generate_deck_of_cards():
    values = list(range(1, 14))
    suits = ["D", "C", "H", "S"]
    cards = list(itertools.product(values, suits))
    random.shuffle(cards)
    return cards


app = FastAPI()

## Poker Game State in JSON

state = {
    "cards": generate_deck_of_cards(),
    "players": [
        {
            "first_name": "Shad",
            "last_name": "Sharma",
            "email": "shadanan@gmail.com",
            "pool": 500,
            "state": 0,  # 0: fold, 1: call, 2: raise
            "bet": 200,
        },
        {
            "first_name": "Sachie",
            "last_name": "Sharma",
            "email": "sachie@gmail.com",
            "pool": 50,
            "state": 1,  # 0: fold, 1: call, 2: raise
            "bet": 50,
        },
        {
            "first_name": "Richard",
            "last_name": "Ngo",
            "email": "richard1ngo@gmail.com",
            "pool": 500,
            "state": 2,  # 0: fold, 1: call, 2: raise
            "bet": 200,
        },
        {
            "first_name": "Niwako",
            "last_name": "Sugimura",
            "email": "niwako@gmail.com",
            "pool": 500,
            "state": 1,  # 0: fold, 1: call, 2: raise
            "bet": 6,
        },
    ],
    "dealer": 0,  ## Index into players
    "bet_size": 2,
    "turn": 3,  # 0: ante, 1: flop, 2: turn, 3: river
    "round": 0,
}


@app.get("/api/state")
def get_state():
    return state


@app.get("/api/{user}/state")
def get_user_state(user):
    if user == "shad":
        return {"cards": [state["cards"][0], state["cards"][0 + len(state["players"])]]}
    elif user == "sach":
        return {"cards": [state["cards"][1], state["cards"][1 + len(state["players"])]]}


@app.post("/api/game")
def create_game():
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


def generate_game_id():
    game_id = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return game_id.decode("utf-8").replace("=", "")


def generate_game_code():
    return "".join(random.choice(string.ascii_uppercase) for _ in range(4))
