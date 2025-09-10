
import sys, pygame
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
    pts = [[- w/2, - h/2], [+ w/2, - h/2], [+ w/2, + h/2], [- w/2, + h/2]]
    pts = np.add(rot_arr(pts, ang), pc)
    pygame.draw.polygon(screen, color, pts, 2)

sz = (800, 600)

class Obstacle:
    def __init__(self, x, y):
        self.x, self.y, self.R = x, y, 30
    def get_pos(self): return (self.x, self.y)
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,0), self.get_pos(), self.R, 2)

class Robot:
    def __init__(self, x, y, alpha):
        self.x, self.y, self.alpha = x, y, alpha
        self.L, self.W = 70, 40
        self.speed=0 #линейная скорость
        self.steer=0 #руление
        self.traj=[] #траектория
    def get_pos(self): return (self.x, self.y)
    def draw(self, screen):
        p = np.array(self.get_pos())
        draw_rot_rect(screen, (0,0,0), p, self.L, self.W, self.alpha)
        dx, dy = self.L/3, self.W/3
        dd=[[-dx,-dy],[-dx,dy],[dx,-dy],[dx,dy]]
        dd=rot_arr(dd, self.alpha)
        for d, k in zip(dd, [0,0,1,1]):
            draw_rot_rect(screen, (0,0,0), p+d, self.L/5, self.W/5, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            pygame.draw.line(screen, (0,0,255), *self.traj[i:i+2], 1)

    def sim(self, dt):
        delta=rot([self.speed*dt, 0], self.alpha)
        self.x, self.y = self.x+delta[0], self.y+delta[1]
        if self.steer!=0: self.alpha+=self.speed*dt/(self.L/self.steer)
        p = self.get_pos()
        if len(self.traj)==0 or dist(p, self.traj[-1])>10: self.traj.append(p)

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps
    t=0

    robot=Robot(200, 350, 0.1)
    robot.speed=50
    # robot.steer=0.5

    obsts=[Obstacle(200, 200), Obstacle(400, 300), Obstacle(270, 350), Obstacle(250, 450)]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        robot.steer = 0.7 * math.sin(2 * t)
        robot.sim(dt)

        screen.fill((255, 255, 255))
        robot.draw(screen)
        for o in obsts: o.draw(screen)

        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)
        t+=dt

main()

#template file by S. Diane, RTU MIREA, 2024
