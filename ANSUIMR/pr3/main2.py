
import sys, pygame
from builtins import hasattr

import numpy as np
import math
import json

class Ngon: #многоугольник
    def __init__(self):
        self.pts=[]
        self.closed=False
    def add_pt(self, p): self.pts.append(p)
    def clear(self): self.pts=[]
    def save(self, name):
        with open(name, "w") as f:
            f.write(json.dumps({'pts': self.pts, 'closed': self.closed}))
    def load(self, name):
        with open(name, "r") as f:
            d = json.loads(f.read())
            self.pts=d["pts"]
            self.closed=d["closed"]

    def draw(self, screen):
        if len(self.pts)>1:
            pygame.draw.lines(screen, (0,0,255), self.closed, self.pts, 2)
        for p in self.pts:
            pygame.draw.circle(screen, (0,0,255), p, 5, 2)


pygame.font.init()
def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

def rot(v, ang): #поворот вектора на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def lim_ang(ang): #ограничение угла в пределах +/-pi
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rot_arr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2): #расстояние между точками
    return np.linalg.norm(np.subtract(p1, p2))

def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rot_arr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

sz = (800, 600)

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps

    ngon=Ngon()
    p_last=None

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    ngon.clear()
                if ev.key == pygame.K_s:
                    ngon.save("ngon.txt")
                if ev.key == pygame.K_o:
                    ngon.load("ngon.txt")
            if ev.type == pygame.MOUSEBUTTONDOWN:
                all_keys = pygame.key.get_pressed()
                p = ev.pos
                if all_keys[pygame.K_LCTRL] and p_last:
                    p1 = [ev.pos[0], p_last[1]] #вертикаль
                    p2 = [p_last[0], ev.pos[1]] #горизонталь
                    d1, d2 = dist(ev.pos, p1), dist(ev.pos, p2)
                    if min(d1, d2)<50: p = p1 if d1<d2 else p2 #свободный наклон
                ngon.add_pt(p)
                p_last=p


        screen.fill((255, 255, 255))
        ngon.draw(screen)
        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024