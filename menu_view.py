import arcade
import arcade.gui

from game_view import GameView

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        ai_button = arcade.gui.UIFlatButton(text="IA basique", width=200)
        self.v_box.add(ai_button)

        player_button = arcade.gui.UIFlatButton(text="Jouer", width=200)
        self.v_box.add(player_button)

        q_learning_button = arcade.gui.UIFlatButton(text="Entrainer Q-learning", width=200)
        self.v_box.add(q_learning_button)

        ai_button.on_click = self.on_click_ai
        player_button.on_click = self.on_click_player
        q_learning_button.on_click = self.on_click_q_learning

        self.manager.add(
            arcade.gui.UIAnchorLayout(
                anchor_x="center_x",
                anchor_y="center_y",
                children=[self.v_box])
        )

    def on_click_ai(self, event):
        game_view = GameView("AI")
        self.window.show_view(game_view)

    def on_click_player(self, event):
        game_view = GameView("PLAYER")
        self.window.show_view(game_view)

    def on_click_q_learning(self, event):
        game_view = GameView("Q-LEARNING")
        self.window.show_view(game_view)

    def on_draw(self):
        self.clear()
        self.manager.draw()
