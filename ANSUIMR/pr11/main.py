import sys, pygame, numpy as np

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

sz = (800, 600)

eps=1
x_vals=np.arange(50, 750+eps, 50)
y_vals=np.zeros(len(x_vals))

pA=(50,0)
pB=(750,200)
y_vals[-1]=pB[1]


def tr(p): #преобразование системы координат
    y0=sz[1]/2
    return [p[0], y0-p[1]]

def draw_curve(screen, x_vals, y_vals):
    for i in range(1, len(x_vals)):
        x1,x2=x_vals[i-1], x_vals[i]
        y1,y2=y_vals[i-1], y_vals[i]
        pygame.draw.circle(screen, (255,0,255), tr([x1, y1]), 4, 2)
        pygame.draw.line(screen, (0,0,255), tr([x1, y1]), tr([x2, y2]), 2)
    pygame.draw.circle(screen, (255,0,255), tr([x2, y2]), 4, 2)
    pygame.draw.circle(screen, (255,0,0), tr(pA), 7, 2)
    pygame.draw.circle(screen, (0,255,0), tr(pB), 7, 2)

#действие - это физич. величина в подынтегральной части уравнения Лагранжа-Эйлера
#TODO: уточнить
#https://ru.wikipedia.org/wiki/Действие_(физическая_величина)

def get_action(x_vals, y_vals, ind):
    if ind<2: return 0
    xi,xi1,xi2=x_vals[ind], x_vals[max(0,ind-1)], x_vals[max(0,ind-2)]
    yi,yi1,yi2=y_vals[ind], y_vals[max(0,ind-1)], y_vals[max(0,ind-2)]
    yi_=(yi-yi1)/(xi-xi1)
    yi1_=(yi1-yi2)/(xi1-xi2)
    ki=(1+yi_**2)**0.5
    ki1=(1+yi1_**2)**0.5
    dk= ki-ki1
    dy_= yi_-yi1_
    #see wikipedia ddy_ sqrt(1+(dydx)2)
    if dy_==0: return 0
    f = dk/dy_
    return f

def err_func(x_vals, y_vals, ind):
    f=get_action(x_vals, y_vals, ind)
    f1=get_action(x_vals, y_vals, ind-1)
    return abs(f1-f) #ожидаем близкую к нулю ошибку

def approach(x_vals, y_vals, index, delta, radius, err_func):
    y0=y_vals[index]
    e0=err_func(x_vals, y_vals, index)
    emin, ybest=e0,y0
    for d in np.arange(-radius, radius, delta):
        y_vals[index]=y0+d
        e=err_func(x_vals, y_vals, index)
        if e<emin: emin,ybest=e,y_vals[index]
    y_vals[index]=ybest

def apply_Euler(x_vals, y_vals):
    #метод Эйлера для реш. диф. уравнения
    #for index in range(len(x_vals)):
    for index in range(len(x_vals)-1):
        for iter in range(100):
            if iter==0 and index==1: x_vals[index-1]
            if iter==0 and index>1: x_vals[index-1] + (x_vals[index-1]-x_vals[index-2])
            approach(x_vals, y_vals, index, 1, 10, err_func)

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20; dt=1/fps
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: 
                    apply_Euler(x_vals, y_vals)
                          

        screen.fill((255, 255, 255))     
        draw_curve(screen, x_vals, y_vals)
        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()