import sys, pygame
import numpy as np
import math

pygame.font.init()

def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

def rot(v, ang):  # поворот вектора на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def lim_ang(ang):  # ограничение угла в пределах +/-pi
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rot_arr(vv, ang):  # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2):  # расстояние между точками
    return np.linalg.norm(np.subtract(p1, p2))

def draw_rot_rect(screen, color, pc, w, h, ang):  # точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [[- w / 2, - h / 2], [+ w / 2, - h / 2], [+ w / 2, + h / 2], [- w / 2, + h / 2]]
    pts = np.add(rot_arr(pts, ang), pc)
    pygame.draw.polygon(screen, color, pts, 2)

class Robot:
    def __init__(self, x, y, alpha):
        self.x, self.y, self.alpha = x, y, alpha
        self.L, self.W = 1, 0.6 #габариты в метрах
        self.speed=0 #линейная скорость
        self.steer=0 #руление
        self.A=3 #стремление к цели
        self.B=2 #страх препятствий
        self.traj=[] #траектория
    def get_pos(self): return (self.x, self.y)
    def draw(self, screen, SCALE, SHIFT):
        def tr(pt):  # transform pt from m to px
            return (SCALE * (pt[0] - SHIFT[0]), SCALE * (pt[1] - SHIFT[1]))
        p = np.array(tr(np.array(self.get_pos())))
        draw_rot_rect(screen, (0,0,0), p, self.L*SCALE, self.W*SCALE, self.alpha)
        dx, dy = self.L/3*SCALE, self.W/3*SCALE
        dd=[[-dx,-dy],[-dx,dy],[dx,-dy],[dx,dy]]
        dd=rot_arr(dd, self.alpha)
        for d, k in zip(dd, [0,0,1,1]):
            draw_rot_rect(screen, (0,0,0), p+d, self.L/5*SCALE, self.W/5*SCALE, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            pygame.draw.line(screen, (0,0,255), tr(self.traj[i]), tr(self.traj[i+1]), 1)
    def sim(self, dt):
        delta=rot([self.speed*dt, 0], self.alpha)
        self.x, self.y = self.x+delta[0], self.y+delta[1]
        if self.steer!=0: self.alpha+=self.speed*dt/(self.L/self.steer)
        p = self.get_pos()
        if len(self.traj)==0 or dist(p, self.traj[-1])>0.1: self.traj.append(p)
    def goto(self, pos, obsts, dt):
        #1 - оценка углового рассогласования на цель
        v = np.subtract(pos, self.get_pos())
        a_goal=math.atan2(v[1], v[0])
        da=lim_ang(a_goal-self.alpha)
        da2=0
        #2 - оценка углового рассогласования от препятствий
        if len(obsts):
            dd = [dist(self.get_pos(), o.get_pos()) for o in obsts]
            i = np.argmin(dd)
            v2 = np.subtract(obsts[i].get_pos(), self.get_pos())
            a_obst = math.atan2(v2[1], v2[0])
            da2 = lim_ang(a_obst - self.alpha)
        #3 - объединение двух компонент управления
        self.steer += (self.A*da - self.B*da2)*dt
        self.steer=max(-1, min(1, self.steer))
        self.speed=1