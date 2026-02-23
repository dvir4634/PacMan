import arcade
import random

# =====================
# קבועים
# =====================
TILE_SIZE = 40
SCREEN_WIDTH = 11 * TILE_SIZE
SCREEN_HEIGHT = 4 * TILE_SIZE
SCREEN_TITLE = "Arcade Pacman"

PLAYER_SPEED = 3
ENEMY_SPEED = 2

LEVEL_MAP = [
    "###########",
    "#P....G...#",
    "#.........#",
    "###########",
]

# =====================
# מחלקות
# =====================
class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_circle_texture(15, arcade.color.YELLOW)
        self.center_x = x
        self.center_y = y
        self.start_x = x
        self.start_y = y
        self.score = 0
        self.lives = 3


class Enemy(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_circle_texture(15, arcade.color.RED)
        self.center_x = x
        self.center_y = y
        self.change_x = ENEMY_SPEED
        self.change_y = 0

    def pick_new_direction(self):
        directions = [
            (ENEMY_SPEED, 0),
            (-ENEMY_SPEED, 0),
            (0, ENEMY_SPEED),
            (0, -ENEMY_SPEED),
        ]
        self.change_x, self.change_y = random.choice(directions)


class Coin(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_circle_texture(8, arcade.color.GOLD)
        self.center_x = x
        self.center_y = y
        self.value = 10


# =====================
# משחק
# =====================
class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        self.player = None
        self.physics_engine = None

        self.game_state = "PLAYING"  # אפשרויות: PLAYING, GAME_OVER, WIN

    def setup(self):
        # מחיקות של רשימות קיימות (במקרה של Restart)
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.player = None

        for row_i, row in enumerate(reversed(LEVEL_MAP)):
            for col_i, cell in enumerate(row):

                x = col_i * TILE_SIZE + TILE_SIZE // 2
                y = row_i * TILE_SIZE + TILE_SIZE // 2

                if cell == "#":
                    wall = arcade.SpriteSolidColor(
                        TILE_SIZE, TILE_SIZE, arcade.color.BLUE
                    )
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)

                elif cell == ".":
                    self.coin_list.append(Coin(x, y))

                elif cell == "P":
                    self.player = Player(x, y)
                    self.player_list.append(self.player)

                elif cell == "G":
                    self.enemy_list.append(Enemy(x, y))

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list
        )

        self.game_state = "PLAYING"

    def on_draw(self):
        self.clear()  # שימוש נכון במקום start_render

        if self.game_state == "PLAYING":
            self.wall_list.draw()
            self.coin_list.draw()
            self.enemy_list.draw()
            self.player_list.draw()
            arcade.draw_text(
                f"Score: {self.player.score}   Lives: {self.player.lives}",
                10,
                SCREEN_HEIGHT - 20,
                arcade.color.WHITE,
                14,
            )
        else:
            # מסך סיום
            if self.game_state == "GAME_OVER":
                arcade.draw_text(
                    "GAME OVER",
                    SCREEN_WIDTH / 2,
                    SCREEN_HEIGHT / 2 + 20,
                    arcade.color.RED,
                    36,
                    anchor_x="center",
                )
            else:
                arcade.draw_text(
                    "YOU WIN!",
                    SCREEN_WIDTH / 2,
                    SCREEN_HEIGHT / 2 + 20,
                    arcade.color.GREEN,
                    36,
                    anchor_x="center",
                )

            arcade.draw_text(
                "Press ENTER to Restart",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 20,
                arcade.color.WHITE,
                20,
                anchor_x="center",
            )

    def on_update(self, delta_time):
        if self.game_state != "PLAYING":
            return  # לא מעדכנים כשבמסך סיום

        self.physics_engine.update()

        for coin in arcade.check_for_collision_with_list(
            self.player, self.coin_list
        ):
            self.player.score += coin.value
            coin.remove_from_sprite_lists()

        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            enemy.center_y += enemy.change_y

            if arcade.check_for_collision_with_list(enemy, self.wall_list):
                enemy.center_x -= enemy.change_x
                enemy.center_y -= enemy.change_y
                enemy.pick_new_direction()

            if arcade.check_for_collision(self.player, enemy):
                self.player.lives -= 1
                self.player.center_x = self.player.start_x
                self.player.center_y = self.player.start_y
                self.player.change_x = 0
                self.player.change_y = 0

        if self.player.lives <= 0:
            self.game_state = "GAME_OVER"

        if len(self.coin_list) == 0:
            self.game_state = "WIN"

    def on_key_press(self, key, modifiers):
        if self.game_state == "PLAYING":
            self.player.change_x = 0
            self.player.change_y = 0

            if key == arcade.key.UP:
                self.player.change_y = PLAYER_SPEED
            elif key == arcade.key.DOWN:
                self.player.change_y = -PLAYER_SPEED
            elif key == arcade.key.LEFT:
                self.player.change_x = -PLAYER_SPEED
            elif key == arcade.key.RIGHT:
                self.player.change_x = PLAYER_SPEED
        else:
            # במסך סיום: ENTER → התחלה מחדש
            if key == arcade.key.ENTER:
                self.setup()


# =====================
# הפעלה
# =====================
if __name__ == "__main__":
    game = Game()
    game.setup()
    arcade.run()