import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

sz = (800, 600)


def rot(v, ang): #поворот вектора на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]


def rot_arr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def rot_arr_around(vv, ang, c): # функция для поворота массива на угол
    return list(np.add(c, [rot([v[0]-c[0], v[1]-c[1]], ang) for v in vv]))

def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    ang=ang%(2*arc); return ang + (2*arc if ang<-arc else -2*arc if ang>arc else 0)

pts1 = [[100,70],[200,90],[300,50],[250,170],[190,110],[270,220],[320,200]]

pts2 = np.array(rot_arr(pts1, 0.5)) + [200,200]

def find_center(pts):
    return np.mean(pts, axis=0)

def find_nearest_pt(p, pts2):
    dd=[np.linalg.norm(np.subtract(p, q)) for q in pts2]
    return pts2[np.argmin(dd)]

def estimate_angle(c, p, pts2):
    q=find_nearest_pt(p, pts2)
    d1, d2=np.subtract(p, c), np.subtract(q, c)
    a1, a2=math.atan2(*d1[::-1]), math.atan2(*d2[::-1])
    return lim_ang(a2-a1)

def main():
    global pts1, pts2
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20; dt=1/fps

    c1, c2=np.zeros(2), np.zeros(2)
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: 
                    c1=find_center(pts1)
                    c2=find_center(pts2)
                if ev.key == pygame.K_2: 
                    pts2-=(c2-c1)
                    c2=find_center(pts2)
                if ev.key == pygame.K_3:
                    aa = [estimate_angle(c2, p, pts2) for p in pts1] 
                    ang = np.mean(aa)
                    print(ang)
                    #pts2=rot_arr(pts2, ang)
                    pts2=rot_arr_around(pts2, -ang, c2)                    

        screen.fill((255, 255, 255))     

        for p in pts1:
            pygame.draw.circle(screen, (0,0,0), p, 3, 2)
        for p in pts2:
            pygame.draw.circle(screen, (255,0,0), p, 3, 2)

        pygame.draw.circle(screen, (0,0,0), c1, 5, 4)
        pygame.draw.circle(screen, (255,0,0), c2, 5, 4)

        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()
