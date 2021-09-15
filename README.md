# Run Locally

1. Create and activate a new virtual environment.

   ```shell
   $ python3 -m venv .venv
   $ . .venv/bin/activate
   ```

1. Install dependencies.

   ```shell
   $ pip install -r requirements.txt
   ```

1. Launch the development server.

   ```shell
   $ uvicorn main:app --reload
   ```

## Example Game State

```python

def generate_deck_of_cards():
    values = list(range(1, 14))
    suits = ["D", "C", "H", "S"]
    cards = list(itertools.product(values, suits))
    random.shuffle(cards)
    return cards

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
```
