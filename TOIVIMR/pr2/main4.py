import sys, pygame
import numpy as np
import math

THRESHOLD = 500

pygame.font.init()
def draw_text(screen, s, x, y, sz=12, с=(100, 200, 100)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

def draw_hist(screen, arr, x, y, w, h):
    d0=2;d=(w-2*d0)/len(arr)
    x_, y_,hmax,c = x+d0,y+h-d0, max(arr), (255,0,0)
    k=1/hmax*(h-d0*2) if hmax>0 else 0
    for i in range(len(arr)):
        pygame.draw.line(screen, c, (x_+i*d, y_), (x_+i*d, y_-arr[i]*k), 1)

W, H = sz = (800, 600)

def arr_to_str(arr):
    return " ".join([f"{v:.0f}" for v in arr])

def rgb2gray(rgb, krgb=[0.33,0.33,0.33]):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = krgb[0] * r + krgb[1] * g + krgb[2] * b
    return gray

def compare(hist1, hist2):
    return np.linalg.norm(np.subtract(hist1, hist2))

def gauss_mask(x=0, y=0, mx=0, my=0, sx=1, sy=1):
    return np.exp(-0.5*(((x - mx)/sx)**2 + ((y - my)/sy)**2))

frw,frh=45,45
GAUSS_MASK=[[gauss_mask(ix, iy, frw/2, frh/2, frw/2, frh/2) for ix in range(frw)] for iy in range(frh)]

class Frame:
    def __init__(self, x0, y0, w, h):
        self.x0, self.y0, self.w, self.h=x0, y0, w, h
        self.brightness=0
        self.contrast=0
        self.histogram=None
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
        self.brightness/=(self.w*self.h*255)
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
    def calc_histogram_ext(self, img, nbins=10):
        h1 = self.calc_histogram(img, 10, krgb=[1, 0, 0])
        h2 = self.calc_histogram(img, 10, krgb=[0, 1, 0])
        h3 = self.calc_histogram(img, 10, krgb=[0, 0, 1])
        self.histogram=list(h1) + list(h2) + list(h3)
        return self.histogram
    def calc_histogram(self, img, nbins=10, krgb=[0.33,0.33,0.33]):
        img2=rgb2gray(img, krgb)
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
                        res[j]+=GAUSS_MASK[iy][ix]
                        break
        return res

def search(etalon, image, thresh, dx, dy, margin):
    res=[]
    for y in range(0,image.shape[0]-margin, dx):
        for x in range(0,image.shape[1]-margin, dy):
            frame=Frame(x, y, frw, frh)
            h=frame.calc_histogram_ext(image, 10)
            error=compare(etalon, h)
            if error<thresh: res.append([x,y])
    return res
        
def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Histogram Detector')
    timer = pygame.time.Clock()
    fps = 20
    dt=1/fps

    surf = pygame.image.load('img_.jpg')
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
                if ev.key == pygame.K_e: etalon=frame.calc_histogram_ext(img, 10)
                if ev.key == pygame.K_1:
                    locations=search(etalon, img, THRESHOLD, 20, 20, 45)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                frame.x0=ev.pos[0]
                frame.y0=ev.pos[1]
                h=frame.calc_histogram_ext(img, 10)
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
        
        if frame.histogram is not None:
            str_hist=arr_to_str(frame.histogram)
            draw_text(screen, f"Curr. Hist. = {str_hist}", 5, 530)
            draw_hist(screen, frame.histogram, frame.x0, frame.y0, frame.w, frame.h)

        if etalon is not None:
            str_hist=arr_to_str(etalon)
            draw_text(screen, f"Etalon Hist. = {str_hist}", 5, 555)

        pygame.display.flip()
        timer.tick(fps)

main()


#template file by S. Diane, RTU MIREA, 2024
