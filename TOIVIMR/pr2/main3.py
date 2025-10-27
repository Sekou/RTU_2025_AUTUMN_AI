import sys, pygame
import numpy as np
import math

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, с=(100, 200, 100)):  # отрисовка текста
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
    d0,d=2,w/len(arr)
    x_, y_,hmax,c = x+d0,y+h-d0, max(arr), (255,0,0)
    k=1/hmax*(h-d0*2) if hmax>0 else 0
    for i in range(len(arr)):
        pygame.draw.line(screen, c, (x_+i*d, y_), (x_+i*d, y_-arr[i]*k), 2)

W, H = sz = (800, 600)

def arr_to_str(arr):
    return ", ".join([f"{v:.2f}" for v in arr])

def rgb2gray(rgb):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.333 * r + 0.333 * g + 0.333 * b
    return gray

def compare(hist1, hist2):
    return np.linalg.norm(np.subtract(hist1, hist2))

def gauss_mask(x=0, y=0, mx=0, my=0, sx=1, sy=1):
    return np.exp(-0.5*(((x - mx)/sx)**2 + ((y - my)/sy)**2))

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
        iw,ih=img.shape[1],img.shape[0]
        for iy in range(min(self.h, ih-self.y0)):
            for ix in range(min(self.w, iw-self.x0)):
                self.brightness+=\
                    np.mean(img[self.y0+iy,self.x0+ix,:])
        self.brightness/=(self.w*self.h*255*3)
        return self.brightness
    def calc_contrast(self, img):
        vv=[]
        iw,ih=img.shape[1],img.shape[0]
        for iy in range(min(self.h, ih-self.y0)):
            for ix in range(min(self.w, iw-self.x0)):
                vv.append(np.mean(img[self.y0+iy,self.x0+ix,:]))
        vv=sorted(vv)
        a, b, avg=np.mean(vv[:200]), np.mean(vv[-200:]), np.mean(vv)
        c1 = abs(a-avg)/255
        c2 = abs(avg-b)/255
        self.contrast=(c1+c2)/2
        return self.contrast
    def calc_histogramm(self, img, nbins=10):
        img2=rgb2gray(img) if len(img.shape)==3 else img
        iw,ih=img.shape[1],img.shape[0]
        img3=img2[self.y0:min(self.y0+self.h,ih), self.x0:min(self.x0+self.w, iw)] #NEW ih->iw
        if self.x0>=iw or self.y0>=ih: return None
        vmax = img3.max(axis=(0, 1))
        res=np.zeros(nbins)
        thresholds = list(np.arange(0, vmax, vmax/nbins))+[vmax]
        iw,ih=img.shape[1],img.shape[0]
        for iy in range(min(self.h, ih-self.y0)):
            for ix in range(min(self.w, iw-self.x0)):
                v=img3[iy, ix]
                for j in range(len(thresholds)-1):
                    if thresholds[j]<=v<thresholds[j+1]:
                        g=gauss_mask(ix, iy, self.w/2, self.h/2, self.w/2, self.h/2)
                        res[j]+=g
                        break
        self.histogramm=res
        return res

def search(etalon, image, thresh, dx, dy, margin):
    res=[]
    for y in range(0,image.shape[0]-margin, dx):
        for x in range(0,image.shape[1]-margin, dy):
            frame=Frame(x, y, 45, 45)
            h=frame.calc_histogramm(image, 10)
            error=compare(etalon, h)
            if error<thresh: res.append([x,y])
    return res
        
def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps

    surf = pygame.image.load('img.jpg')
    img = pygame.surfarray.array3d(surf)
    img=img.swapaxes(0, 1) #NEW

    img_gray=rgb2gray(img)
    img_rect = surf.get_rect(topleft=(0, 0))

    frame=Frame(100, 100, 45, 45)

    etalon=None
    locations=[]

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
                if ev.key == pygame.K_1:
                    locations=search(etalon, img_gray, 250, 20, 20, 45)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                frame.x0=ev.pos[0]
                frame.y0=ev.pos[1]
                h=frame.calc_histogramm(img, 10)
                if etalon is not None:
                    error=compare(etalon, h)
                    print(f"error={error}")

        frame.calc_brightness(img)
        frame.calc_contrast(img)

        screen.fill((200, 200, 200))

        screen.blit(surf, img_rect)

        frame.draw(screen)

        for l in locations:            
            pygame.draw.rect(screen, (255,155,0), [*l, 45, 45], 2)

        draw_text(screen, f"W*H = {W}*{H}", 5, 5)
        draw_text(screen, f"Brightness = {frame.brightness:.2f}", 5, 25)
        draw_text(screen, f"Contrast = {frame.contrast:.2f}", 5, 45)
        draw_text(screen, f"X, Y = {frame.x0:.0f}, {frame.y0:.0f}", 5, 65)
        
        if frame.histogramm is not None:
            str_hist=arr_to_str(frame.histogramm)
            draw_text(screen, f"Current Hist. = {str_hist}", 5, 560)
            draw_hist(screen, frame.histogramm, frame.x0, frame.y0, frame.w, frame.h)

        if etalon is not None:
            str_hist=arr_to_str(etalon)
            draw_text(screen, f"Etalon Hist. = {str_hist}", 5, 580)

        pygame.display.flip()
        timer.tick(fps)

main()

#template file by S. Diane, RTU MIREA, 2024