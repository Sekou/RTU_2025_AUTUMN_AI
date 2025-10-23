import sys
import cv2
import numpy as np

img=cv2.imread("img.jpg")
original_height, original_width = img.shape[:2]
new_width = 600
aspect_ratio = new_width / original_width
new_height = int(original_height * aspect_ratio)
img = cv2.resize(img, (new_width, new_height))
cv2.imwrite("img_resized.jpg", img)

cv2.imshow("img", img)
cv2.waitKey(0)


# 1 через OpenCV
fast = cv2.FastFeatureDetector_create()
kp = fast.detect(img,None)
img2 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
cv2.imwrite('fm_cv.png', img2)
#sys.exit(0)

# 1 вручную
deltas=[[0,-3], [1,-3], [2,-2], [3,-1], [3, 0], [3,1], [2,2],
[1,3], [0,3], [-1,3], [-2,2], [-3,1], [-3,0], [-3,-1], [-2,-2], [-1,-3]]

def getPx(img, x, y):
    if x<0 or y<0 or x>=img.shape[1] or y>=img.shape[0]:
        return 0
    return np.sum(img[y,x])/3


def getDescr(img, x, y):
    thr = 20
    descr=[]
    v=getPx(img, x, y)
    n1, n2, n3 = 0, 0, 0
    for d in deltas:
        v2=getPx(img, x+d[0], y+d[1])
        if v2<v-thr: #крайний пиксель темнее центра
            n1+=1; n2, n3 = 0, 0
            descr.append(1)
        if v+thr>v2>v-thr: #крайний пиксель похожий
            n2+=1; n1, n3 = 0, 0
            descr.append(2)
        if v2>v+thr: #крайний пиксель светлее центра
            n3+=1; n1, n2 = 0, 0
            descr.append(0)
    if max([n1, n3])>=12:
        return descr
    else:
        return None

def getFeatureMap(img):
    print("Started building Feature Map")
    fm=np.zeros(img.shape)
    for iy in range(img.shape[0]):
        progress=100*iy/img.shape[0]
        print(f"Progress: {progress:.3f}%")
        for ix in range(img.shape[1]):
            fm[iy, ix]=[255, 255, 255] \
            if getDescr(img, ix, iy) is not None \
            else [0,0,0]
    return fm


fm=getFeatureMap(img)
cv2.imwrite("fm.jpg", fm)
cv2.imshow("fm", fm)
cv2.waitKey(0)
