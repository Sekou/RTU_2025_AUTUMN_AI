from dis import dis
import itertools
import sys, pygame
import numpy as np
import math

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))

sz = (800, 600)

def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def limAng(ang):
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rotArr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))

def drawRotRect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

def get_segm_intersection(A, B, C, D): #поиск точки пересечения двух отрезков
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = A, B, C, D
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0: return None  # отрезки параллельны или совпадают
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1: return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None

class Line:
    def __init__(self, is_closed): 
        self.pts=[]
        self.is_closed=is_closed
    def add_pt(self, pt):
        self.pts.append(pt)
    def iter_segments(self):
        i_start=0 if self.is_closed else 1 
        for i in range(i_start, len(self.pts)):
            yield [self.pts[i-1], self.pts[i]]
    def draw(self, screen):
        i_start=0 if self.is_closed else 1 
        for i in range(i_start, len(self.pts)):
            pygame.draw.line(screen, (0,0,0), self.pts[i-1], self.pts[i], 2)

class Lidar:
    def __init__(self, n_rays):
        self.nrays=n_rays
        self.x, self.y=0.0,0.0
        self.ang=0
        self.L=200
        self.pp=[]
        self.vals=[self.L]*self.nrays
    def draw(self, screen):
        p1=(self.x, self.y)
        p2=np.array(p1)+ (10*math.cos(self.ang), 10*math.sin(self.ang))
        pygame.draw.line(screen, (255,0,0), p1, p2, 4)
        dang=2*math.pi/self.nrays
        for i in range(self.nrays):
            a=self.ang+i*dang
            p2=np.array(p1) + (self.L*math.cos(a), self.L*math.sin(a))
            pygame.draw.line(screen, (255,0,0), p1, p2, 2)
        for p in self.pp:
            pygame.draw.circle(screen, (255,0,0), p, 3, 2)
    def sim(self, dt, lines):
            p1=(self.x, self.y)
            dang=2*math.pi/self.nrays
            pp=[]
            self.vals=[self.L]*self.nrays
            for i in range(self.nrays):
                buffer=[]
                for ln in lines:
                    for segm in ln.iter_segments():
                        a=self.ang+i*dang
                        p2=np.array(p1) + (self.L*math.cos(a), self.L*math.sin(a))
                        p=get_segm_intersection(p1, p2, segm[0], segm[1])
                        if p is not None: buffer.append(p)
                if len(buffer):
                    dd=[dist(p, p1) for p in buffer]
                    pp.append(buffer[np.argmin(dd)])
                    self.vals[i]=dist(buffer[np.argmin(dd)], p1)

            self.pp=pp

class Robot:
    def __init__(self, x, y, alpha):
        self.x=x
        self.y=y
        self.alpha=alpha
        self.L=70
        self.W=40
        self.speed=0
        self.steer=0
        self.traj=[] #точки траектории
        self.control_log=[] #журнал управления
        self.lidar=Lidar(20)
        
    def getPos(self):
        return [self.x, self.y]

    def clear(self):
        self.traj = []
        self.vals1 = []
        self.vals2 = []

    def draw(self, screen):
        p=np.array(self.getPos())
        drawRotRect(screen, (0,0,0), p,
                    self.L, self.W, self.alpha)
        dx=self.L/3
        dy=self.W/3
        dd=[[-dx,-dy], [-dx,dy], [dx,-dy], [dx,dy]]
        dd=rotArr(dd, self.alpha)
        kRot=[0,0,1,1]
        for d, k in zip(dd, kRot):
            drawRotRect(screen, (0, 0, 0), p+d,
                        self.L/5, self.W/5, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            pygame.draw.line(screen, (0,0,255), self.traj[i], self.traj[i+1], 1)

        self.lidar.draw(screen)

    def sim(self, dt, lines, time):
        self.lidar.x=self.x
        self.lidar.y=self.y
        self.lidar.ang=self.alpha
        self.lidar.sim(dt, lines)
        str_lidar=" ".join([f"{int(v)}" for v in self.lidar.vals])

        self.control_log.append(f"{time:.3f} {self.speed:.0f} {self.steer:.2f} {self.x:.0f} {self.y:.0f} {self.alpha:.2f} {str_lidar}")

        self.addedTrajPt = False
        delta=[self.speed*dt, 0]
        delta=rot(delta, self.alpha)
        self.x+=delta[0]
        self.y+=delta[1]
        if self.steer!=0:
            R = self.L/self.steer
            da = self.speed*dt/R
            self.alpha+=da

        p=self.getPos()
        if len(self.traj)==0 or dist(p, self.traj[-1])>10:
            self.traj.append(self.getPos())
            self.addedTrajPt=True

    def goto(self, pos, dt):
        v=np.subtract(pos, self.getPos())
        aGoal=math.atan2(v[1], v[0])
        da=limAng(aGoal-self.alpha)
        self.steer += 0.5 * da * dt
        maxSteer=1
        if self.steer > maxSteer: self.steer = maxSteer
        if self.steer < -maxSteer: self.steer = -maxSteer
        self.speed = 50

if __name__=="__main__":
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot=Robot(200, 150, 0)

    lines=[]

    MODE="manual"
    #MODE="neural"

    def make_border():
        ln=Line(False)
        ln.add_pt((50,50))
        ln.add_pt((750,50))
        lines.append(ln)

    def make_obstacle(x, y):
        obst=Line(True)
        obst.add_pt((x-40,y-20))
        obst.add_pt((x+40,y-20))
        obst.add_pt((x+40,y+20))
        obst.add_pt((x-40,y+20))
        lines.append(obst)

    make_border()
    make_obstacle(100,90)
    make_obstacle(200,90)
    make_obstacle(400,90)
    make_obstacle(500,90)

    time=0
    #goal = [400,200]

    model=None

    MODE="manual"

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_e: robot.speed=50
                if ev.key==pygame.K_w: robot.speed=20
                if ev.key==pygame.K_s: robot.speed=-20
                if ev.key==pygame.K_a: robot.steer=-0.5
                if ev.key==pygame.K_d: robot.steer=+0.5
                if ev.key==pygame.K_z: robot.speed=robot.steer=0
                if ev.key==pygame.K_r: 
                    robot=Robot(200, 150, 0)

                if ev.key==pygame.K_1: 
                    with open("log.txt", "w") as f:
                        f.write("\n".join(robot.control_log))
                if ev.key==pygame.K_n: 
                    if MODE!="neural":
                        MODE="neural"
                        from net import createModel
                        model=createModel()
                        model.load_weights("net.weights.h5")
                    else: 
                        MODE="manual"
                        model=None

        dt=1/fps
        screen.fill((255, 255, 255))

        #robot.goto(goal, dt)

        if model:
            prev_lidars=[]
            if len(prev_lidars)==0: prev_lidars=robot.lidar.vals
            vec=[robot.y/10, robot.alpha]+[v/100 for v in prev_lidars]+[v/100 for v in robot.lidar.vals]
            result=model.predict(np.array([vec]))
            print(result)
            robot.speed=result[0][0]
            robot.steer=result[0][1]
            prev_lidars=robot.lidar.vals

        robot.sim(dt, lines, time)

        robot.draw(screen)
        for ln in lines: ln.draw(screen)
        
        #pygame.draw.circle(screen, (255,0,0), goal, 5, 2)

        drawText(screen, f"Time = {time:.3f}", 5, 5)
        drawText(screen, f"Mode = {MODE}", 5, 25)
       
        pygame.display.flip()
        timer.tick(fps)
        time+=dt

#template file by S. Diane, RTU MIREA, 2024