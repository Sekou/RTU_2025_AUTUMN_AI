
import sys, pygame
from builtins import hasattr, range, str
from robot import Robot
import numpy as np
import math
import json

SCALE = 50 #px|m
SHIFT=[0,0] #m

def tr(pt): #transform pt from m to px
    return (SCALE*(pt[0]-SHIFT[0]), SCALE*(pt[1]-SHIFT[1]))
def tr_(pt): #transform pt from px to m
    return (pt[0]/SCALE+SHIFT[0], pt[1]/SCALE+SHIFT[1])

def snap(pt, delta=0.1):
    return (round(pt[0], 1), round(pt[1], 1))

#проверяем, находится ли точка внутри многоугольника
def pt_inside_ngon(point, vertices):
    (x, y), c = point, 0
    for i in range(len(vertices)):
        (x1, y1), (x2, y2) = vertices[i-1], vertices[i]
        if min(y1,y2) <= y < max(y1, y2): c ^= (x - x1 < (y - y1) / (y2 - y1)*(x2 - x1))
    return c

class Ngon: #многоугольник
    def __init__(self):
        self.pts=[]
        self.closed=False
        self.tmp_pt=None
        self.inner_pts=[]
        self.info, self.info2="", ""
    def calc_inner_pts(self, step=0.5):
        self.inner_pts=[]
        x0, x1=min([p[0] for p in self.pts]), max([p[0] for p in self.pts])
        y0, y1=min([p[1] for p in self.pts]), max([p[1] for p in self.pts])
        d0, d1=step/2, step/100
        for y in np.arange(y0+d0, y1-d1, step):
            for x in np.arange(x0+d0, x1-d1, step):
                if pt_inside_ngon((x, y), self.pts[:-1]):
                    self.inner_pts.append((x, y))
    def add_pt_px(self, p_px):
        self.pts.append(tr_(p_px))
    def clear(self): self.pts, self.inner_pts=[], []
    def save(self, name):
        with open(name, "w") as f:
            f.write(json.dumps({'pts': self.pts, 'closed': self.closed}))
    def load(self, name):
        with open(name, "r") as f:
            d = json.loads(f.read())
            self.pts=d["pts"]
            self.closed=d["closed"]
    def get_perimeter(self):
        return sum(dist(p1, p2) for p1, p2 in zip(self.pts[1:], self.pts[:1]))
    def get_area(self):
        # определяем площадь многоугольника
        x, y = [p[0] for p in self.pts], [p[1] for p in self.pts]  # get x and y in vectors
        x_, y_ = x - np.mean(x), y - np.mean(y)  # shift coordinates
        main_area = np.dot(x_[:-1], y_[1:]) - np.dot(y_[:-1], x_[1:])  # calculate area
        correction = x_[-1] * y_[0] - y_[-1] * x_[0]
        return 0.5 * np.abs(main_area + correction)
    def draw(self, screen):
        if len(self.pts)>1:
            pp=[tr(p) for p in self.pts]
            pygame.draw.lines(screen, (0,0,255), self.closed, pp, 2)
        if self.tmp_pt and len(self.pts)>0:
            pygame.draw.circle(screen, (0,255,255), tr(self.tmp_pt), 5, 2)
            p1, p2 = tr(self.pts[-1]), tr(self.tmp_pt)
            if dist(self.pts[-1], self.pts[0])>0.1:
                pygame.draw.line(screen, (0,255,255), p1, p2, 2)
            L=dist(self.pts[-1], self.tmp_pt)
            x, y=self.tmp_pt
            self.info = f"End point = ({x:.2f}, {y:.2f}), end segm. len. = {L:.2f}"
            self.info2 = f"Perimeter = {self.get_perimeter():.2f}, area = {self.get_area():.2f}"
        for p in self.pts:
            pygame.draw.circle(screen, (0,0,255), tr(p), 5, 2)
        for p in self.inner_pts:
            pygame.draw.circle(screen, (190,190,190), tr(p), 3, 2)

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
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rot_arr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

sz = (800, 600)

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20; dt=1/fps; sim_time=0

    ngon=Ngon()
    ngon.load("ngon.txt")
    ngon.calc_inner_pts()

    robot=Robot(1, 1, 1)
    explored_pts=[]

    FINISHED=False

    p_last=None
    running=True
    while running:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                running=False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_c:
                    ngon.clear()
                if ev.key == pygame.K_s:
                    ngon.save("ngon.txt")
                if ev.key == pygame.K_o:
                    ngon.load("ngon.txt")
                    ngon.calc_inner_pts()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                all_keys = pygame.key.get_pressed()
                pos = tr(snap(tr_(ev.pos)))
                p=pos
                if all_keys[pygame.K_LCTRL] and p_last:
                    p1 = [pos[0], p_last[1]] #вертикаль
                    p2 = [p_last[0], pos[1]] #горизонталь
                    d1, d2 = dist(pos, p1), dist(pos, p2)
                    if min(d1, d2)<50: p = p1 if d1<d2 else p2 #свободный наклон
                ngon.add_pt_px(p)
                p_last=p
                ngon.calc_inner_pts()
            if ev.type == pygame.MOUSEMOTION:
                pos = tr(snap(tr_(ev.pos)))
                ngon.tmp_pt=tr_(pos)

        pp = robot.filter_visible_pts(ngon.inner_pts)
        for p in pp:
            if not p in explored_pts:
                explored_pts.append(p)

        future_pts=list(set(ngon.inner_pts) ^ set(explored_pts))

        selected_pt=tr_([sz[0]/2, sz[1]/2])
        if len(future_pts):
            dd = [dist(robot.get_pos(), p) for p in future_pts]
            i = np.argmin(dd)
            selected_pt=future_pts[i]

        robot.goto(selected_pt, [], dt)
        robot.sim(dt)

        screen.fill((255, 255, 255))
        ngon.draw(screen)
        robot.draw(screen, SCALE, SHIFT)
        for p in pp: pygame.draw.circle(screen, (255, 0, 0), tr(p), 4, 2)
        for p in explored_pts: pygame.draw.circle(screen, (255, 255, 0), tr(p), 4, 2)
        pygame.draw.circle(screen, (255, 0, 255), tr(selected_pt), 7, 2)
        draw_text(screen, f"SCALE = {SCALE}, SHIFT = {SHIFT}", 5, 5)
        draw_text(screen, f"{ngon.info}", 5, 25)
        draw_text(screen, f"{ngon.info2}", 5, 45)
        draw_text(screen, f"Num expl. pts. = {len(explored_pts)}", 5, 520)
        expl_ratio=len(explored_pts)/max(1, len(ngon.inner_pts))
        draw_text(screen, f"Expl. ratio = {expl_ratio:.3f}", 5, 540)
        draw_text(screen, f"Time = {sim_time:.2f}", 5, 560)

        if expl_ratio>=0.999:
            FINISHED=True
            robot.speed=0

        pygame.display.flip()
        timer.tick(fps)
        if not FINISHED: sim_time+=dt

main()

#template file by S. Diane, RTU MIREA, 2024