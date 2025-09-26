import sys, pygame
from ctypes import py_object

import numpy as np
import math

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

def find_route(p_start, p_finish, pts):
    res=[p_start]
    buf=[*pts]
    while len(buf):
        dd=[dist(res[-1], p) for p in buf]
        i=np.argmin(dd)
        res.append(buf[i])
        del buf[i]
    res.append(p_finish)
    return res

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps

    pts = [[200, 200], [300, 400], [400, 200], [250, 300], [220, 380]]
    p_start = [50, 50]
    p_finish = [500, 500]

    p_last=(0,0)
    st, en=False, False

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if dist(ev.pos, p_start)<10: st=True
                if dist(ev.pos, p_finish)<10: en=True
            if ev.type == pygame.MOUSEBUTTONUP:
                st, en = False, False
            if ev.type == pygame.MOUSEMOTION:
                dx, dy = ev.pos[0] - p_last[0], ev.pos[1] - p_last[1]
                if st: p_start=[p_start[0]+dx, p_start[1]+dy]
                if en: p_finish=[p_finish[0]+dx, p_finish[1]+dy]
                p_last=ev.pos

        route=find_route(p_start, p_finish, pts)

        screen.fill((255, 255, 255))
        for p in pts:
            pygame.draw.circle(screen, (100,100,100), p, 5, 2)
        pygame.draw.circle(screen, (255,0,0), p_start, 10, 2)
        pygame.draw.circle(screen, (0,0,255), p_finish, 10, 2)

        pygame.draw.lines(screen, (255,0,255), False, route[1:-1], 2)
        pygame.draw.line(screen, (255,180,255), *route[:2], 2)
        pygame.draw.line(screen, (255,180,255), *route[-2:], 2)

        L=sum(dist(p1, p2) for p1, p2 in zip(route[1:], route[:-1]))
        draw_text(screen, f"Len = {L:.2f}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024