import random
from typing import List, Tuple
import arcade

from config import WORLD_COLUMNS, WORLD_ROWS


class PlayerWorm:
    def __init__(self):
        self.cells: List[Tuple[int, int]] = []
        self.direction = (1, 0)  # droite
        self.growth_pending = 0
        self.score = 0
        self.alive = True
        self.spleen = 0
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))

    def reset(self, world):
        start_x = random.randint(0, world.columns - 1)
        start_y = random.randint(0, world.rows - 1)
        self.cells = [(start_x, start_y)]
        self.direction = (1, 0)
        self.growth_pending = 0
        self.score = 0
        self.alive = True
        self.spleen = 0
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    
    def die(self, world):
        self.alive = False
        world.spawn_pellets_from_death(self.cells, self.spleen)

    @property
    def head(self) -> Tuple[int, int]:
        return self.cells[0]

    def set_direction_from_key(self, symbol):
        import arcade  # import local pour éviter les cycles
        dx, dy = self.direction

        if symbol == arcade.key.UP and (dx, dy) != (0, -1):
            self.direction = (0, 1)
        elif symbol == arcade.key.DOWN and (dx, dy) != (0, 1):
            self.direction = (0, -1)
        elif symbol == arcade.key.LEFT and (dx, dy) != (1, 0):
            self.direction = (-1, 0)
        elif symbol == arcade.key.RIGHT and (dx, dy) != (-1, 0):
            self.direction = (1, 0)

    def choose_direction(self, world, worms=None):
        pass

    def step(self, world, worms=None):
        """Fait avancer le ver d'une case dans le monde."""
        if not self.alive:
            return

        self.choose_direction(world, worms)

        head_x, head_y = self.head
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Bordures du monde
        if not (0 <= new_head[0] < world.columns and 0 <= new_head[1] < world.rows):
            self.die(world)
            return

        # Collision avec son corps
        if new_head in self.cells:
            self.die(world)
            return
        
        # Collision avec les autres vers
        if worms:
            for worm in worms:
                if worm is not self and worm.alive and new_head in worm.cells:
                    self.die(world)
                    return

        # On avance
        self.cells.insert(0, new_head)

        # Boulettes mangées
        score_delta, growth_delta = world.eat_pellets_at(
            new_head[0], new_head[1], snake_cells=self.cells
        )
        if score_delta > 0:
            self.score += score_delta
            self.growth_pending += growth_delta
            self.spleen += 1

        # Croissance
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.cells.pop()
