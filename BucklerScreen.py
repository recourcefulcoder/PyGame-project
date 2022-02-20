import pygame


def buckler_screen():
    pygame.init()
    size = (800, 600)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Ты получаешь щит!')
    font1 = pygame.font.SysFont('segoescript', 40)
    font2 = pygame.font.SysFont('segoescript', 20)
    text1 = font1.render('Ты получаешь щит!', True, (255, 255, 0))
    text2 = font2.render('Он убережет тебя от', True, (255, 255, 0))
    text3 = font2.render('подрыва на следующей мине', True, (255, 255, 0))
    screen.blit(text1, (size[0] / 2 - text1.get_size()[0] // 2, 150))
    screen.blit(text2, (size[0] / 2 - text2.get_size()[0] // 2, 250))
    screen.blit(text3, (size[0] / 2 - text3.get_size()[0] // 2, 300))
    pygame.display.flip()


if __name__ == '__main__':
    buckler_screen()
    while True:
        print(1.1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
