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

pts1 = [[100,70],[200,90],[300,50],[250,170],[190,110],[270,220],[320,200]]


pts2 = np.array(rot_arr(pts1, 0.5)) + [200,200]

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20; dt=1/fps
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: print("Hi")                

        screen.fill((255, 255, 255))     

        for p in pts1:
            pygame.draw.circle(screen, (0,0,0), p, 3, 2)
        for p in pts2:
            pygame.draw.circle(screen, (255,0,0), p, 3, 2)

        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()