from .player import PlayerWorm
import random

class AIWorm(PlayerWorm):
    """
    A worm controlled by a simple AI.
    The AI will try to avoid walls and its own body.
    """

    def __init__(self):
        super().__init__()

    def choose_direction(self, world, worms=None):
        """Chooses the next direction to avoid walls, self-collision and seek food."""
        head_x, head_y = self.head
        
        # --- Collision avoidance ---
        possible_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if self.direction in possible_directions:
             possible_directions.remove((-self.direction[0], -self.direction[1]))

        safe_moves = []
        for move_dir in possible_directions:
            dx, dy = move_dir
            new_head = (head_x + dx, head_y + dy)

            is_wall = not (0 <= new_head[0] < world.columns and 0 <= new_head[1] < world.rows)
            is_body = new_head in self.cells
            
            is_other_worm = False
            if worms:
                for worm in worms:
                    if worm is not self and new_head in worm.cells:
                        is_other_worm = True
                        break

            if not is_wall and not is_body and not is_other_worm:
                safe_moves.append(move_dir)

        if not safe_moves:
            return

        # --- Food seeking ---
        target_pellet = None
        min_dist = float('inf')
        for pellet in world.pellets:
            dist = abs(head_x - pellet.x) + abs(head_y - pellet.y)
            if dist < min_dist:
                min_dist = dist
                target_pellet = pellet

        best_move = None
        if target_pellet:
            # Determine preferred direction
            if target_pellet.x > head_x:
                preferred_move_h = (1, 0)
            elif target_pellet.x < head_x:
                preferred_move_h = (-1, 0)
            else:
                preferred_move_h = None

            if target_pellet.y > head_y:
                preferred_move_v = (0, 1)
            elif target_pellet.y < head_y:
                preferred_move_v = (0, -1)
            else:
                preferred_move_v = None

            # Try to move towards the pellet
            if preferred_move_h and preferred_move_h in safe_moves:
                best_move = preferred_move_h
            elif preferred_move_v and preferred_move_v in safe_moves:
                best_move = preferred_move_v
        
        # --- Decision ---
        if best_move:
            self.direction = best_move
        else:
            # Fallback to random safe move
            if self.direction in safe_moves:
                if len(safe_moves) > 1 and random.random() < 0.2:
                    safe_moves.remove(self.direction)
                    self.direction = random.choice(safe_moves)
                else:
                    pass # Stay
            else:
                self.direction = random.choice(safe_moves)
