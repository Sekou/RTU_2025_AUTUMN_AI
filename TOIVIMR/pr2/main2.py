import sys, pygame
import numpy as np
import math

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, с=(255, 255, 255)):  # отрисовка текста
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

def draw_hist(screen, arr, x, y, w, h):
    y_,hmax,c = y+h, max(arr), (255,0,0)
    for i in range(len(arr)): pygame.draw.line(screen, c, (x+i*5, y_), (x+i*5, y_-arr[i]*h/hmax), 4)
    pygame.draw.rect(screen, c, (x, y, w, h), 1)

def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина, высота и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rot_arr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

W, H = sz = (800, 600)

def arr_to_str(arr):
    return ", ".join([f"{v:.2f}" for v in arr])

def rgb2gray(rgb):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.333 * r + 0.333 * g + 0.333 * b
    return gray

def compare(hist1, hist2):
    return np.linalg.norm(np.subtract(hist1, hist2))

class Frame:
    def __init__(self, x0, y0, w, h):
        self.x0, self.y0, self.w, self.h=x0, y0, w, h
        self.brightness=0
        self.contrast=0
        self.histogramm=None
    def draw(self, screen):
        pygame.draw.rect(screen, (255,255,0),
                         (self.x0, self.y0, self.w, self.h), 2)
    def calc_brightness(self, img):
        self.brightness=0
        for iy in range(self.h):
            for ix in range(self.w):
                self.brightness+=\
                    np.mean(img[self.y0+iy,self.x0+ix,:])
        self.brightness/=(self.w*self.h*255*3)
        return self.brightness
    def calc_contrast(self, img):
        vv=[]
        for iy in range(self.h):
            for ix in range(self.w):
                vv.append(np.mean(img[self.y0+iy,self.x0+ix,:]))
        vv=sorted(vv)
        a, b, avg=np.mean(vv[:200]), np.mean(vv[-200:]), np.mean(vv)
        c1 = abs(a-avg)/255
        c2 = abs(avg-b)/255
        self.contrast=(c1+c2)/2
        return self.contrast
    def calc_histogramm(self, img, nbins=10):
        img2=rgb2gray(img)
        img3=img2[self.y0:self.y0+self.h, self.x0:self.x0+self.w]
        vmax = img3.max(axis=(0, 1))
        res=np.zeros(nbins)
        thresholds = list(np.arange(0, vmax, vmax/nbins))+[vmax]
        for iy in range(self.h):
            for ix in range(self.w):
                v=img3[iy, ix]
                for j in range(len(thresholds)-1):
                    if thresholds[j]<=v<thresholds[j+1]:
                        res[j]+=1
                        break
        self.histogramm=res
        return res
        
def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps

    surf = pygame.image.load('img.jpg')
    img = pygame.surfarray.array3d(surf)
    img_rect = surf.get_rect(bottomright=(W, H))

    frame=Frame(100, 100, 45, 45)

    etalon=None
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w: frame.y0-=5
                if ev.key == pygame.K_a: frame.x0-=5
                if ev.key == pygame.K_s: frame.y0+=5
                if ev.key == pygame.K_d: frame.x0+=5
                if ev.key == pygame.K_e: etalon=frame.calc_histogramm(img, 10)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                frame.x0=ev.pos[0]
                frame.y0=ev.pos[1]
                h=frame.calc_histogramm(img, 10)
                if etalon is not None:
                    error=compare(etalon, h)
                    print(f"error={error}")

        frame.calc_brightness(img)
        frame.calc_contrast(img)

        screen.fill((255, 255, 255))

        screen.blit(surf, img_rect)

        frame.draw(screen)

        draw_text(screen, f"W*H = {W}*{H}", 5, 5)
        draw_text(screen, f"Brightness = {frame.brightness:.2f}", 5, 25)
        draw_text(screen, f"Contrast = {frame.contrast:.2f}", 5, 45)
        
        if frame.histogramm is not None:
            str_hist=arr_to_str(frame.histogramm)
            draw_text(screen, f"Hist = {str_hist}", 5, 560)
            draw_hist(screen, frame.histogramm, frame.x0, frame.y0, frame.w, frame.h)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024