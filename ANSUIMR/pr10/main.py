import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

def draw_obj(screen, x, y, sz):
    pygame.draw.rect(screen, (0,0,0), [x -sz/2, y-sz/2, sz, sz], 2)
    pygame.draw.circle(screen, (0,0,255), [x,y], 5, 2)

# отрисовка стрелки по точке и углу
def draw_arrow(screen, color, p0, angle, lenpx, w):
    p1 = [p0[0] + lenpx * math.cos(angle), p0[1] + lenpx * math.sin(angle)]
    p2 = [p1[0] - 10 * math.cos(angle + 0.5), p1[1] - 10 * math.sin(angle + 0.5)]
    p3 = [p1[0] - 10 * math.cos(angle - 0.5), p1[1] - 10 * math.sin(angle - 0.5)]
    for a,b in [[p0, p1], [p1, p2], [p1, p3]]: pygame.draw.line(screen, color, a, b, w)
    
sz = (800, 600)

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20; dt=1/fps

    m=1
    F=10

    x0,y0=50,250

    x, y = x0, y0
    ax, vx = 0, 0
    t=0

    x_plot=[]
    t_plot=[]

    import matplotlib.pyplot as plt   
    plot_visible=False
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: print("Hi")      

        ax=F/m #2 закон Ньютона
        vx+=ax*dt          
        x+=vx*dt   

        x_plot.append(x)
        t_plot.append(t)

        if x>750 and not plot_visible:
            plt.plot(t_plot, x_plot)
            plt.show()    
            plot_visible=True
            break


        screen.fill((255, 255, 255))     
        draw_obj(screen, x, y, 50)
        draw_arrow(screen, (200,200,200), [x0, y0], 0, 700, 2)
        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)
        t+=dt

main()