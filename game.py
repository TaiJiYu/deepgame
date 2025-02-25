import time

import pygame

pygame.init()
font_size = 15
font = pygame.font.SysFont("SimHei", font_size)


class Mind:
    SIZE = 500, 500
    CameraPos = SIZE[0] / 2, SIZE[1] / 2

    def __init__(self):
        self.screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption("deepgame  R键重新开始")
        self.back_layer = pygame.Surface(Mind.SIZE, pygame.SRCALPHA)
        self.game = Game()
        self.mouse_left_bit = False
        self.key_r = False
        self.clock = pygame.time.Clock()
        self.run()

    def get_input(self, keys, mouse):
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit(0)
        if (not self.key_r) and keys[pygame.K_r]:
            self.game.replay()
        self.key_r = keys[pygame.K_r]
        # 鼠标左键
        if (not self.mouse_left_bit) and mouse[0]:
            if self.game.player_fall():
                win, end = self.game.check_end()
                if end:
                    if win == "0":
                        print("平局")
                    else:
                        print(self.game.label_to_show(win), "赢了")
                else:
                    self.game.ai_fall()
        self.mouse_left_bit = mouse[0]

    def draw(self):
        self.screen.blit(self.back_layer, (0, 0))
        self.game.draw(self.screen)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)
            mouse = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()
            self.get_input(keys, mouse)
            self.screen.fill((255, 255, 255))
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)


from openai import OpenAI
import deepseek as dp


class DeepSeekAi:

    def __init__(self):
        self.client = OpenAI(api_key=dp.API_KEY, base_url="https://api.deepseek.com")
        self.content = []

    def replay(self):
        self.content = []

    def ask(self, content, del_func):
        self.content.append({"role": "user", "content": content})
        print("问deepseek：", content)

        def _():
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                             {"role": "system", "content": """你是一个专业的井字棋棋手。
### 井字棋规则：
1. **棋盘**：3x3的方格。
2. **玩家**：两名玩家，分别用“X”和“O”表示。
3. **目标**：先在水平、垂直或对角线上连成一条线的玩家获胜。
4. **轮流下棋**：玩家轮流在空格中放置自己的符号（“X”或“O”）。
5. **平局**：如果棋盘填满且无人获胜，则为平局。
### 示例棋盘：
```
(1,1) | (1,2) | (1,3)
---------------------
(2,1) | (2,2) | (2,3)
---------------------
(3,1) | (3,2) | (3,3)
```"""},
                         ] + self.content,
                stream=False
            )
            info = response.choices[0].message.content
            self.content.append({"role": "assistant", "content": info})
            del_func(info)

        _thread.start_new_thread(_,())

import _thread

