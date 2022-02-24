import sys
import pygame

WIDTH = 800
HEIGHT = 600
STEP = 50

print("generate_level set_mode")
pygame.display.set_mode((WIDTH, HEIGHT))
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, color_key=-1):  # загружает изображения
    fullname = 'data/images/' + name
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
    if name == "escape.png":
        pygame.display.quit()
    return image


tile_images = {'wall': load_image('wall.png'), 'empty': load_image('empty.png'),
               'tower': load_image('tower.png'), 'ruins': load_image('ruins.png'),
               "evacuation point": load_image('escape.png')}  # словарь с изображениями тайлов
tile_types = {'black': 'empty', 'grey': 'wall', 'brown': 'tower', 'red': 'mine', 'blue': 'detector', 'white': 'shield',
              'golden': 'evacuation point', 'green': 'ruins'}  # словарь соответствия цвета и типа тайла

tile_width = tile_height = 50


def load_level(username):  # считывает карту из файла
    filename = "data/progress/" + username + "/map.txt"
    with open(filename, 'r') as mapFile:
        level_map = [line.split() for line in mapFile]
    return level_map


def generate_level(level, tiles_all_groups):  # отрисовывает поле
    towers_dict = dict()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'grey':
                Tile('wall', x, y, 'wall', tiles_all_groups)
            elif level[y][x] == 'brown':
                towers_dict[(y, x)] = Tile('tower', x, y, 'tower', tiles_all_groups)
            else:
                if level[y][x] in tile_types.keys() and tile_types[level[y][x]] in tile_images:
                    Tile(tile_types[level[y][x]], x, y, tile_types[level[y][x]],
                         tiles_all_groups)
                else:
                    Tile('empty', x, y, 'checkpoint', tiles_all_groups)
    return towers_dict


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_image, pos_x, pos_y, tile_type, tiles_all_group):
        super().__init__(*tiles_all_group)
        self.image = tile_images[tile_image]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.type = tile_type


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
    print("quited")
    sys.exit()
