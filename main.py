import time

import pygame
import pygame.time

pygame.init()
size = (800, 800)
sc = pygame.display.set_mode(size)
pygame.display.init()
pygame.display.set_caption('Очень жаль, что вас убило...')

font = pygame.font.SysFont('segoescript', 50)
colt = (255, 0, 0)
txt1 = font.render('You', 1, colt)
w1, h1 = txt1.get_size()
txt2 = font.render('have', 1, colt)
w2, h2 = txt1.get_size()
txt3 = font.render('been', 1, colt)
w3, h3 = txt1.get_size()
txt4 = font.render('destroyed', 1, colt)
w4, h4 = txt1.get_size()

x1, y1 = 50, 350
x2, y2 = 180, 350
x3, y3 = 340, 350
x4, y4 = 500, 350
kx1,kx2,kx3,kx4,ky1,ky2,ky3,ky4 = 1,-2,2,-1,3,-3,-1,-2
c=1
fps = 60
clock = pygame.time.Clock()

sc.blit(txt1, (x1, y1))
sc.blit(txt2, (x2, y2))
sc.blit(txt3, (x3, y3))
sc.blit(txt4, (x4, y4))


while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            quit()

    clock.tick(fps)

    sc.blit(txt1, (x1, y1))
    sc.blit(txt2, (x2, y2))
    sc.blit(txt3, (x3, y3))
    sc.blit(txt4, (x4, y4))
    pygame.display.update()

    if c:
        time.sleep(3)
        c=0

    x1, y1 = x1 + kx1, y1 + ky1
    if x1 < 0 or x1+w1 > 800:
        kx1 = -kx1
    if y1 < 0 or y1+h1 > 800:
        ky1 = -ky1

    x2, y2 = x2 + kx2, y2 + ky2

    if x2 < 0 or x2 + w2 > 800:
        kx2 = -kx2
    if y2 < 0 or y2 + h2 > 800:
        ky2 = -ky2

    x3, y3 = x3 + kx3, y3 + ky3

    if x3 < 0 or x3 + w3 > 800:
        kx3 = -kx3
    if y3< 0 or y3 + h3 > 800:
        ky3 = -ky3

    x4, y4 = x4 + kx4, y4 + ky4

    if x4 < 0 or x4 + w4 > 800:
        kx4 = -kx4
    if y4 < 0 or y4 + h4 > 800:
        ky4 = -ky4

    pygame.display.update()
    sc.fill((0, 0, 0))