import pygame


def detector_screen():
    pygame.init()
    size = (800, 600)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Ты получаешь металлоискатель!')
    font1 = pygame.font.SysFont('segoescript', 30)
    font2 = pygame.font.SysFont('segoescript', 20)
    text1 = font1.render('Ты получаешь металлоискатель!', True, (255, 255, 0))
    text2 = font2.render('Он покажет тебе,', True, (255, 255, 0))
    text3 = font2.render('где расположены мины.', True, (255, 255, 0))
    screen.blit(text1, (size[0] / 2 - text1.get_size()[0] // 2, 150))
    screen.blit(text2, (size[0] / 2 - text2.get_size()[0] // 2, 250))
    screen.blit(text3, (size[0] / 2 - text3.get_size()[0] // 2, 300))
    pygame.display.flip()


if __name__ == '__main__':
    detector_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()