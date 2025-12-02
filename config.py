# config.py

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Slither RL - Arcade"

GRID_SIZE = 20

WORLD_COLUMNS = 200
WORLD_ROWS = 200
WORLD_WIDTH = WORLD_COLUMNS * GRID_SIZE
WORLD_HEIGHT = WORLD_ROWS * GRID_SIZE

MOVE_INTERVAL = 0.05

INITIAL_PELLET_COUNT = 200
NUM_BOTS = 5

SMALL_WORLD_COLUMNS = 30
SMALL_WORLD_ROWS = 30
SMALL_INITIAL_PELLET_COUNT = 20

# Assets intégrés d'Arcade (coins)
# cf. :resources:images/items/coinBronze.png / coinSilver.png / coinGold.png
PELLET_TYPES = [
    {
        "score": 1,
        "growth": 1,
        "texture": ":resources:images/items/coinBronze.png",
    },
    {
        "score": 2,
        "growth": 2,
        "texture": ":resources:images/items/coinSilver.png",
    },
    {
        "score": 3,
        "growth": 3,
        "texture": ":resources:images/items/coinGold.png",
    },
]
