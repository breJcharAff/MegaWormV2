# game_view.py

import arcade

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRID_SIZE,
    MOVE_INTERVAL,
    WORLD_WIDTH,
    WORLD_HEIGHT,
    PELLET_TYPES,
    NUM_BOTS,
    SMALL_WORLD_COLUMNS,
    SMALL_WORLD_ROWS,
    SMALL_INITIAL_PELLET_COUNT,
)
from world.map import World
from player.player import PlayerWorm
from player.q_learning_player import QLearningWorm
from player.ai_player import AIWorm


class GameView(arcade.View):
    def __init__(self, player_mode="PLAYER"):
        super().__init__()
        self.player_mode = player_mode

        arcade.set_background_color(arcade.color.BLACK)

        self.world_camera = arcade.Camera2D()
        self.ui_camera = arcade.Camera2D()
        self.world_camera.match_window()
        self.ui_camera.match_window()

        if self.player_mode == "Q-LEARNING-SOLO":
            self.world = World(
                columns=SMALL_WORLD_COLUMNS,
                rows=SMALL_WORLD_ROWS,
                initial_pellet_count=SMALL_INITIAL_PELLET_COUNT,
            )
        else:
            self.world = World()
        
        self.worms = []
        self.time_since_last_move = 0.0

        self.game_number = 0
        self.score_history = []
        self.restart_timer = 0.0
        
        self.reset()

    def reset(self):
        if self.worms and not self.worms[0].alive:
            self.game_number += 1
            if "Q-LEARNING" in self.player_mode:
                self.score_history.append(self.worms[0].score)
                if len(self.score_history) > 100:
                    self.score_history.pop(0)

        self.worms.clear()

        # Create main player
        if self.player_mode == "AI":
            main_worm = AIWorm()
        elif "Q-LEARNING" in self.player_mode:
            main_worm = QLearningWorm()
        else:
            main_worm = PlayerWorm()
        self.worms.append(main_worm)

        if self.player_mode != "Q-LEARNING-SOLO":
            for _ in range(NUM_BOTS):
                self.worms.append(AIWorm())

        all_cells = []
        for worm in self.worms:
            worm.reset(self.world)
            all_cells.extend(worm.cells)

        self.world.reset(all_cells)
        self.time_since_last_move = 0.0
        self.restart_timer = 0.0
        self.update_camera()

    def on_update(self, delta_time: float):
        if not self.worms[0].alive:
            if self.player_mode == "Q-LEARNING-SOLO":
                self.restart_timer += delta_time
                if self.restart_timer > 1.0:
                    if "Q-LEARNING" in self.player_mode and self.worms:
                        self.worms[0].save_q_table()
                    self.reset()
            return

        self.time_since_last_move += delta_time
        if self.time_since_last_move >= MOVE_INTERVAL:
            self.time_since_last_move = 0.0
            
            for worm in self.worms:
                if worm.alive:
                    worm.step(self.world, self.worms)
            
            self.update_camera()

    def update_camera(self):
        main_player = self.worms[0]
        head_gx, head_gy = main_player.head
        head_x = head_gx * GRID_SIZE + GRID_SIZE / 2
        head_y = head_gy * GRID_SIZE + GRID_SIZE / 2

        half_w = self.world_camera.width / 2
        half_h = self.world_camera.height / 2
        
        world_width = self.world.columns * GRID_SIZE
        world_height = self.world.rows * GRID_SIZE

        min_x = half_w
        max_x = world_width - half_w
        min_y = half_h
        max_y = world_height - half_h

        if min_x > max_x:
            x = world_width / 2
        else:
            x = min(max(head_x, min_x), max_x)

        if min_y > max_y:
            y = world_height / 2
        else:
            y = min(max(head_y, min_y), max_y)

        self.world_camera.position = (x, y)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.draw_background()
        self.draw_pellets()
        self.draw_worms()
        self.ui_camera.use()
        self.draw_ui()

    def draw_background(self):
        world_width = self.world.columns * GRID_SIZE
        world_height = self.world.rows * GRID_SIZE
        arcade.draw_lbwh_rectangle_filled(0, 0, world_width, world_height, (5, 5, 15))
        
        step = GRID_SIZE * 4
        for x in range(0, int(world_width), step):
            for y in range(0, int(world_height), step):
                arcade.draw_circle_filled(x + GRID_SIZE // 2, y + GRID_SIZE // 2, 1.5, (35, 35, 70))

    def draw_pellets(self):
        for pellet in self.world.pellets:
            px = pellet.x * GRID_SIZE + GRID_SIZE / 2
            py = pellet.y * GRID_SIZE + GRID_SIZE / 2
            spec = PELLET_TYPES[pellet.type_index]
            radius = spec.get("radius", GRID_SIZE // 3)
            color = spec.get("color", arcade.color.YELLOW)
            arcade.draw_circle_filled(px, py, radius, color)

    def draw_worms(self):
        for worm in self.worms:
            if not worm.alive:
                continue
            
            for i, (gx, gy) in enumerate(worm.cells):
                cx = gx * GRID_SIZE + GRID_SIZE / 2
                cy = gy * GRID_SIZE + GRID_SIZE / 2
                radius = GRID_SIZE * 0.55 if i == 0 else GRID_SIZE * 0.48
                arcade.draw_circle_filled(cx, cy, radius, worm.color)

    def draw_ui(self):
        main_player = self.worms[0]
        arcade.draw_text(f"Score : {main_player.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)

        if "Q-LEARNING" in self.player_mode:
            avg_score = sum(self.score_history) / len(self.score_history) if self.score_history else 0
            arcade.draw_text(f"Game: {self.game_number}", 10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)
            arcade.draw_text(f"Epsilon: {main_player.epsilon:.3f}", 10, SCREEN_HEIGHT - 90, arcade.color.WHITE, 16)
            arcade.draw_text(f"Q-table size: {main_player.q_table_size}", 10, SCREEN_HEIGHT - 120, arcade.color.WHITE, 16)
            arcade.draw_text(f"Avg Score (last 100): {avg_score:.2f}", 10, SCREEN_HEIGHT - 150, arcade.color.WHITE, 16)

        if not main_player.alive:
            # In solo mode, don't show the restart message, as it's automatic
            if self.player_mode != "Q-LEARNING-SOLO":
                arcade.draw_text("GAME OVER - Espace pour recommencer", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")
            else:
                arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")


    def on_key_press(self, symbol, modifiers):
        import arcade as _a
        if self.player_mode == "PLAYER":
            if symbol in (_a.key.UP, _a.key.DOWN, _a.key.LEFT, _a.key.RIGHT):
                self.worms[0].set_direction_from_key(symbol)
        
        if self.player_mode != "Q-LEARNING-SOLO":
            if symbol == _a.key.SPACE and not self.worms[0].alive:
                if "Q-LEARNING" in self.player_mode and self.worms:
                    self.worms[0].save_q_table()
                self.reset()
			
    def on_hide_view(self):
        if "Q-LEARNING" in self.player_mode and self.worms:
            self.worms[0].save_q_table()


