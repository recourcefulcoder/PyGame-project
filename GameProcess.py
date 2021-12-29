import pygame
from pygame import image as pi
import sys
import os

CHANGE_SPRITE = pygame.USEREVENT + 1


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
    if not self.player_is_moving:
        self.last_animation_step = 0
        self.image = self.current_image.subsurface(
            pygame.Rect(0, self.current_orientation * self.image_height, self.image_width, self.image_height))
    else:
        self.last_animation_step = (self.last_animation_step + 1) % 4
        self.image = self.current_image.subsurface(
            pygame.Rect(self.last_animation_step * self.image_width, self.current_orientation * self.image_height,
                        self.image_width, self.image_height))


class Player(pygame.sprite.Sprite):
    def __init__(self, binded_screen, *groups):
        super().__init__(*groups)
        self.current_orientation = 0
        self.player_clock = pygame.time.Clock()
        self.binded_screen = binded_screen
        self.player_is_moving = False
        self.last_animation_step = 0
        self.image_width = 32
        self.image_height = 48
        # 0 - персонаж повёрнут лицом, 1 - левым боком, 2 - правым боком, 3 - спиной
        self.current_image = load_image("player_image.png")
        self.image = self.current_image.subsurface(
            pygame.Rect(0, self.current_orientation * self.image_height, self.image_width, self.image_height))
        self.rect = self.image.get_rect()

    def move(self, moving_vector):
        self.rect = self.rect.move(*moving_vector)


if __name__ == "__main__":
    pygame.init()
    pygame.time.set_timer(CHANGE_SPRITE, 200)
    pygame.display.set_caption("Loop")
    size = width, height = 800, 500
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    player_group = pygame.sprite.Group()
    player = Player(screen, player_group)
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
        pygame.display.flip()
