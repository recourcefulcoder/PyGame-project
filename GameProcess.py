# -*- coding: utf-8 -*-
import pygame
from pygame import image as pi
import sys
import os
import json
from math import floor
from generate_level import (load_level, generate_level, terminate,
                            Camera, STEP, tile_images)
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic

CHANGE_SPRITE = pygame.USEREVENT + 1
SIZE = WIDTH, HEIGHT = 800, 600


def except_hook(cls, traceback, exception):
    sys.__excepthook__(cls, traceback, exception)


def load_image(name, colorkey=None):
    fullname = os.path.join('data\\images', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pi.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def count_player_coords_p(player):
    # Находит местополжение игрока на матрице карты
    # (возвращаемое значение функции load_level в файле generate_level)
    # определяется по центру изображения игрока
    # предоположительно будет использоваться при получении бонусов
    x_coord = floor(player.map_x_pos / STEP)  # выяснила опытным путем, что работает только сокруглением вниз
    y_coord = floor(player.map_y_pos / STEP)
    return x_coord, y_coord


def count_player_coords_c(x, y):
    # Находит местополжение игрока на матрице карты
    # (возвращаемое значение функции load_level в файле generate_level)
    # определяется по переданным координатам
    # предоположительно будет использоваться при взаимодействии со стенами
    x_coord = floor(x / STEP)
    y_coord = floor(y / STEP)
    return x_coord, y_coord


def draw_icon(screen, image_name, pose):
    image = load_image(image_name, -1)
    screen.blit(image, pose)


class BombAnimationPack:
    def __init__(self, player, time_period, all_sprite_group):
        self.time_gone = 0
        self.clock = pygame.time.Clock()
        self.time_period = time_period

        self.process_dead = True

        self.alpha_screen = pygame.Surface(SIZE)
        self.alpha_screen.set_alpha(100)
        self.alpha_screen.set_colorkey((0, 0, 0))

        self.player = player

        self.explosion_image = load_image("explosion.png")
        self.exp_image_group = pygame.sprite.Group()
        self.current_exp_image = pygame.sprite.Sprite(self.exp_image_group, all_sprite_group)
        self.current_exp_image.rect = pygame.Rect(300, 300, 100, 100)
        self.exp_col_cnt = -1
        self.exp_row_cnt = -2

        self.x_indent = -300
        self.y_indent = -300

    def update(self):
        value = self.clock.tick()
        self.update_progress_bar(value)
        self.update_bomb_borders()
        self.animate_explosion()

    def update_progress_bar(self, value):
        if self.process_dead:
            return
        self.time_gone += value
        pygame.draw.rect(self.player.screen, (255, 255, 255),
                         (self.player.rect.x, self.player.rect.y - 7, self.player.image_width, 7), width=1)
        pygame.draw.rect(self.player.screen, (0, 255, 0),
                         (self.player.rect.x + 1, self.player.rect.y - 6,
                          self.time_gone / (self.time_period * 1000) * self.player.image_width - 1, 5))
        if self.time_gone + value >= self.time_period * 1000:
            self.player.bomb_planted = True
            self.current_exp_image.rect = pygame.Rect(
                self.player.bomb_pos[0] + abs(self.x_indent) + 300 - 50 + self.player.image_width // 2,
                self.player.bomb_pos[1] + abs(self.y_indent) + 300 - 50 + self.player.image_height, 100, 100)
            self.kill_process_bar()

    def update_bomb_borders(self):
        self.alpha_screen.fill((0, 0, 0))
        center = [300 + self.player.image_width // 2, 300 + self.player.image_height]
        if not self.process_dead:
            pygame.draw.circle(self.alpha_screen, (219, 137, 0), center,
                               self.time_gone / (self.time_period * 1000) * self.player.detonate_zone)
            pygame.draw.circle(self.alpha_screen, (255, 0, 0), center,
                               self.time_gone / (self.time_period * 1000) * self.player.attack_zone)
            self.player.screen.blit(self.alpha_screen, (0, 0))
        if self.player.bomb_planted:
            pygame.draw.circle(self.alpha_screen, (219, 137, 0), center, self.player.detonate_zone)
            pygame.draw.circle(self.alpha_screen, (255, 0, 0), center, self.player.attack_zone)
            self.player.screen.blit(self.alpha_screen,
                                    (self.x_indent - self.player.bomb_pos[0],
                                     self.y_indent - self.player.bomb_pos[1]))

    def animate_explosion(self):
        if self.exp_row_cnt == -2:
            return
        self.exp_col_cnt = (self.exp_col_cnt + 1) % 5
        self.exp_row_cnt += (self.exp_col_cnt == 0)
        if self.exp_row_cnt > 4:
            self.exp_row_cnt = -2
            self.exp_col_cnt = -1
            return
        self.current_exp_image.image = self.explosion_image.subsurface(
            pygame.Rect(self.exp_col_cnt * 100, self.exp_row_cnt * 100, 100, 100))
        self.exp_image_group.draw(self.player.screen)

    def kill_process_bar(self):
        self.process_dead = True
        self.time_gone = 0
        self.player.can_move = True


class Player(pygame.sprite.Sprite):
    def __init__(self, username, binded_screen, player_group, all_sprites_group, tiles_all_group):
        super().__init__(player_group, all_sprites_group)
        self.current_orientation = 0
        # 0 - персонаж повёрнут лицом, 1 - левым боком, 2 - правым боком, 3 - спиной
        self.last_animation_step = 0
        self.can_move = True
        self.player_is_moving = False

        self.image_width = 32
        self.image_height = 48
        self.full_image = load_image("player_image.png")
        self.image = self.full_image.subsurface(
            pygame.Rect(0, self.current_orientation * self.image_height, self.image_width, self.image_height))
        self.rect = self.image.get_rect()
        self.map_x_pos = self.image_width // 2  # Здесь находятся координаты относительно левого верхнего
        self.map_y_pos = self.image_height // 2  # угла карты центра изображения персонажа

        self.clock = pygame.time.Clock()
        self.screen = binded_screen
        self.camera = Camera()

        self.detonate_zone = 200
        self.attack_zone = 50
        self.bomb_planted = False
        self.bomb_animation_pack = BombAnimationPack(self, 3, all_sprites_group)
        self.bomb_pos = [None, None]

        self.has_buckler = False
        self.has_detector = False
        self.current_checkpoint = [0, [self.map_x_pos, self.map_y_pos]]
        self.detonated_mines = []
        self.destroyed_towers = 0  # здесь - число уничтоженных вышек
        self.current_level = load_level(f"{username}")
        self.towers = generate_level(self.current_level, tiles_all_group)
        print(self.towers)

    def move(self, moving_vector, map):
        if self.can_move:
            # определяет, не вышел ли персонаж за пределы карты
            if not (STEP * 35 >= self.map_x_pos + moving_vector[0] >= 0):
                moving_vector[0] = 0
            if not (STEP * 29.6 >= self.map_y_pos + moving_vector[1] >= 0):
                moving_vector[1] = 0
            map_x, map_y = count_player_coords_c(self.map_x_pos + moving_vector[0], self.map_y_pos + moving_vector[1])
            if map[map_y][map_x] != 'grey':  # проверяет, не войдет ли персонаж в стену
                self.rect = self.rect.move(*moving_vector)
                self.map_x_pos += moving_vector[0]
                self.map_y_pos += moving_vector[1]
            else:
                map_x, map_y = count_player_coords_c(self.map_x_pos + moving_vector[0], self.map_y_pos)
                if map[map_y][map_x] != 'grey':
                    self.rect = self.rect.move(moving_vector[0], 0)
                    self.map_x_pos += moving_vector[0]
                else:
                    map_x, map_y = count_player_coords_c(self.map_x_pos, self.map_y_pos + moving_vector[1])
                    if map[map_y][map_x] != 'grey':
                        self.rect = self.rect.move(0, moving_vector[1])
                        self.map_y_pos += moving_vector[1]

    def plant_bomb(self):
        if not self.bomb_planted:
            self.bomb_pos = [self.bomb_animation_pack.x_indent,
                             self.bomb_animation_pack.y_indent]
            self.can_move = False
            self.bomb_animation_pack.process_dead = False

    def detonate_bomb(self):
        if self.bomb_planted:
            bomb_distance = ((self.bomb_animation_pack.x_indent - self.bomb_pos[0]) ** 2 + (
                    self.bomb_animation_pack.y_indent - self.bomb_pos[1]) ** 2) ** 0.5
            if bomb_distance <= self.detonate_zone:
                self.bomb_planted = False
                self.bomb_animation_pack.exp_row_cnt += 1
                ans = self.exploded_cells()
                for elem in ans:
                    if self.current_level[elem[0]][elem[1]] == 'brown':
                        self.current_level[elem[0]][elem[1]] = "green"
                        self.towers[(elem[0], elem[1])].image = tile_images["ruins"]
                        self.destroyed_towers += 1
            if bomb_distance <= self.attack_zone:
                print("you're dead!")

    def change_picture(self):
        if not self.player_is_moving or not self.can_move:
            self.last_animation_step = 0
            self.image = self.full_image.subsurface(
                pygame.Rect(0, self.current_orientation * self.image_height, self.image_width, self.image_height))
        else:
            self.last_animation_step = (self.last_animation_step + 1) % 4
            self.image = self.full_image.subsurface(
                pygame.Rect(self.last_animation_step * self.image_width, self.current_orientation * self.image_height,
                            self.image_width, self.image_height))

    def check_position(self, map):
        #  print(self.has_buckler)
        #  проверяет, на какую клетку наступил игрок и, если надо, выдает ему бонус или умертвляет
        y, x = count_player_coords_p(self)
        if map[x][y] == 'white':
            self.has_buckler = True
        if map[x][y] == 'blue':
            self.has_detector = True
        if map[x][y] == 'red':
            if self.has_buckler:
                self.has_buckler = False
            else:
                pass  # смерть

    def detect_mine(self, map, screen):
        # ищет и подсвечиает мины вокруг игрока
        y, x = count_player_coords_p(self)
        screen_x, screen_y = self.rect.x + self.image_width // 2, self.rect.y + self.image_height // 2
        steps = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
        pygame.draw.circle(screen, (255, 255, 255),
                           (screen_x, screen_y), 75, 3)
        for elem in steps:
            if map[x + elem[0]][y + elem[1]] == 'red':
                pygame.draw.circle(screen, (255, 0, 0),
                                   (screen_x + 50 * elem[0], screen_y + 50 * elem[1]), 12.5)

    def exploded_cells(self):
        steps = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (0, 0)]
        ans = list()
        x = int(abs(self.bomb_pos[0]) // STEP)
        y = int(abs(self.bomb_pos[1]) // STEP)
        for point in steps:
            ppos = [(x + point[0]) * STEP + STEP // 2, (y + point[1]) * STEP + STEP // 2]  # point position
            dist = ((abs(self.bomb_pos[0]) + self.image_width // 2 - ppos[0]) ** 2 + (
                    abs(self.bomb_pos[1]) + self.image_height - ppos[1]) ** 2) ** 0.5
            # оказывается, bomb_pos хранит координаты левого верхнего угла изображения игрока
            # в момент закладки бомбы, а не её технические координаты на карте
            if dist <= self.attack_zone and not (x + point[0] < 0 or y + point[1] < 0):
                ans.append([y + point[1], x + point[0]])
        return ans


class DialogWindow(pygame.Surface):
    def __init__(self, binded_screen, dialog_name):
        super().__init__(SIZE)
        self.text = ""
        self.screen = binded_screen
        self.text_len = 0
        self.timer = 0
        self.clock = pygame.time.Clock()
        self.last_char_num = -1
        self.bg_image = pygame.transform.scale(load_image("dialog_bg_image.jpg"), SIZE)
        self.current_text = ''
        self.new_paragraph = False
        self.font = pygame.font.Font("data/fonts/dsmoster.ttf", 20)
        self.add_char_period = 50  # milliseconds
        self.add_paragraph_period = 3000
        self.load_dialog(dialog_name)

    def load_dialog(self, filename):
        # Реплики в диалогах отделять друг от друга тремя звёздочками. Пример:
        # Джереми:
        # Отличный сегодня денёк!
        #
        # Не правда ли?)
        # ***
        # Алекс:
        # Действительно!)
        # ***
        # Абзацы с неуказанным обозначением произносящего считаются абзацами от автора диалога
        with open(f"data/dialogs/{filename}", encoding='utf-8') as text_dialog:
            self.text = text_dialog.read()
        self.text_len = len(self.text)

    def show_dialog(self):
        self.change_text()
        self.blit(self.bg_image, (0, 0))
        self.write_text()

    def change_text(self):
        self.timer += self.clock.tick()
        if self.last_char_num + 1 < self.text_len:
            if not self.new_paragraph and self.timer >= self.add_char_period:
                self.current_text += self.text[self.last_char_num + 1]
                self.last_char_num += 1
                self.timer = 0
                if self.text[self.last_char_num + 1:self.last_char_num + 4] == "***":
                    self.new_paragraph = True
                    self.last_char_num += 4
            elif self.new_paragraph and self.timer >= self.add_paragraph_period:
                self.current_text += self.text[self.last_char_num + 1]
                self.last_char_num += 1
                self.new_paragraph = False
                self.timer = 0
        self.current_text = self.text[:self.last_char_num + 1]

    def write_text(self):
        text_array = self.make_text_array()
        y_indent = 0
        for elem in text_array:
            text = self.font.render(elem, True, (50, 50, 50))
            self.screen.blit(text, (30 - 5, y_indent + 30))
            y_indent += self.font.size(elem)[1] + 5

    def make_text_array(self):
        text_array = list()
        start_point = 0
        current_len = len(self.current_text)
        while start_point < current_len:
            finish_point = start_point + 1
            avoid_n_symbol = 0
            while self.font.size(self.current_text[start_point:finish_point])[0] < WIDTH - 60:
                finish_point += 1
                if finish_point > current_len:
                    break
                if finish_point < current_len and self.current_text[finish_point] == '\n':
                    avoid_n_symbol += 1
                    break
            if not self.current_text[start_point:finish_point].strip() == "***":
                text_array.append(self.current_text[start_point:finish_point])
            else:
                text_array.append('\n')
            start_point = finish_point + avoid_n_symbol
        return text_array


class LeaveGameWindow(QWidget):
    def __init__(self, player, level_num, username):
        super().__init__()
        uic.loadUi("ui_files/leave_game_win.ui", self)
        self.running = True
        self.player = player
        self.level_num = level_num
        self.save_level = ''
        self.username = username
        self.no_btn.clicked.connect(self.close)
        self.yes_btn.clicked.connect(self.close_and_safe)

    def close_and_safe(self):
        with open(f"data/progress/{self.username}/info.txt", mode='w', encoding="utf-8") as infofile:
            data = {
                "level_num": self.level_num,
                "checkpoint": self.player.current_checkpoint,
                "has_shield": self.player.has_buckler,
                "has_detector": self.player.has_detector,
                "destroyed_towers": self.player.destroyed_towers
            }
            writedata = json.dumps(data)
            infofile.write(writedata)
        with open(f"data/progress/{self.username}/map.txt", mode='w', encoding="utf-8") as mapfile:
            for elem in self.save_level:
                mapfile.write(' '.join(elem))
                mapfile.write('\n')
        self.running = False


def dialog_win_main():
    pygame.init()
    pygame.time.set_timer(CHANGE_SPRITE, 200)
    pygame.display.set_caption("Loop")
    screen = pygame.display.set_mode(SIZE)
    win = DialogWindow(screen, "quick start to plot.txt")
    running = True
    while running:
        screen.blit(win, (0, 0))
        win.show_dialog()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.display.flip()
    terminate()


def game_process_main(username):
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    pygame.init()
    pygame.time.set_timer(CHANGE_SPRITE, 200)
    pygame.display.set_caption("Loop")
    screen = pygame.display.set_mode(SIZE)

    clock = pygame.time.Clock()

    with open(f"data/progress/{username}/info.txt", mode='r', encoding='utf-8') as info:
        data = json.loads(info.readlines()[0])
        current_level_num = data["level_num"]

    tiles_group = pygame.sprite.Group()
    all_sprites_group = pygame.sprite.Group()
    tiles_all_group = [tiles_group, all_sprites_group]

    player_group = pygame.sprite.Group()
    player = Player(username, screen, player_group, all_sprites_group, tiles_all_group)

    camera = Camera()

    close_win = LeaveGameWindow(player, current_level_num, username)

    doubled_speed = False
    pressed_move_buttons = [False, False, False, False]

    while close_win.running:
        clock.tick(30)
        x_pos_change = 0
        y_pos_change = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_win.save_level = player.current_level
                close_win.show()
            if event.type == pygame.KEYDOWN:
                check = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    check = True
                    pressed_move_buttons[3] = True
                    player.current_orientation = 3
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    check = True
                    pressed_move_buttons[0] = True
                    player.current_orientation = 0
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    check = True
                    pressed_move_buttons[2] = True
                    player.current_orientation = 2
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    check = True
                    pressed_move_buttons[1] = True
                    player.current_orientation = 1
                if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                    pygame.time.set_timer(CHANGE_SPRITE, 100)
                    doubled_speed = True
                if event.key == pygame.K_r:
                    player.plant_bomb()
                if event.key == pygame.K_e:
                    player.detonate_bomb()
                if event.key == pygame.K_ESCAPE:
                    close_win.running = False
                if check:
                    player.player_is_moving = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    pressed_move_buttons[3] = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    pressed_move_buttons[0] = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    pressed_move_buttons[2] = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    pressed_move_buttons[1] = False
                if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                    pygame.time.set_timer(CHANGE_SPRITE, 200)
                    doubled_speed = False
                if event.key == pygame.K_r:
                    player.bomb_animation_pack.kill_process_bar()
                if True not in pressed_move_buttons:
                    player.player_is_moving = False
                for ind in range(3, -1, -1):
                    if pressed_move_buttons[ind]:
                        player.current_orientation = ind
            if event.type == CHANGE_SPRITE:
                player.change_picture()
        speed = 2 * (1 + doubled_speed)
        y_pos_change -= speed * pressed_move_buttons[3]
        y_pos_change += speed * pressed_move_buttons[0]
        x_pos_change += speed * pressed_move_buttons[2]
        x_pos_change -= speed * pressed_move_buttons[1]
        screen.blit(load_image('map_bg_image.jpg'), (0, 0))
        player.move([x_pos_change, y_pos_change], player.current_level)
        camera.update(player)
        player.check_position(player.current_level)
        camera.apply(all_sprites_group)
        tiles_group.draw(screen)
        player.bomb_animation_pack.update()
        player_group.draw(screen)

        pygame.display.flip()
    terminate()
    sys.exit(app.exec())


if __name__ == "__main__":
    game_process_main("admin")
