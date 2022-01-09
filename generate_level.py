import os
import sys
import pygame

pygame.init()
FPS = 50
WIDTH = 600
HEIGHT = 600
STEP = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
player = None
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


tile_images = {'wall': load_image('wall.png'), 'empty': load_image('empty.png'), 'tower': load_image('tower.png')}  # словарь с изображениями тайлов
tile_types = {'black': 'empty', 'grey': 'wall', 'brown': 'tower', 'red': 'mine', 'blue': 'detector', 'white': 'shield',
              'golden': 'evacuation point'}  # словарь соответствия цвета и типа тайла
player_image = load_image('mario.png')  # адапатировать потом к Гришиному Player; Марио для примера

tile_width = tile_height = 50


def load_level(filename):  # считывает карту из файла
    filename = "data\levels\\" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.split() for line in mapFile]
    return level_map


def generate_level(level):  # отрисовывает поле
    x, y = None, None
    new_player = Player(0, 0)  # надо будет адаптировать к Гришиному Player
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'grey':
                Tile('wall', x, y, 'wall')
            elif level[y][x] == 'brown':
                Tile('tower', x, y, 'tower')
            else:
                if level[y][x] in tile_types.keys():
                    Tile('empty', x, y, tile_types[level[y][x]])
                else:
                    Tile('empty', x, y, 'checkpoint')
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_image, pos_x, pos_y, tile_type):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_image]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.type = tile_type


class Player(pygame.sprite.Sprite):  # надо будет заменить на Гришин Player
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)


class Camera:
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size

    def apply(self, obj):  # сдвигает объекты
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):  # корректирует сдвиг камеры
        self.dx = -(target.rect.x - WIDTH / 2)
        self.dy = -(target.rect.y - HEIGHT / 2)


def terminate():
    pygame.quit()
    sys.exit()


running = True
map = load_level("map.txt")
print(*map)
player, level_x, level_y = generate_level(map)  # map для примера
camera = Camera((level_x, level_y))

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

    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)

terminate()
