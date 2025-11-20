
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

class Tree:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.color=(0,125,0)
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1 = np.array(self.get_pos())
        p2 = p1+[0,-35]
        pygame.draw.line(screen, self.color, p1, p2, 2)
        self.draw_branch(screen, p2, 10, 0.7, 0)
        self.draw_branch(screen, p2, 15, 0.7, 8)
        self.draw_branch(screen, p2, 20, 0.7, 16)
        self.draw_branch(screen, p2, 10, -0.7+math.pi, 0)
        self.draw_branch(screen, p2, 15, -0.7+math.pi, 8)
        self.draw_branch(screen, p2, 20, -0.7+math.pi, 16)
    def draw_branch(self, screen, p2, l, a, dy):
        s, c = math.sin(a), math.cos(a)
        pygame.draw.line(screen, self.color, p2+[0,dy], p2+[l*c, l*s+dy], 2)

class Tree2:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.color=(0,125,0)
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1 = np.array(self.get_pos())
        p2 = p1 + [0, -35]
        pygame.draw.line(screen, self.color, p1, p2, 2)
        pp = [[0,-14], [-6,-12], [-7,-9], [-10,-7], [-12,-2], [-9,2], [-12,6], [-13,11],
              [-6,15], [6,16], [12,13], [13,7], [9,4], [11,0], [10,-7], [7,-9], [6,-12]]
        pygame.draw.polygon(screen, (0, 150, 0), p1*0.2+p2*0.8+pp, 2)

class Tree3:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.color=(0,125,0)
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1 = np.array(self.get_pos())
        p2 = p1+[0,-25]
        p3 = p1+[0,-35]
        pygame.draw.line(screen, self.color, p1, p3, 2)
        pygame.draw.circle(screen, self.color, p3, 3, 2)
        self.draw_branch(screen, p2, 10, -0.7, 0)
        self.draw_branch(screen, p2, 15, -0.7, 8)
        self.draw_branch(screen, p2, 15, -0.7, 16)
        self.draw_branch(screen, p2, 10, 0.7+math.pi, 0)
        self.draw_branch(screen, p2, 15, 0.7+math.pi, 8)
        self.draw_branch(screen, p2, 15, 0.7+math.pi, 16)
    def draw_branch(self, screen, p2, l, a, dy):
        s, c = math.sin(a), math.cos(a)
        p3 = p2+[0,dy]
        p4 = p3+[l/2*c, l/2*s]
        p5 = p3+[l*c, l*s]
        pygame.draw.line(screen, self.color, p3, p5, 2)
        pygame.draw.circle(screen, self.color, p4, 3, 2)
        pygame.draw.circle(screen, self.color, p5, 3, 2)

sz = (800, 600)

class Robot:
    def __init__(self, x, y):
        self.radius=15
        self.color=(0,0,0)
        self.x, self.y, self.a=x,y,0
        self.vlin, self.vrot=0,0
        self.fov = [[0,0], [150,70], [150,-70]]
    def get_pos(self):
        return [self.x, self.y]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
        pp=self.get_rotated_fov()
        for i in range(len(pp)):
            pygame.draw.line(screen, (0,255,0), pp[i-1], pp[i], 2)
    def get_rotated_fov(self):
        return [np.add(self.get_pos(), rot(p, self.a)) for p in self.fov]
    def detect(self, objs):
        pp=self.get_rotated_fov()
        for o in objs:
            if pt_inside_ngon(o.get_pos(), pp):
                if type(o)==Tree: return "fir"
                if type(o)==Tree2: return "oak"
                if type(o)==Tree3: return "birch"
        return "empty"
    def sim(self, dt):
        s,c=math.sin(self.a), math.cos(self.a)
        self.x+=c*self.vlin*dt
        self.y+=s*self.vlin*dt
        self.a+=self.vrot*dt

def main():
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20
    robot = Robot(200, 200)

    detection_time=1*fps

    trees=[
        Tree(300,100),
        Tree2(400,150),
        Tree3(350,200),
        Tree(420,250),
        Tree2(500,300),
        Tree3(450,400),
        Tree(300,390),
        Tree2(200,380),
        Tree3(100,380),
    ]

    detection_history=""
    t_ind=0

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w: robot.vlin=50
                if ev.key == pygame.K_s: robot.vlin=-50
                if ev.key == pygame.K_a: robot.vrot=-1
                if ev.key == pygame.K_d: robot.vrot=+1
                if ev.key == pygame.K_1: 
                    with open("detection_history.txt", "w") as f:
                        f.write(detection_history)

        dt=1/fps
        robot.sim(dt)
        if t_ind%detection_time==0:
            detection=robot.detect(trees)
            print(detection)
            detection_history+=detection+" "

        screen.fill((255, 255, 255))
        for tree in trees:
            tree.draw(screen)

        robot.draw(screen)
        drawText(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)
        t_ind+=1

main()

#template file by S. Diane, RTU MIREA, 2024