class Game:
    def __init__(self):
        self.player_pawn_type = "1"
        self.fall_type = 0
        self.ai = DeepSeekAi()
        self.game = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        self.time_screen_layer = pygame.Surface(Mind.SIZE, pygame.SRCALPHA)

    def replay(self):
        self.fall_type = 0
        self.game = [["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]
        self.ai.replay()
    def label_to_show(self, l):
        if l == "1":
            return "X"
        elif l == "2":
            return "O"
        else:
            return " "
    def pack_to_ai(self):
        game = self.game[0]+self.game[1]+self.game[2]
        info = """```
{0} | {1} | {2}
---------------------
{3} | {4} | {5}
---------------------
{6} | {7} | {8}
```""".format(*[self.label_to_show(i) for i in game])
        return "请你作为{}方落子，棋盘如下：\n{}\n请以横纵坐标作为回答，不要有额外的文字\n例如：2,3". \
            format("O" if self.player_pawn_type == "1" else "X", info)

    def draw(self, screen):
        self.check_mouse()
        pygame.draw.line(screen, (0, 0, 0), (0, Mind.SIZE[1] / 3), (Mind.SIZE[0], Mind.SIZE[1] / 3), 10)
        pygame.draw.line(screen, (0, 0, 0), (0, 2 * Mind.SIZE[1] / 3), (Mind.SIZE[0], 2 * Mind.SIZE[1] / 3), 10)
        pygame.draw.line(screen, (0, 0, 0), (Mind.SIZE[0] / 3, 0), (Mind.SIZE[0] / 3, Mind.SIZE[1]), 10)
        pygame.draw.line(screen, (0, 0, 0), (2 * Mind.SIZE[0] / 3, 0), (2 * Mind.SIZE[0] / 3, Mind.SIZE[1]), 10)

        for i, s in enumerate(self.game):
            for j, pawn in enumerate(s):
                self.draw_pawn(screen, ((2 * j + 1) * Mind.SIZE[0] / 6, (2 * i + 1) * Mind.SIZE[1] / 6), pawn, True)

        self.draw_time_pawn()
        screen.blit(self.time_screen_layer, (0, 0))

    def check_mouse(self):
        mouse = pygame.mouse.get_pos()
        return mouse[1] * 3 // Mind.SIZE[1], mouse[0] * 3 // Mind.SIZE[0]

    def draw_time_pawn(self):
        self.time_screen_layer.fill((255, 255, 255, 0))
        i, j = self.check_mouse()
        if self.game[i][j] != "0":
            return
        self.draw_pawn(self.time_screen_layer, ((2 * j + 1) * Mind.SIZE[0] / 6, (2 * i + 1) * Mind.SIZE[1] / 6),
                       self.player_pawn_type,
                       False)

    def check_end(self):
        # 检查行
        for row in self.game:
            if row[0] == row[1] == row[2] and row[0] != '0':
                return row[0], True

                # 检查列
        for col in range(3):
            if self.game[0][col] == self.game[1][col] == self.game[2][col] and self.game[0][col] != '0':
                return self.game[0][col], True

        # 检查对角线
        if self.game[0][0] == self.game[1][1] == self.game[2][2] and self.game[0][0] != "0":
            return self.game[0][0], True
        if self.game[0][2] == self.game[1][1] == self.game[2][0] and self.game[0][2] != "0":
            return self.game[0][2], True  # 返回赢家 'X' 或 'O'

        # 检查是否平局
        for row in self.game:
            if "0" in row:
                return "0", False  # 游戏未结束

        return "0", False  # 平局

    def player_fall(self):
        if str(self.fall_type + 1) != self.player_pawn_type:
            return False
        i, j = self.check_mouse()
        return self.fall(i, j)

    # ai落子
    def ai_fall(self):
        if str(self.fall_type + 1) == self.player_pawn_type:
            return False

        def _(info):
            print("回复：", info)
            i, j = info.split(",")
            if self.fall(int(i) - 1, int(j) - 1):
                win, end = self.check_end()
                if end:
                    if win == "0":
                        print("平局")
                    else:
                        print(self.label_to_show(win), "赢了")
        self.ai.ask(self.pack_to_ai(),_)


        # return self.fall(int(i) - 1, int(j) - 1)

    # 落子
    def fall(self, i, j):
        # i,j从0开始
        if self.game[i][j] != "0":
            return False
        s = str(self.fall_type + 1)
        self.game[i][j] = s
        self.fall_type = (self.fall_type + 1) % 2
        return True

    def draw_pawn(self, screen, pos, pawn_type, is_real):
        if pawn_type == "1":
            pygame.draw.line(screen, (0, 0, 0, 255 if is_real else 100), (pos[0] - 20, pos[1] - 20),
                             (pos[0] + 20, pos[1] + 20), 5)
            pygame.draw.line(screen, (0, 0, 0, 255 if is_real else 100), (pos[0] - 20, pos[1] + 20),
                             (pos[0] + 20, pos[1] - 20), 5)
        elif pawn_type == "2":
            pygame.draw.circle(screen, (200, 0, 0, 255 if is_real else 100), pos, 20, 5)


mind = Mind()
mind.run()
