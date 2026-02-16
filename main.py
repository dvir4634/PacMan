import random

class Coin:
    def __init__(self,center_x,center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.value = 10


class Character:
    def __init__(self,center_x,center_y,speed):
        self.center_x = center_x
        self.center_y = center_y
        self.speed = speed
        self.change_x = 0
        self.change_y = 0


class Player(Character):
    def __init__(self,center_x,center_y,speed):
        super().__init__(center_x,center_y,speed)
        self.score = 0
        self.lives = 3

    def move(self):
        self.center_x += self.change_x*self.speed
        self.center_y += self.change_y*self.speed


class Enemy(Character):
    def __init__(self,center_x,center_y,speed):
        super().__init__(center_x,center_y,speed)
        self.time_to_change_direction = 0

    def pick_new_direction(self):
        directions = [(0,1),(0,-1),(1,0),(-1,0),(0,0)]
        self.change_x, self.change_y = random.choice(directions)
        self.time_to_change_direction = random.uniform(0.3, 1.0)

    def update(self, time_delta=1/60):
        self.time_to_change_direction -= time_delta
        if self.time_to_change_direction <= 0:
            self.pick_new_direction()
        self.center_x += self.change_x*self.speed
        self.center_y += self.change_y*self.speed


class Wall:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y


















# מפה לדוגמה: # = קיר, . = מטבע, P = פקמן, G = רוח, רווח = כלום
LEVEL_MAP = [
    "###########",
    "#P....G...#",
    "#.........#",
    "###########",
]


class ConsolePacmanGame:
    """משחק פקמן טקסטואלי לקונסול."""

    def __init__(self, level_map):
        self.level_map = level_map
        self.height = len(level_map)
        self.width = len(level_map[0]) if self.height > 0 else 0

        self.walls = []
        self.coins = []
        self.ghosts = []
        self.player = None

        self.start_x = 0
        self.start_y = 0

        self.setup()

    def setup(self):
        self.walls = []
        self.coins = []
        self.ghosts = []
        self.player = None

        for y, row in enumerate(reversed(self.level_map)):
            for x, cell in enumerate(row):
                if cell == "#":
                    self.walls.append(Wall(x, y))
                elif cell == ".":
                    self.coins.append(Coin(x, y))
                elif cell == "P":
                    self.player = Player(x, y, 1)
                    self.start_x = x
                    self.start_y = y
                elif cell == "G":
                    self.ghosts.append(Enemy(x, y, 1))

        if self.player is None:
            self.player = Player(self.width // 2, self.height // 2, 1)
            self.start_x = self.player.center_x
            self.start_y = self.player.center_y

    def render(self):
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        for wall in self.walls:
            grid[int(wall.center_y)][int(wall.center_x)] = "#"

        for coin in self.coins:
            grid[int(coin.center_y)][int(coin.center_x)] = "."

        for ghost in self.ghosts:
            grid[int(ghost.center_y)][int(ghost.center_x)] = "G"

        grid[int(self.player.center_y)][int(self.player.center_x)] = "P"

        print("\n" + "=" * (self.width + 2))
        for row in reversed(grid):
            print("|" + "".join(row) + "|")
        print("=" * (self.width + 2))
        print(f"Score: {self.player.score} | Lives: {self.player.lives}")

    def is_wall(self, x, y):
        for wall in self.walls:
            if int(wall.center_x) == int(x) and int(wall.center_y) == int(y):
                return True
        return False

    def get_coin_at(self, x, y):
        for coin in self.coins:
            if int(coin.center_x) == int(x) and int(coin.center_y) == int(y):
                return coin
        return None

    def get_ghost_at(self, x, y):
        for ghost in self.ghosts:
            if int(ghost.center_x) == int(x) and int(ghost.center_y) == int(y):
                return ghost
        return None

    def handle_player_move(self, direction):
        dx, dy = 0, 0
        if direction == "w":
            dy = 1
        elif direction == "s":
            dy = -1
        elif direction == "a":
            dx = -1
        elif direction == "d":
            dx = 1
        else:
            return

        new_x = self.player.center_x + dx
        new_y = self.player.center_y + dy

        if self.is_wall(new_x, new_y):
            return

        self.player.center_x = new_x
        self.player.center_y = new_y

        coin = self.get_coin_at(new_x, new_y)
        if coin is not None:
            self.player.score += coin.value
            self.coins.remove(coin)

        ghost = self.get_ghost_at(new_x, new_y)
        if ghost is not None:
            self.player.lives -= 1
            print("ננגסת ע\"י רוח! חיים -1")
            self.reset_player_position()

    def reset_player_position(self):
        self.player.center_x = self.start_x
        self.player.center_y = self.start_y

    def move_ghosts(self):
        for ghost in self.ghosts:
            if random.random() < 0.3 or (ghost.change_x == 0 and ghost.change_y == 0):
                ghost.pick_new_direction()

            new_x = ghost.center_x + ghost.change_x
            new_y = ghost.center_y + ghost.change_y

            if self.is_wall(new_x, new_y):
                continue

            ghost.center_x = new_x
            ghost.center_y = new_y

            if int(ghost.center_x) == int(self.player.center_x) and int(ghost.center_y) == int(self.player.center_y):
                self.player.lives -= 1
                print("רוח תפסה אותך! חיים -1")
                self.reset_player_position()

    def is_game_over(self):
        if self.player.lives <= 0:
            print("GAME OVER – נגמרו החיים.")
            return True
        if len(self.coins) == 0:
            print("YOU WIN – אספת את כל המטבעות!")
            return True
        return False

    def run(self):
        print("ברוך הבא לפקמן קונסול!")
        print("השליטה: w = למעלה, s = למטה, a = שמאלה, d = ימינה, q = יציאה.")
        while True:
            self.render()

            if self.is_game_over():
                break

            command = input("לאן לזוז? (w/a/s/d/q): ").strip().lower()
            if command == "q":
                print("יציאה מהמשחק.")
                break

            self.handle_player_move(command)
            self.move_ghosts()


if __name__ == "__main__":
    game = ConsolePacmanGame(LEVEL_MAP)
    game.run()