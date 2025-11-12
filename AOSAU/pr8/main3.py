
from select import select
import sys, pygame
import numpy as np
import math

pygame.font.init()
def drawText(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    font = pygame.font.SysFont('Comic Sans MS', sz)
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))

def rot(v, ang): #поворот вектора на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def limAng(ang): #ограничение угла в пределах +/-pi
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rotArr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2): #расстояние между точками
    return np.linalg.norm(np.subtract(p1, p2))

sz = (800, 600)

def contains(obj, bb):
    x, y=obj.get_pos()
    return bb[0]<x<bb[0]+bb[2] and bb[1]<y<bb[1]+bb[3]

class VolleyballCourt:
    def __init__(self, x0, y0, w, h):
        self.x0, self.y0, self.w, self.h=x0, y0, w, h
    def get_bb(self):#bounding box
        return [self.x0, self.y0, self.w, self.h]
    def get_bb1(self):#left area
        return [self.x0, self.y0, self.w/2, self.h]
    def get_bb2(self):#right area
        return [self.x0+self.w/2, self.y0, self.w/2, self.h]
    def draw(self, screen):
        pygame.draw.rect(screen, (0,0,0), self.get_bb1(), 2)
        pygame.draw.rect(screen, (0,0,0), self.get_bb2(), 2)

class Ball:
    def __init__(self, x, y):
        self.radius0=10
        self.radius=self.radius0
        self.color=(0,0,0)
        self.x, self.y=x,y
        self.z, self.vz=0,0
        self.vlin=0
        self.a=0
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.get_pos(), self.radius, 2)
    def sim(self, dt):
        s,c=math.sin(self.a), math.cos(self.a)
        if self.z>1:
            self.x+=c*self.vlin*dt; self.y+=s*self.vlin*dt
        self.z=max(0,self.z+self.vz*dt)
        self.vz+=-9.8*dt

class Robot:
    def __init__(self, x, y):
        self.radius=20
        self.color=(0,0,0)
        self.x, self.y, self.a=x,y,0
        self.vlin, self.vrot=0,0
        self.attached_obj=None
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
    def sim(self, dt):
        s,c=math.sin(self.a), math.cos(self.a)
        self.x+=c*self.vlin*dt; self.y+=s*self.vlin*dt; self.a+=self.vrot*dt
        if self.attached_obj: self.attached_obj.x, self.attached_obj.y = self.x, self.y
    def catches_obj(self, obj):
        return dist(obj.get_pos(), self.get_pos())<self.radius
    def goto_obj(self, obj, dt):
        x, y=obj.get_pos()
        dx, dy = x-self.x, y-self.y
        gamma=math.atan2(dy, dx)
        da=limAng(gamma-self.a)
        self.a+=0.5*da*dt
        self.vlin=10
    def stop(self):
        self.vrot=self.vlin=0

def show_color(obj, vc):
    if contains(obj, vc.get_bb1()): obj.color=(255,0,0)
    elif contains(obj, vc.get_bb2()): obj.color=(0,0,255)
    else: obj.color=(0,0,0)

def ball_is_near_player(ball, robots):
    return any([r.catches_obj(ball) for r in robots])

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20
    robots =[Robot(300, 200), Robot(500, 400)]
    ind_robot=0
    score1=0 #очки первой команды
    score2=0 #очки второй команды
    last_loose=0 #1 или 2
    game_started=False

    vc = VolleyballCourt(20, 20, sz[0]-40, sz[1]-40)
    ball = Ball(300, 400)

    while True:
        robot=robots[ind_robot]
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w: robot.vlin=50
                if ev.key == pygame.K_s: robot.vlin=-50
                if ev.key == pygame.K_a: robot.vrot=-1
                if ev.key == pygame.K_d: robot.vrot=+1
                if ev.key == pygame.K_z: robot.stop()
                if ev.key == pygame.K_SPACE: 
                    if robot.attached_obj:
                        robot.attached_obj.vlin=50
                        robot.attached_obj.vz=20
                        robot.attached_obj.a=robot.a
                        robot.attached_obj=None
                        game_started=True
                if ev.key == pygame.K_t: 
                    robot.attached_obj=ball
                if ev.key == pygame.K_1: ind_robot=0
                if ev.key == pygame.K_2: ind_robot=1

        dt=1/fps
        for r in robots: 
            r.sim(dt)
            if not r.attached_obj:
                A = contains(r, vc.get_bb1()) and contains(ball, vc.get_bb1()) 
                B = contains(r, vc.get_bb2()) and contains(ball, vc.get_bb2()) 
                if A or B: r.goto_obj(ball, dt)
                else: r.stop()
        ball.sim(dt)

        catch=ball_is_near_player(ball, robots)
        if game_started and ball.z<1 and not catch:
            if last_loose!=1 and contains(ball, vc.get_bb1()): 
                score2+=1
                last_loose=1
            elif last_loose!=2 and contains(ball, vc.get_bb2()): 
                score1+=1
                last_loose=2

        for o in [robot,ball]: show_color(o, vc)

        screen.fill((255, 255, 255))
        vc.draw(screen)
        for r in robots: r.draw(screen)
        ball.draw(screen)
        drawText(screen, f"Index = {ind_robot};"+ 
        f"Score1 = {score1}; Score2 = {score2}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024