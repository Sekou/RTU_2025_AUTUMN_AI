
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
        self.A=3 #стремление к цели
        self.B=2 #страх препятствий
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
    def goto(self, pos, obsts, dt):
        #1 - оценка углового рассогласования на цель
        v = np.subtract(pos, self.get_pos())
        a_goal=math.atan2(v[1], v[0])
        da=lim_ang(a_goal-self.alpha)
        #2 - оценка углового рассогласования от препятствий
        dd = [dist(self.get_pos(), o.get_pos()) for o in obsts]
        i = np.argmin(dd)
        v2 = np.subtract(obsts[i].get_pos(), self.get_pos())
        a_obst = math.atan2(v2[1], v2[0])
        da2 = lim_ang(a_obst - self.alpha)
        #3 - объединение двух компонент управления
        self.steer += (self.A*da - self.B*da2)*dt
        self.steer=max(-1, min(1, self.steer))
        self.speed=50

def calc_traj_len(traj):
    return sum(dist(p1, p2) for p1, p2 in zip(traj[1:], traj[:-1]))
def calc_collisions(traj, obsts):
	return sum(1 for p in traj if min(dist(p, o.get_pos()) for o in obsts)<30) #число столкновений
def calc_fitness(traj, obsts, goal):
    L=calc_traj_len(traj)
    C=calc_collisions(traj, obsts)
    D=dist(traj[-1], goal)
    Q = 1/(1/800*L+1/80*C+1/800*D)
    return Q
    

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps
    t=0
    run_id=0

    goal = (700,400)
    robot=None
    
    # AA=[1, 3, 5]
    # BB=[1, 3, 5]
    
    
    # variants=list(itertools.product(AA, BB))
    variants=[[1, 1], [1, 3], [1, 5], [3, 1], [3, 3], [3, 5], [5, 1], [5, 3], [5, 5]]

    def reset(run_id):
        nonlocal robot, variants
        v=variants[run_id]
        robot=Robot(200, 150, 0.1)
        robot.A=v[0]
        robot.B=v[1]
        robot.speed=0
        robot.steer=0

    reset(0)
    
    obsts=[Obstacle(200, 200), Obstacle(400, 300), Obstacle(270, 350), Obstacle(250, 450)]
    
    
    with open("log.txt", "w") as f: f.write("")

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    print("Hi")

        #robot.steer = 0.7 * math.sin(2 * t)
        robot.goto(goal, obsts, dt)
        robot.sim(dt)

        screen.fill((255, 255, 255))
        robot.draw(screen)
        for o in obsts: o.draw(screen)
        pygame.draw.circle(screen, (255,0,0), goal, 7, 2)

        L=calc_traj_len(robot.traj)
        C=calc_collisions(robot.traj, obsts)
        D=dist(robot.traj[-1], goal)
        Q=calc_fitness(robot.traj, obsts, goal)
        draw_text(screen, f"Time = {t:.2f}", 5, 5)
        draw_text(screen, f"Traj Len = {L:.0f}", 5, 25)
        draw_text(screen, f"Num Col = {C:.0f}", 5, 45)
        draw_text(screen, f"Dist to Goal = {D:.0f}", 5, 65)
        draw_text(screen, f"Q = {Q:0.3f}", 5, 85)
        draw_text(screen, f"run_id = {run_id}", 5, 105)

        pygame.display.flip()
        timer.tick(fps)
        t+=dt
        if t>10:
            run_id+=1
            reset(run_id)
            t=0
            with open("log.txt", "a") as f: f.write(f"{run_id} {Q}\n")            
            if run_id>=len(variants):
                break
            
            

    print("Expriment finished")
    print(f"Q={Q:0.3f}")



main()

#template file by S. Diane, RTU MIREA, 2024