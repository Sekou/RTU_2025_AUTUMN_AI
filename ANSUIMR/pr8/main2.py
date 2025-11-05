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

def lim_ang(ang):
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rot_arr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2):
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

def project_pt(segm, pt): #точка-проекция точки на отрезок
    v2=np.subtract(pt, segm[0], dtype=float)
    v1=np.subtract(segm[1], segm[0], dtype=float)
    v1_=v1/np.linalg.norm(v1)
    L2=np.dot(v1_, v2)
    return segm[0] + L2*v1_

class TargetTrajectory:
    def __init__(self, pts):
        self.pts=pts
    def draw(self, screen):
        for i in range(1, len(self.pts)):
            pygame.draw.line(screen, (200,200,0), self.pts[i-1], self.pts[i], 1)
    def get_traj_len(self):
        return sum([dist(self.pts[i-1], self.pts[i]) for i in range(1, len(self.pts))])

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
        self.prev_da=0
        self.integr_da=0
        
    def get_pos(self):
        return [self.x, self.y]

    def get_traj_len(self):
        return sum([dist(self.traj[i-1], self.traj[i]) for i in range(1, len(self.traj))])

    def clear(self):
        self.traj = []
        self.vals1 = []
        self.vals2 = []

    def draw(self, screen):
        p=np.array(self.get_pos())
        draw_rot_rect(screen, (0,0,0), p,
                    self.L, self.W, self.alpha)
        dx=self.L/3
        dy=self.W/3
        dd=[[-dx,-dy], [-dx,dy], [dx,-dy], [dx,dy]]
        dd=rot_arr(dd, self.alpha)
        kRot=[0,0,1,1]
        for d, k in zip(dd, kRot):
            draw_rot_rect(screen, (0, 0, 0), p+d,
                        self.L/5, self.W/5, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            pygame.draw.line(screen, (0,0,255), self.traj[i], self.traj[i+1], 1)
        pygame.draw.circle(screen, (255,0,255), self.get_pos(), 4, 2)
        
    def sim(self, dt):
        self.addedTrajPt = False
        delta=[self.speed*dt, 0]
        delta=rot(delta, self.alpha)
        self.x+=delta[0]
        self.y+=delta[1]
        if self.steer!=0:
            R = self.L/self.steer
            da = self.speed*dt/R
            self.alpha+=da

        p=self.get_pos()
        if len(self.traj)==0 or dist(p, self.traj[-1])>10:
            self.traj.append(self.get_pos())
            self.addedTrajPt=True

    def goto(self, pos, dt):
        v=np.subtract(pos, self.get_pos())
        aGoal=math.atan2(v[1], v[0])
        da=lim_ang(aGoal-self.alpha)
        #П-закон управления
        #self.steer += 0.5 * da * dt
        
        #ПД-закон управления
        #self.steer += 0.5 * da * dt + 1 * (da-self.prev_da)/dt * dt
        
        #ПИД-закон управления
        self.steer += 0.5 * da * dt + 1 * (da-self.prev_da)/dt * dt + 0.005*self.integr_da*dt

        self.prev_da=da
        self.integr_da+=da
        maxSteer=1
        if self.steer > maxSteer: self.steer = maxSteer
        if self.steer < -maxSteer: self.steer = -maxSteer
        self.speed = 50


#TODO: 1 ускорить 2 мерить длину траект 3 мерить ошибку

SIM_RATE=2

if __name__=="__main__":
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot=Robot(100, 100, 1)
    pts=[[100,100], [200, 250], [400, 200], [550, 500]]
    traj = TargetTrajectory(pts)

    time=0
    goal = [600,400]
    errors = []
    
    ind_pt=0 #индекс целевой точки, в которую едет робот

    running=True
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
        dt=1/fps

        for iter in range(SIM_RATE):
            if running:
                goal=pts[ind_pt]
                robot.goto(goal, dt)

            robot.sim(dt)

            d_pt = dist(robot.get_pos(), goal)

            if d_pt<50:
                ind_pt+=1
                if ind_pt>=len(pts):
                    running=False
                    robot.speed=0

        screen.fill((255, 255, 255))
        robot.draw(screen)
        traj.draw(screen)

        i1, i2=ind_pt-1, ind_pt
        if i1<0: i1, i2=i1+1, i2+1
        if i2>=len(traj.pts): i1, i2=i1-1, i2-1

        if running:
            segm=[traj.pts[i1], traj.pts[i2]]
            p_=project_pt(segm, robot.get_pos())
            e=dist(*segm)
            errors.append(e)
        
        pygame.draw.line(screen, (255,0,255), robot.get_pos(), p_, 2)
        pygame.draw.circle(screen, (255,0,255), p_, 5, 2)
        pygame.draw.circle(screen, (255,0,0), goal, 5, 2)

        drawText(screen, f"Traj Len Desired = {traj.get_traj_len():.0f}", 5, 5)
        drawText(screen, f"Traj Len Real= {robot.get_traj_len():.0f}", 5, 25)
        drawText(screen, f"Error Avg = {np.mean(errors):.0f}", 5, 45)
       
        pygame.display.flip()
        timer.tick(fps)
        time+=dt

#template file by S. Diane, RTU MIREA, 2024