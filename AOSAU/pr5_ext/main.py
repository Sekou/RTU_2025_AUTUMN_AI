
import sys, pygame
import numpy as np
import math

K_FORCE=1000000

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

def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина, высота и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rot_arr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

#отрисовка стрелки по 2 точкам
def arrow2(screen, color, p0, p1, w):
    angle=math.atan2(p1[1]-p0[1],p1[0]-p0[0])
    p2 = [p1[0] - 7 * math.cos(angle + 0.5), p1[1] - 7 * math.sin(angle + 0.5)]
    p3 = [p1[0] - 7 * math.cos(angle - 0.5), p1[1] - 7 * math.sin(angle - 0.5)]
    for a,b in [[p0, p1], [p1, p2], [p1, p3]]: pygame.draw.line(screen, color, a, b, w)

def draw_vector_field(screen, objs, W, H, step=50):
    for iy in np.arange(step, H, step):
        for ix in np.arange(step, W, step):
            p=(ix, iy)
            pygame.draw.circle(screen, (0,0,0), p, 3, 2)
            f=np.zeros(2) #сила которая действет на единичный заряд
            for o in objs:
                d=dist(p, o.get_pos())
                F=K_FORCE*1*o.charge/d**2 #формула Кулона - скаляр                
                fvec=np.array(np.subtract(p, o.get_pos()), dtype=np.float64)
                fvec*=F/np.linalg.norm(fvec)
                f+=fvec
            F1=np.linalg.norm(f)
            F2=min(40, max(-40, 10*F1))
            f*=F2/F1
            arrow2(screen, (200,0,200), p, p+f, 1)

sz = (800, 600)

class Obj: #robot, goal, obstacle
    def __init__(self, x, y, charge, mass, r=20):
        self.p, self.charge, self.mass, self.r = (x, y), charge, mass, r
        self.a=np.zeros(2)
        self.v=np.zeros(2)
        self.traj=[]
    def get_pos(self): return self.p
    def draw(self, screen):
        c=(255,0,0) if self.charge>0 else (0,0,255)
        pygame.draw.circle(screen, c, self.get_pos(), self.r, 2)
        for i in range(1, len(self.traj)):
            pygame.draw.line(screen, (0,255,0), self.traj[i-1], self.traj[i], 1)
    def sim(self, dt, objs):
        for o in objs:
            if o==self: continue
            d=dist(self.get_pos(), o.get_pos())
            F=K_FORCE*self.charge*o.charge/d**2 #формула Кулона - скаляр
            fvec=np.array(np.subtract(self.get_pos(), o.get_pos()), dtype=np.float64)
            fvec*=F/np.linalg.norm(fvec)
            a=fvec/self.mass #ускорение
            self.v+=a*dt
            self.v*=0.995
            self.p+=self.v*dt

        self.traj.append([*self.get_pos()])

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps   

    robot = Obj(50,50, 1, 1, 15) #робот
    goal = Obj(500,500, -1, 1000) #цель
    obst = Obj(290,300, 0.1, 1000) #препятствие

    objs=[robot, goal, obst]

    FINISHED=False

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")     

        if not FINISHED:
            for o in objs: o.sim(dt, objs)

        if dist(robot.get_pos(), goal.get_pos())<30:
            print("Finished")
            FINISHED=True

        screen.fill((255, 255, 255))    

        draw_vector_field(screen, [o for o in objs if o!=robot], *sz, 50)

        for o in objs: o.draw(screen)

        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024