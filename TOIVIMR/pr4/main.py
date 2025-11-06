import cv2
import numpy as np

LK_PARAMS = dict(winSize=(20, 20), maxLevel=3, 
criteria=(cv2.TermCriteria_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
#30 - макс число итераций
#0.01 - целевая точность

def process_images(detector, image_1_rgb, image_2_rgb):
    image_1=cv2.cvtColor(image_1_rgb, cv2.COLOR_RGB2GRAY)
    image_2=cv2.cvtColor(image_2_rgb, cv2.COLOR_RGB2GRAY)
    keypoints_1_full=detector.detect(image_1)
    keypoints_1=np.array([x.pt for x in keypoints_1_full], dtype=np.float32)
    keypoints_2, status, error = cv2.calcOpticalFlowPyrLK(image_1, image_2, keypoints_1,
None, **LK_PARAMS)
    status=status.reshape(status.shape[0])
    keypoints_1 = keypoints_1[status==1]
    keypoints_2 = keypoints_2[status==1]
    E, mask_match = cv2.findEssentialMat(keypoints_2, keypoints_1, method=cv2.RANSAC,
prob=0.999, threshold=0.0003)
    _, RotMatrix, d_xyz, mask = cv2.recoverPose(E, keypoints_1, keypoints_2)
    image_1_rgb = draw_tracks(keypoints_1, keypoints_2, image_1_rgb)
    return d_xyz, RotMatrix, image_1_rgb

def draw_tracks(old_pts, new_pts, img):
    for i, (new, old) in enumerate(zip(new_pts, old_pts)):
        a, b, c, d = np.array([*new.ravel(), *old.ravel()], dtype=int)
        img=cv2.line(img, (a,b), (c,d), (255, 0, 0), 1)
    return img

def main():
    detector = cv2.FastFeatureDetector_create(threshold=65, nonmaxSuppression=True)
    frame1=cv2.imread("road1.jpg")
    frame2=cv2.imread("road2.jpg")
    d_xyz, R, image_tracked = process_images(detector, frame1, frame2)
    cv2.imwrite("result.jpg", image_tracked)
    print(f"dxyz={d_xyz}")
    print(f"R={R}")

main()
