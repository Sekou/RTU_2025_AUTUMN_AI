
from cmath import atan
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

# проверяем, находится ли точка внутри многоугольника
def pt_inside_ngon(point, vertices):
    (x, y), c = point, 0
    for i in range(len(vertices)):
        (x1, y1), (x2, y2) = vertices[i-1], vertices[i]
        if min(y1,y2) <= y < max(y1, y2):
            ratio = (y - y1) / (y2 - y1)
            c ^= (x - x1 < ratio*(x2 - x1))
    return c

sz = (800, 600)
SAFETY_RADIUS = 200

class Robot:
    def __init__(self, x, y):
        self.radius=15
        self.color=(0,0,0)
        self.x, self.y, self.a=x,y,0
        self.vlin, self.vrot=0,0
        self.v=[0,0]
        self.collision_cones=[] #конусы скоростей столкновения
        self.obsts=[]
        self.debug_pts=[]
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen, debug=False):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
        if debug:
            cc=self.collision_cones
            for c in cc: 
                p0, p1, p2=c[0], c[1], c[2]
                for s in [[p0,p1],[p1,p2],[p2,p0]]:
                    pygame.draw.line(screen, (0,255,0), *s, 2)
            for obst in self.obsts: pygame.draw.circle(screen, (255,0,0), obst.get_pos(), obst.radius+2, 2)
            for p in self.debug_pts: pygame.draw.circle(screen, (0,255,0), p, 3, 2)
            pygame.draw.circle(screen, (200,200,200), self.get_pos(), SAFETY_RADIUS, 1)
    def find_cones(self):
        self.collision_cones=[]
        self.debug_pts=[]
        for obst in self.obsts: 
            L=dist(self.get_pos(), obst.get_pos())
            x=(L**2 - obst.radius**2)**0.5
            alpha=math.atan(obst.radius/x)
            beta = math.atan2(obst.y-self.y, obst.x-self.x)
            p0=np.array(self.get_pos())
            p1,p2=p0+rot([x,0], beta+alpha), p0+rot([x,0], beta-alpha)
            self.debug_pts.append(p1)
            self.debug_pts.append(p2)
            delta=np.add(self.v, obst.v)*0.5
            p0_, p1_, p2_=p0+delta, p1+delta, p2+delta
            c=[p0_, p1_, p2_]
            self.collision_cones.append(c)
    def get_obstacles(self, objs):
        objs_=[o for o in objs if o!=self and dist(o.get_pos(), self.get_pos())<SAFETY_RADIUS]
        return objs_    
    def sim(self, dt, objs):
        s,c=math.sin(self.a), math.cos(self.a)
        self.x+=c*self.vlin*dt
        self.y+=s*self.vlin*dt
        self.a+=self.vrot*dt
        self.obsts=self.get_obstacles(objs)
        self.v=[c*self.vlin, s*self.vlin] #for collision cones
        self.find_cones()

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20
    robots = [Robot(200, 200), Robot(250, 250), Robot(250, 350)]
    robot=robots[0]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w: robot.vlin=50
                if ev.key == pygame.K_s: robot.vlin=-50
                if ev.key == pygame.K_a: robot.vrot=-1
                if ev.key == pygame.K_d: robot.vrot=+1
                if ev.key == pygame.K_z: robot.vlin=robot.vrot=0

        dt=1/fps
        for r in robots: r.sim(dt, robots)

        screen.fill((255, 255, 255))
        for i,r in enumerate(robots): r.draw(screen, i==0)
        
        drawText(screen, f"D = {dist(robots[0].get_pos(), robots[1].get_pos())}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024