import sys, pygame, numpy as np
pygame.font.init()
def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))
sz = (800, 600)

#массивы значений оптимизируемой кривой
eps=1
x_vals=np.arange(50, 750+eps, 50)
y_vals=np.zeros(len(x_vals))

#граничные точки
pA=(50,0)
pB=(750,200)
y_vals[0]=pA[1]
y_vals[-1]=pB[1]

def tr(p): #преобразование системы координат
    y0=sz[1]/2
    return [p[0], y0-p[1]]

#отрисовка прямой
def draw_curve(screen, x_vals, y_vals):
    for i in range(1, len(x_vals)):
        x1,x2=x_vals[i-1], x_vals[i]
        y1,y2=y_vals[i-1], y_vals[i]
        pygame.draw.circle(screen, (255,0,255), tr([x1, y1]), 4, 2)
        pygame.draw.line(screen, (0,0,255), tr([x1, y1]), tr([x2, y2]), 2)
    pygame.draw.circle(screen, (255,0,255), tr([x2, y2]), 4, 2)
    pygame.draw.circle(screen, (255,0,0), tr(pA), 7, 2)
    pygame.draw.circle(screen, (0,255,0), tr(pB), 7, 2)

#действие - это физич. величина эквивалентная интегралу длины кривой
#https://ru.wikipedia.org/wiki/Действие_(физическая_величина)

#Рассчет Лагранжиана
def get_lagrangian_and_dydx(x_vals, y_vals, ind):
    if ind<2: return 0,0
    xi,xi1=x_vals[ind], x_vals[max(0,ind-1)]
    yi,yi1=y_vals[ind], y_vals[max(0,ind-1)]
    yi_=(yi-yi1)/(xi-xi1)
    ki=(1+yi_**2)**0.5
    return ki, yi_

def get_ddydx_lagrangian(x_vals, y_vals, ind): #должен = const
    if ind<2: return 0
    ki, dydxi=get_lagrangian_and_dydx(x_vals, y_vals, ind)
    ki1, dydxi1=get_lagrangian_and_dydx(x_vals, y_vals, ind-1)
    dk= ki-ki1
    dy_= dydxi-dydxi1
    #see wikipedia ddy_ sqrt(1+(dydx)2)
    if dy_==0: return 0
    f = dk/dy_
    return f

def err_func(x_vals, y_vals, ind):
    f=get_ddydx_lagrangian(x_vals, y_vals, ind)
    f1=get_ddydx_lagrangian(x_vals, y_vals, ind-1)
    f1p=get_ddydx_lagrangian(x_vals, y_vals, ind+1)
    #return max(abs(f1-f), abs(f1p-f)) #ожидаем близкую к нулю ошибку
    return max(abs(f1-f), abs(f1p-f)) #ожидаем близкую к нулю ошибку
    #return f**2 + (f1-f)**2 + (f1p-f)**2 + (f1p-f1)**2 #ожидаем близкую к нулю ошибку

def approach(x_vals, y_vals, index, delta, radius, err_func):
    y0=y_vals[index]
    e0=err_func(x_vals, y_vals, index)
    emin, ybest=e0,y0
    for d in np.arange(-radius, radius, delta):
        y_vals[index]=y0+d
        #СЮДА МОЖНО БЫЛО БЫ ВПИСАТЬ ЛОГИКУ ПОДСТРОЙКИ УПРАВЛЕНИЯ РОБОТОМ
        #МОЖНО БЫЛО БЫ УЧЕСТЬДИНАМИКУ РАЗГОНА/ТОРМОЖЕНИЯ РОБОТА
        #ВМЕСТО y_vals = *, напистаь control = *
        e=err_func(x_vals, y_vals, index)
        if e<emin: emin,ybest=e,y_vals[index]
    y_vals[index]=ybest

def apply_Euler(x_vals, y_vals):
    #метод Эйлера для реш. диф. уравнения
    #for index in range(len(x_vals)):
    for index in range(1, len(x_vals)-1):
        approach(x_vals, y_vals, index, 0.01, 1, err_func)

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
                if ev.key == pygame.K_2: 
                    for i in range(100):
                        apply_Euler(x_vals, y_vals)
                          

        screen.fill((255, 255, 255))     
        draw_curve(screen, x_vals, y_vals)
        draw_text(screen, f"Test = {1}", 5, 5)

        pygame.display.flip()
        timer.tick(fps)

main()