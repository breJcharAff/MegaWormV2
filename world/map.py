# world/map.py

import random
from dataclasses import dataclass
from typing import List, Tuple

from config import WORLD_COLUMNS, WORLD_ROWS, INITIAL_PELLET_COUNT, PELLET_TYPES


@dataclass
class Pellet:
    x: int
    y: int
    type_index: int  # index dans PELLET_TYPES


class World:
    def __init__(self):
        self.columns = WORLD_COLUMNS
        self.rows = WORLD_ROWS
        self.pellets: List[Pellet] = []

    def reset(self, snake_cells: List[Tuple[int, int]]):
        """Réinitialise le monde et génère le champ de boulettes."""
        self.pellets.clear()
        for _ in range(INITIAL_PELLET_COUNT):
            self.spawn_pellet(snake_cells)

    def spawn_pellet(self, forbidden_cells: List[Tuple[int, int]]):
        """Place une nouvelle boulette sur une case libre."""
        while True:
            gx = random.randrange(self.columns)
            gy = random.randrange(self.rows)

            if (gx, gy) in forbidden_cells:
                continue
            if any(p.x == gx and p.y == gy for p in self.pellets):
                continue

            type_index = random.randrange(len(PELLET_TYPES))
            self.pellets.append(Pellet(gx, gy, type_index))
            break

    def eat_pellets_at(self, gx: int, gy: int, snake_cells: List[Tuple[int, int]]):
        """Le ver mange les boulettes sur la case (gx, gy). Retourne (score_delta, growth_delta)."""
        eaten = [p for p in self.pellets if p.x == gx and p.y == gy]
        if not eaten:
            return 0, 0

        score_delta = 0
        growth_delta = 0

        for pellet in eaten:
            spec = PELLET_TYPES[pellet.type_index]
            score_delta += spec["score"]
            growth_delta += spec["growth"]
            self.pellets.remove(pellet)

        # On respawn le même nombre de boulettes ailleurs
        for _ in eaten:
            self.spawn_pellet(snake_cells)

        return score_delta, growth_delta

    def spawn_pellets_from_death(self, dead_snake_cells: List[Tuple[int, int]], spleen: int):
        """Fait apparaître des boulettes sur le corps d'un serpent mort."""
        if not dead_snake_cells:
            return

        # Spawn a pellet for every N cells, where N is based on the spleen
        step = max(1, len(dead_snake_cells) // (spleen + 1))
        
        for i in range(0, len(dead_snake_cells), step):
            gx, gy = dead_snake_cells[i]
            if any(p.x == gx and p.y == gy for p in self.pellets):
                continue
            
            type_index = random.randrange(len(PELLET_TYPES))
            self.pellets.append(Pellet(gx, gy, type_index))
