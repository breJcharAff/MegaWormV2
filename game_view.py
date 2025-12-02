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
)
from world.map import World
from player.player import PlayerWorm
from player.q_learning_player import QLearningWorm
from player.ai_player import AIWorm


class GameView(arcade.View):
    def __init__(self, player_mode="PLAYER"):
        super().__init__()
        self.player_mode = player_mode

        # Couleur de fond par défaut (au cas où)
        arcade.set_background_color(arcade.color.BLACK)

        # --- Cameras ---
        self.world_camera = arcade.Camera2D()
        self.ui_camera = arcade.Camera2D()

        self.world_camera.match_window()
        self.ui_camera.match_window()

        # --- Game objects ---
        self.world = World()
        self.worms = []

        self.time_since_last_move = 0.0

        self.reset()

    # --- Logique de jeu ---

    def reset(self):
        """Réinitialise la partie."""
        # Save Q-table if the game is restarting
        if self.player_mode == "Q-LEARNING" and self.worms and not self.worms[0].alive:
            self.worms[0].save_q_table()

        self.worms.clear()

        # Create main player
        if self.player_mode == "AI":
            main_worm = AIWorm()
        elif self.player_mode == "Q-LEARNING":
            main_worm = QLearningWorm()
        else:
            main_worm = PlayerWorm()
        self.worms.append(main_worm)

        # Create bots
        for _ in range(NUM_BOTS):
            self.worms.append(AIWorm())

        # Reset worms and world
        all_cells = []
        for worm in self.worms:
            worm.reset(self.world)
            all_cells.extend(worm.cells)

        self.world.reset(all_cells)
        self.time_since_last_move = 0.0
        self.update_camera()

    def on_update(self, delta_time: float):
        # Allow a reset only if the main player is dead
        if not self.worms[0].alive:
            if self.player_mode == "Q-LEARNING":
                self.worms[0].save_q_table()
            return

        self.time_since_last_move += delta_time
        if self.time_since_last_move >= MOVE_INTERVAL:
            self.time_since_last_move = 0.0
            
            # Create a list of all worm cells for collision detection
            all_worm_cells = []
            for worm in self.worms:
                if worm.alive:
                    all_worm_cells.extend(worm.cells)

            # Update each worm
            for worm in self.worms:
                if worm.alive:
                    worm.step(self.world, self.worms)
            
            self.update_camera()

    def update_camera(self):
        """Centre la caméra sur la tête du ver, en restant dans les bordures du monde."""
        main_player = self.worms[0]
        head_gx, head_gy = main_player.head
        head_x = head_gx * GRID_SIZE + GRID_SIZE / 2
        head_y = head_gy * GRID_SIZE + GRID_SIZE / 2

        # Taille de la zone visible par la caméra (en unités monde)
        half_w = self.world_camera.width / 2
        half_h = self.world_camera.height / 2

        # On évite que la caméra sorte de la map
        min_x = half_w
        max_x = WORLD_WIDTH - half_w
        min_y = half_h
        max_y = WORLD_HEIGHT - half_h

        # Si le monde est plus petit que la vue, on évite les inversions
        if min_x > max_x:
            x = WORLD_WIDTH / 2
        else:
            x = min(max(head_x, min_x), max_x)

        if min_y > max_y:
            y = WORLD_HEIGHT / 2
        else:
            y = min(max(head_y, min_y), max_y)

        self.world_camera.position = (x, y)

    # --- Rendu ---

    def on_draw(self):
        self.clear()

        # --- Pass monde (caméra qui suit le ver) ---
        self.world_camera.use()
        self.draw_background()
        self.draw_pellets()
        self.draw_worms()

        # --- Pass UI (coordonnées écran fixes) ---
        self.ui_camera.use()
        self.draw_ui()

    def draw_background(self):
        """
        Fond type "espace" simple :
        - grand rectangle sombre
        - petits points plus clairs pour éviter le fond noir monotone
        """

        # Fond global
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            WORLD_WIDTH,
            WORLD_HEIGHT,
            (5, 5, 15),  # bleu nuit très sombre
        )

        # "étoiles" / points pour donner un léger motif
        step = GRID_SIZE * 4
        for x in range(0, WORLD_WIDTH, step):
            for y in range(0, WORLD_HEIGHT, step):
                arcade.draw_circle_filled(
                    x + GRID_SIZE // 2,
                    y + GRID_SIZE // 2,
                    1.5,
                    (35, 35, 70),
                )

    def draw_pellets(self):
        """Dessine les boulettes (sans textures, uniquement en cercles colorés)."""
        for pellet in self.world.pellets:
            px = pellet.x * GRID_SIZE + GRID_SIZE / 2
            py = pellet.y * GRID_SIZE + GRID_SIZE / 2

            spec = PELLET_TYPES[pellet.type_index]
            radius = spec.get("radius", GRID_SIZE // 3)
            color = spec.get("color", arcade.color.YELLOW)

            arcade.draw_circle_filled(px, py, radius, color)

    def draw_worms(self):
        """Dessine le ver comme une série de cercles (tête + segments)."""
        for worm in self.worms:
            if not worm.alive:
                continue
            
            for i, (gx, gy) in enumerate(worm.cells):
                cx = gx * GRID_SIZE + GRID_SIZE / 2
                cy = gy * GRID_SIZE + GRID_SIZE / 2

                if i == 0:
                    radius = GRID_SIZE * 0.55
                else:
                    radius = GRID_SIZE * 0.48

                arcade.draw_circle_filled(cx, cy, radius, worm.color)

    def draw_ui(self):
        """HUD fixe en coordonnées écran (score + message game over)."""
        main_player = self.worms[0]
        arcade.draw_text(
            f"Score : {main_player.score}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            16,
        )

        if not main_player.alive:
            arcade.draw_text(
                "GAME OVER - Espace pour recommencer",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.WHITE,
                20,
                anchor_x="center",
                anchor_y="center",
            )

    # --- Input ---

    def on_key_press(self, symbol, modifiers):
        import arcade as _a

        if self.player_mode == "PLAYER":
            if symbol in (_a.key.UP, _a.key.DOWN, _a.key.LEFT, _a.key.RIGHT):
                self.worms[0].set_direction_from_key(symbol)
        
        if symbol == _a.key.SPACE and not self.worms[0].alive:
            self.reset()

    def on_close(self):
        """Save Q-table on window close."""
        if self.player_mode == "Q-LEARNING" and self.worms:
            self.worms[0].save_q_table()
        super().on_close()

