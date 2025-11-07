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

SCALE = 50 #px/m

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
    pts = np.add(pts, pc)*SCALE
    pygame.draw.polygon(screen, color, pts, 2)

def drawLine(screen, color, p1, p2, w=2):
    p1, p2=np.array(p1)*SCALE, np.array(p2)*SCALE
    pygame.draw.line(screen, color, p1, p2, w)

def drawCircle(screen, color, p, radius, w=2):
    pygame.draw.circle(screen, color, np.array(p)*SCALE, radius, 2)

def drawGrid(screen, sz=50, step=1):
    for iy in np.arange(0, sz, step):
        drawLine(screen, (200,200,200), (0,iy), (sz,iy), 1)
    for ix in np.arange(0, sz, step):
        drawLine(screen, (200,200,200), (ix, 0), (ix, sz), 1)

class Robot:
    def __init__(self, x, y, alpha):
        self.t, self.t_=0,0
        self.x, self.x_=x,x
        self.y, self.y_=y,y
        self.alpha, self.alpha_=alpha,alpha
        self.L=4
        self.W=1.6
        self.mass=1000
        self.I=0
        self.speed=0
        self.steer=0
        self.traj=[] #точки траектории
        self.E1,self.E2,self.E=0,0,0

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
                        self.L/7, self.W/7, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            drawLine(screen, (0,0,255), self.traj[i], self.traj[i+1], 1)

    def calcEnergy(self):
        dt=self.t-self.t_
        if dt==0: return 0
        d=np.array((self.x, self.y))-np.array((self.x_, self.y_))
        v=d/dt
        self.E1=self.mass*(v@v)/2
        w=(self.alpha-self.alpha_)/dt
        self.I=1/12*self.mass*(self.L**2+self.W**2)
        self.E2=self.I * w**2 / 2
        self.E=self.E1+self.E2
        return self.E

    def sim(self, time, dt):
        self.t=time 

        self.addedTrajPt = False
        delta=[self.speed*dt, 0]
        delta=rot(delta, self.alpha)
        self.x+=delta[0]
        self.y+=delta[1]
        if self.steer!=0:
            R = self.L/self.steer
            da = self.speed*dt/R
            self.alpha+=da

        self.calcEnergy()
        self.x_, self.y_, self.alpha_=self.x, self.y, self.alpha
        self.t_=self.t

        p=self.getPos()
        if len(self.traj)==0 or dist(p, self.traj[-1])>0.1:
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
        self.speed = 10

if __name__=="__main__":
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot=Robot(2, 2, 1)

    time=0
    goal = [6,4]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
        dt=1/fps
        screen.fill((255, 255, 255))

        robot.goto(goal, dt)

        robot.sim(time, dt)

        robot.draw(screen)
        drawGrid(screen, sz=50, step=1)

        
        drawCircle(screen, (255,0,0), goal, 5, 2)

        drawText(screen, f"Time = {time:.3f}", 5, 5)
        drawText(screen, f"X,Y = {robot.x:.0f}, {robot.y:.0f}, ", 5, 25)
        drawText(screen, f"Energy = {robot.E:.3f}", 5, 45)
       
        pygame.display.flip()
        timer.tick(fps)
        time+=dt

#template file by S. Diane, RTU MIREA, 2024