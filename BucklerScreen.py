import pygame, os, sys
from pygame import image as pi


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


def buckler_screen():
    pygame.init()
    size = (800, 600)
    screen = pygame.display.set_mode(size)
    screen.blit(load_image('win_bg_image.jpg'), (0, 0))
    pygame.display.set_caption('Вы получили щит!')
    font1 = pygame.font.SysFont('segoescript', 40)
    font2 = pygame.font.SysFont('segoescript', 20)
    text1 = font1.render('Вы получили щит!', True, (255, 255, 0))
    text2 = font2.render('Он убережет вас от', True, (255, 255, 0))
    text3 = font2.render('подрыва на следующей мине', True, (255, 255, 0))
    screen.blit(text1, (size[0] / 2 - text1.get_size()[0] // 2, 150))
    screen.blit(text2, (size[0] / 2 - text2.get_size()[0] // 2, 250))
    screen.blit(text3, (size[0] / 2 - text3.get_size()[0] // 2, 300))
    pygame.display.flip()


if __name__ == '__main__':
    buckler_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
