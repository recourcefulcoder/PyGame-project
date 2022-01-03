import pygame
from pygame import image as pi
import sys
import os

CHANGE_SPRITE = pygame.USEREVENT + 1
SIZE = WIDTH, HEIGHT = 800, 500


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


def change_picture(self):
    if not self.player_is_moving or not player.can_move:
        self.last_animation_step = 0
        self.image = self.current_image.subsurface(
            pygame.Rect(0, self.current_orientation * self.image_height, self.image_width, self.image_height))
    else:
        self.last_animation_step = (self.last_animation_step + 1) % 4
        self.image = self.current_image.subsurface(
            pygame.Rect(self.last_animation_step * self.image_width, self.current_orientation * self.image_height,
                        self.image_width, self.image_height))


class BombAnimationPack:
    def __init__(self, player, time_period):
        self.time_gone = 0
        self.clock = pygame.time.Clock()
        self.time_period = time_period

        self.process_dead = True

        self.alpha_screen = pygame.Surface(SIZE)
        self.alpha_screen.set_alpha(100)

        self.player = player

        self.explosion_image = load_image("explosion.png")
        self.exp_image_group = pygame.sprite.Group()
        self.current_exp_image = pygame.sprite.Sprite(self.exp_image_group)
        self.exp_col_cnt = -1
        self.exp_row_cnt = -2
        self.exp_timer = 0

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
                self.player.bomb_pos[0] - 50, self.player.bomb_pos[1] - 50, 100, 100)
            self.kill_process_bar()

    def update_bomb_borders(self):
        center = [self.player.bomb_pos[0], self.player.bomb_pos[1]]
        self.alpha_screen.fill((0, 0, 0))
        if not self.process_dead:
            pygame.draw.circle(self.alpha_screen, (219, 137, 0), center,
                               self.time_gone / (self.time_period * 1000) * self.player.detonate_zone)
            pygame.draw.circle(self.alpha_screen, (255, 0, 0), center,
                               self.time_gone / (self.time_period * 1000) * self.player.attack_zone)
            self.player.screen.blit(self.alpha_screen, (0, 0))
        if self.player.bomb_planted:
            pygame.draw.circle(self.alpha_screen, (219, 137, 0), center, self.player.detonate_zone)
            pygame.draw.circle(self.alpha_screen, (255, 0, 0), center, self.player.attack_zone)
            self.player.screen.blit(self.alpha_screen, (0, 0))

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
    def __init__(self, binded_screen, *groups):
        super().__init__(*groups)
        self.current_orientation = 0
        self.player_clock = pygame.time.Clock()
        self.screen = binded_screen
        self.player_is_moving = False
        self.detonate_zone = 200
        self.attack_zone = 50
        self.can_move = True
        self.bomb_planted = False
        self.bomb_animation_pack = BombAnimationPack(self, 3)
        self.bomb_pos = [None, None]
        self.last_animation_step = 0
        self.image_width = 32
        self.image_height = 48
        # 0 - персонаж повёрнут лицом, 1 - левым боком, 2 - правым боком, 3 - спиной
        self.current_image = load_image("player_image.png")
        self.image = self.current_image.subsurface(
            pygame.Rect(0, self.current_orientation * self.image_height, self.image_width, self.image_height))
        self.rect = self.image.get_rect()

    def move(self, moving_vector):
        if self.can_move:
            self.rect = self.rect.move(*moving_vector)

    def plant_bomb(self):
        if not self.bomb_planted:
            self.bomb_pos = [self.rect.x + self.image_width // 2,
                             self.rect.y + self.image_height]
            self.can_move = False
            self.bomb_animation_pack.process_dead = False

    def detonate_bomb(self):
        if self.bomb_planted:
            bomb_distance = ((self.rect.x + self.image_width // 2 - self.bomb_pos[0]) ** 2 + (
                    self.rect.y + self.image_height // 2 - self.bomb_pos[1]) ** 2) ** 0.5
            if bomb_distance <= self.detonate_zone:
                self.bomb_planted = False
                self.bomb_animation_pack.exp_row_cnt += 1
            if bomb_distance <= self.attack_zone:
                print("you're dead!")


if __name__ == "__main__":
    pygame.init()
    pygame.time.set_timer(CHANGE_SPRITE, 200)
    pygame.display.set_caption("Loop")
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    player_group = pygame.sprite.Group()
    player = Player(screen, player_group)
    player.rect.x = 200
    player.rect.y = 200
    running = True
    doubled_speed = False
    pressed_move_buttons = [False, False, False, False]
    # 0 = k_down, 1 = k_left, 2 = k_right, 3 = k_up
    while running:
        clock.tick(30)
        x_pos_change = 0
        y_pos_change = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
                    running = False
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
                change_picture(player)
        speed = 2 * (1 + doubled_speed)
        y_pos_change -= speed * pressed_move_buttons[3]
        y_pos_change += speed * pressed_move_buttons[0]
        x_pos_change += speed * pressed_move_buttons[2]
        x_pos_change -= speed * pressed_move_buttons[1]
        screen.fill((0, 0, 0))
        player.move([x_pos_change, y_pos_change])
        player_group.draw(screen)
        player.bomb_animation_pack.update()
        pygame.display.flip()
