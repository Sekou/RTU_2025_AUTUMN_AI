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
    F=1

    x0,y0=50,250

    x, y = x0, y0
    ax, vx = 0, 0
    t=0

    x_plot=[]
    t_plot=[]

    #ошибка интегральной кривой для решения диф. ур. методом Эйлера
    def err_func(x_plot, ind, dt, F, m):
        xi, xi1, xi2 = x_plot[ind],  x_plot[max(0,ind-1)],  x_plot[max(0,ind-2)]
        dxdt = (xi-xi1)/dt #robot speed
        dxdt_ = (xi1-xi2)/dt #prev robot speed
        dxdt2 = (dxdt-dxdt_)/dt
        return abs(dxdt2 - F/m) #2nd Newton Law

    def approach(x_plot, index, delta, radius, err_func):
        x0=x_plot[index]
        e0=err_func(x_plot, index, dt, F, m)
        emin, xbest=e0,x0
        for d in np.arange(-radius, radius, delta):
            x_plot[index]=x0+d
            e=err_func(x_plot, index, dt, F, m)
            if e<emin: emin,xbest=e,x_plot[index]
        x_plot[index]=xbest

    x_plot=[0]*int(12/dt)
    def apply_Euler(x_plot):
        #метод Эйлера для реш. диф. уравнения
        for index in range(len(x_plot)):
            for iter in range(100):
                if iter==0 and index==1: x_plot[index-1]
                if iter==0 and index>1: x_plot[index-1] + (x_plot[index-1]-x_plot[index-2])
                approach(x_plot, index, 0.005, 0.01, err_func)

    for i in range(1000):
        print(f"Iter: {i}")
        apply_Euler(x_plot)

    t_plot=[]
    for index in range(len(x_plot)):
        t_plot.append(dt*index)

    import matplotlib.pyplot as plt   

    plt.plot(t_plot, x_plot)
    plt.show()    

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: print("Hi")      

        screen.fill((255, 255, 255))     
        draw_obj(screen, x, y, 50)
        draw_arrow(screen, (200,200,200), [x0, y0], 0, 700, 2)
        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)
        t+=dt

main()