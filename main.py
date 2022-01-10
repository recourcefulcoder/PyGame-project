import time

import pygame
import pygame.time

pygame.init()
size = (600, 600)
sc = pygame.display.set_mode(size)
pygame.display.init()
pygame.display.set_caption('Очень жаль, что вас убило...')

font = pygame.font.SysFont('segoescript', 40)
colt = (255, 0, 0)
txt1 = font.render('You', 1, colt)
w1, h1 = txt1.get_size()
txt2 = font.render('have', 1, colt)
w2, h2 = txt1.get_size()
txt3 = font.render('been', 1, colt)
w3, h3 = txt1.get_size()
txt4 = font.render('destroyed', 1, colt)
w4, h4 = txt1.get_size()

x1, y1 = 30, 250
x2, y2 = 130, 250
x3, y3 = 250, 250
x4, y4 = 370, 250
kx1, kx2, kx3, kx4, ky1, ky2, ky3, ky4 = 1, -2, 2, -1, 3, -3, -1, -2
c = 1
y = 0
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
        x1, y1 = 30, 0
        x2, y2 = 130, 600
        x3, y3 = 250, 0
        x4, y4 = 370, 600

        while y != 300:
            clock.tick(fps)
            y1, y3 = y1 + 1, y3 + 1
            y2, y4 = y2 - 1, y4 - 1
            sc.blit(txt1, (x1, y1))
            sc.blit(txt2, (x2, y2))
            sc.blit(txt3, (x3, y3))
            sc.blit(txt4, (x4, y4))
            pygame.display.update()
            sc.fill((0, 0, 0))
            y += 1
        c = 0
        time.sleep(3)

    x1, y1 = x1 + kx1, y1 + ky1
    if x1 < 0 or x1 + w1 > 500:
        kx1 = -kx1
    if y1 < 0 or y1 + h1 > 500:
        ky1 = -ky1

    x2, y2 = x2 + kx2, y2 + ky2

    if x2 < 0 or x2 + w2 > 500:
        kx2 = -kx2
    if y2 < 0 or y2 + h2 > 500:
        ky2 = -ky2

    x3, y3 = x3 + kx3, y3 + ky3

    if x3 < 0 or x3 + w3 > 500:
        kx3 = -kx3
    if y3 < 0 or y3 + h3 > 500:
        ky3 = -ky3

    x4, y4 = x4 + kx4, y4 + ky4

    if x4 < 0 or x4 + w4 > 500:
        kx4 = -kx4
    if y4 < 0 or y4 + h4 > 500:
        ky4 = -ky4

    pygame.display.update()
    sc.fill((0, 0, 0))
