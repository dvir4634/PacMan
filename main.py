import arcade
import random

# =====================
# קבועים
# =====================
TILE_SIZE = 32
#אחיה מימרן
LEVEL_MAP = [
    "####################",
    "#P.......#........G#",
    "#.######.#.######..#",
    "#........#.........#",
    "#.######.#.######..#",
    "#........G.....G...#",
    "####################",
]

ROWS = len(LEVEL_MAP)
COLS = len(LEVEL_MAP[0])

SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE
SCREEN_TITLE = "Arcade Pacman"

PLAYER_SPEED = 3
ENEMY_SPEED = 2


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
        self.lives = 3  # ❤️ שלוש פסילות


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
        self.game_state = "PLAYING"

        self.hit_cooldown = 0  # למניעת הורדת כמה לבבות ברצף

    def setup(self):
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.player = None
        self.hit_cooldown = 0

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

    # ❤️ ציור לב
    def draw_heart(self, x, y, size=10):
        arcade.draw_circle_filled(x - size / 2, y, size, arcade.color.RED)
        arcade.draw_circle_filled(x + size / 2, y, size, arcade.color.RED)
        arcade.draw_triangle_filled(
            x - size,
            y,
            x + size,
            y,
            x,
            y - size * 1.8,
            arcade.color.RED,
        )

    def on_draw(self):
        self.clear()

        if self.game_state == "PLAYING":
            self.wall_list.draw()
            self.coin_list.draw()
            self.enemy_list.draw()
            self.player_list.draw()

            # ניקוד
            arcade.draw_text(
                f"Score: {self.player.score}",
                10,
                SCREEN_HEIGHT - 40,
                arcade.color.WHITE,
                14,
            )

            # ❤️ לבבות
            for i in range(self.player.lives):
                self.draw_heart(30 + i * 35, SCREEN_HEIGHT - 15)

        else:
            text = "GAME OVER" if self.game_state == "GAME_OVER" else "YOU WIN!"
            color = arcade.color.RED if self.game_state == "GAME_OVER" else arcade.color.GREEN

            arcade.draw_text(
                text,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 20,
                color,
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
            return

        self.physics_engine.update()

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        # מטבעות
        for coin in arcade.check_for_collision_with_list(
            self.player, self.coin_list
        ):
            self.player.score += coin.value
            coin.remove_from_sprite_lists()

        # אויבים
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            enemy.center_y += enemy.change_y

            if arcade.check_for_collision_with_list(enemy, self.wall_list):
                enemy.center_x -= enemy.change_x
                enemy.center_y -= enemy.change_y
                enemy.pick_new_direction()

            if arcade.check_for_collision(self.player, enemy) and self.hit_cooldown == 0:
                self.player.lives -= 1
                self.hit_cooldown = 60  # שנייה חסינות
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
            if key == arcade.key.ENTER:
                self.setup()


# =====================
# הפעלה
# =====================
if __name__ == "__main__":
    game = Game()
    game.setup()
    arcade.run()
