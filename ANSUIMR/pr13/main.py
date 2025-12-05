import sys, pygame, numpy as np

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

sz = (800, 600)

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20; dt=1/fps

    pts=[
        [200,200], [250, 300], [260, 270], 
        [210,280], [450, 320], [360, 470], 
        [400,100], [280, 370], [290, 290], 
        [240,200], [410, 420], [360, 170]
    ]

    pts_sorted=sorted(pts)

    def bend_sign(p1, p2, p3):
        v1, v2=np.subtract(p2, p1), np.subtract(p3, p2)
        return np.linalg.norm(np.cross(v1, v2))

    def add_node(pts_sorted, contour):
        i = len(contour)
        contour.append(pts_sorted[i])

    def add_node_smart(pts_sorted, contour):
        for i in range(len(contour), len(pts_sorted)):
            if len(contour)<3: sign0=0
            else: sign0=bend_sign(contour[-3], contour[-2], contour[-1])
            sign1=bend_sign(contour[-2], contour[-1], pts_sorted[i])
            if sign0*sign1>=0:
                contour.append(pts_sorted[i])
                return
            i+=1

    contour=[]
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: 
                    if len(contour)<len(pts_sorted):
                        add_node(pts_sorted, contour)
                if ev.key == pygame.K_2: 
                    if len(contour)<len(pts_sorted):
                        add_node_smart(pts_sorted, contour)

        screen.fill((255, 255, 255))     
        for p in pts:
            pygame.draw.circle(screen, (0,0,0), p, 3, 2)
        
        if len(contour)>1:
            pygame.draw.polygon(screen, (0,0,200), contour, 2)
        
        for i in range(len(contour)):
            p1, p2, p3=contour[i-1], contour[i], contour[(i+1)%len(contour)]
            c = (0,255,0) if bend_sign(p1, p2, p3)>0 else (255,0,0)
            pygame.draw.circle(screen, c, p2, 7, 2)

        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()