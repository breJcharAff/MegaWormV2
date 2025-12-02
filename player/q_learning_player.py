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
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.05

        self.last_state = None
        self.last_action = None
        self.last_score = 0

    @property
    def q_table_size(self):
        return len(self.q_table)

    def load_q_table(self):
        if os.path.exists(self.q_table_path):
            q_table = np.load(self.q_table_path, allow_pickle=True).item()
            # Load epsilon from q_table if it exists
            if 'epsilon' in q_table:
                self.epsilon = q_table['epsilon']
                del q_table['epsilon'] # remove it to not interfere with state keys
            return q_table
        return {}

    def save_q_table(self):
        # Save epsilon along with the q_table
        self.q_table['epsilon'] = self.epsilon
        np.save(self.q_table_path, self.q_table)

    def get_state(self, world, worms):
        head_x, head_y = self.head
        
        # 1. Food Radar (10-cell radius)
        target_pellet = None
        min_dist = 10
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

        # 2. Granular Dangers
        dangers = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]: # up, down, right, left
            x, y = head_x + dx, head_y + dy
            
            danger = 0 # 0: no danger
            if not (0 <= x < world.columns and 0 <= y < world.rows):
                danger = 1 # 1: wall
            elif (x, y) in self.cells:
                danger = 2 # 2: own body
            elif worms:
                for worm in worms:
                    if worm is not self and worm.alive and (x, y) in worm.cells:
                        danger = 3 # 3: other worm
                        break
            dangers.append(danger)

        return (food_dir_x, food_dir_y, *dangers)

    def choose_direction(self, world, worms=None):
        state = self.get_state(world, worms)
        
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in [(0, 1), (0, -1), (1, 0), (-1, 0)]}

        # Filter out the reverse action
        possible_actions = list(self.q_table[state].keys())
        reverse_action = (-self.direction[0], -self.direction[1])
        if reverse_action in possible_actions and len(self.cells) > 1:
            possible_actions.remove(reverse_action)

        if random.uniform(0, 1) < self.epsilon:
            action = random.choice(possible_actions)
        else:
            # Create a dictionary with only the possible actions
            q_values = {a: self.q_table[state][a] for a in possible_actions}
            action = max(q_values, key=q_values.get)

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
        
        # Epsilon decay
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

