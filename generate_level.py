import os
import sys
import pygame

WIDTH = 600
HEIGHT = 600
STEP = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, color_key=-1):  # загружает изображения
    fullname = 'data\images\\' + name
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


tile_images = {'wall': load_image('wall.png'), 'empty': load_image('empty.png'),
               'tower': load_image('tower.png')}  # словарь с изображениями тайлов
tile_types = {'black': 'empty', 'grey': 'wall', 'brown': 'tower', 'red': 'mine', 'blue': 'detector', 'white': 'shield',
              'golden': 'evacuation point'}  # словарь соответствия цвета и типа тайла

tile_width = tile_height = 50


def load_level(filename):  # считывает карту из файла
    filename = "data\levels\\" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.split() for line in mapFile]
    return level_map


def generate_level(level, tiles_all_groups):  # отрисовывает поле
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'grey':
                Tile('wall', x, y, 'wall', tiles_all_groups)
            elif level[y][x] == 'brown':
                Tile('tower', x, y, 'tower', tiles_all_groups)
            else:
                if level[y][x] in tile_types.keys():
                    Tile('empty', x, y, tile_types[level[y][x]], tiles_all_groups)
                else:
                    Tile('empty', x, y, 'checkpoint', tiles_all_groups)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_image, pos_x, pos_y, tile_type, tiles_all_group):
        super().__init__(*tiles_all_group)
        self.image = tile_images[tile_image]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.type = tile_type


class Player(pygame.sprite.Sprite):  # надо будет заменить на Гришин Player
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = load_image('mario.png')
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def update(self, player):  # корректирует сдвиг камеры
        self.dx = -(player.rect.x - WIDTH / 2)
        self.dy = -(player.rect.y - HEIGHT / 2)
        player.bomb_animation_pack.x_indent += self.dx
        player.bomb_animation_pack.y_indent += self.dy

    def apply(self, all_sprites):  # сдвигает объекты
        for obj in all_sprites:
            obj.rect.x += self.dx
            obj.rect.y += self.dy


def terminate():
    pygame.quit()
    sys.exit()


def generate_level_main():
    pygame.init()
    map = load_level("map.txt")
    print(*map)
    player = Player(0, 0)
    generate_level(map, [tiles_group, all_sprites])  # map для примера
    camera = Camera()

    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.rect.x -= STEP
                if event.key == pygame.K_RIGHT:
                    player.rect.x += STEP
                if event.key == pygame.K_UP:
                    player.rect.y -= STEP
                if event.key == pygame.K_DOWN:
                    player.rect.y += STEP
                if event.key == pygame.K_ESCAPE:
                    terminate()

        camera.update(player)

        camera.apply(all_sprites)

        screen.blit(load_image('map_bg_image.jpg'), (0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)

        pygame.display.flip()

        clock.tick(50)

    terminate()


if __name__ == "__main__":
    generate_level_main()
