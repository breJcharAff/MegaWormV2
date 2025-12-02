import numpy as np
import random
import os
from .player import PlayerWorm

class QLearningWorm(PlayerWorm):
    def __init__(self, q_table_path="q_table.npy"):
        super().__init__()
        self.q_table_path = q_table_path
        self.q_table = self.load_q_table()
        
        # Hyperparameters
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.1  # Exploration rate

        self.last_state = None
        self.last_action = None
        self.last_score = 0

    def load_q_table(self):
        if os.path.exists(self.q_table_path):
            return np.load(self.q_table_path, allow_pickle=True).item()
        return {}

    def save_q_table(self):
        np.save(self.q_table_path, self.q_table)

    def get_state(self, world, worms):
        head_x, head_y = self.head

        # 1. Food direction
        target_pellet = None
        min_dist = float('inf')
        for pellet in world.pellets:
            dist = abs(head_x - pellet.x) + abs(head_y - pellet.y)
            if dist < min_dist:
                min_dist = dist
                target_pellet = pellet
        
        food_dir_x = 0
        food_dir_y = 0
        if target_pellet:
            if target_pellet.x > head_x: food_dir_x = 1
            elif target_pellet.x < head_x: food_dir_x = -1
            if target_pellet.y > head_y: food_dir_y = 1
            elif target_pellet.y < head_y: food_dir_y = -1
        
        # 2. Dangers
        dangers = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]: # up, down, right, left
            x, y = head_x + dx, head_y + dy
            is_wall = not (0 <= x < world.columns and 0 <= y < world.rows)
            is_body = (x, y) in self.cells
            is_other_worm = False
            if worms:
                for worm in worms:
                    if worm is not self and (x, y) in worm.cells:
                        is_other_worm = True
                        break
            dangers.append(1 if is_wall or is_body or is_other_worm else 0)

        return (food_dir_x, food_dir_y, *dangers)

    def choose_direction(self, world, worms=None):
        state = self.get_state(world, worms)
        
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in [(0, 1), (0, -1), (1, 0), (-1, 0)]}

        if random.uniform(0, 1) < self.epsilon:
            action = random.choice(list(self.q_table[state].keys()))
        else:
            action = max(self.q_table[state], key=self.q_table[state].get)

        self.direction = action
        self.last_state = state
        self.last_action = action
    
    def update_q_table(self, reward, new_state):
        if self.last_state is None or self.last_action is None:
            return

        old_value = self.q_table[self.last_state][self.last_action]
        
        if new_state not in self.q_table:
            self.q_table[new_state] = {a: 0 for a in [(0, 1), (0, -1), (1, 0), (-1, 0)]}
            
        next_max = max(self.q_table[new_state].values())

        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[self.last_state][self.last_action] = new_value

    def get_reward(self, world):
        reward = 0
        if not self.alive:
            reward = -100  # Died
            return reward
        
        if self.score > self.last_score:
            reward = 10  # Ate food
        else:
            # Getting closer or further from food
            # This is a bit tricky, let's keep it simple for now
            # and just give a small penalty for surviving to encourage speed
            reward = -0.1
            
        self.last_score = self.score
        return reward

    def step(self, world, worms=None):
        # Store distance before moving
        # This is a bit of a hack, but let's try to reward getting closer to food
        target_pellet = None
        min_dist_before = float('inf')
        if world.pellets:
            min_dist_before = min(abs(self.head[0] - p.x) + abs(self.head[1] - p.y) for p in world.pellets)

        super().step(world, worms)
        
        # Get reward and new state, and update Q-table
        reward = self.get_reward(world)

        # Add reward for getting closer to food
        if self.alive and world.pellets:
            min_dist_after = min(abs(self.head[0] - p.x) + abs(self.head[1] - p.y) for p in world.pellets)
            if min_dist_after < min_dist_before:
                reward += 1
            else:
                reward -= 1.5

        new_state = self.get_state(world, worms)
        self.update_q_table(reward, new_state)

    def reset(self, world):
        super().reset(world)
        self.last_state = None
        self.last_action = None
        self.last_score = 0
