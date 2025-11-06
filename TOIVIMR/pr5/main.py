from lib2to3.pgen2 import token
import numpy as np
import matplotlib.pyplot as plt

#https://www.youtube.com/watch?v=EBuk7PlTEkI

vals=[]

with open("calibration.txt") as f:
    for ln in f.readlines():
        tokens=ln.split(", ")
        vv=[float(t) for t in tokens]
        vals.append(vv)

print(vals[1][1])
N=len(vals)


# Define data points
indidices = np.arange(N)
arr_ax = np.array([vv[1] for vv in vals])
arr_ay = np.array([vv[2] for vv in vals])
arr_az = np.array([vv[3] for vv in vals])

# Create the plot
plt.plot(indidices, arr_ax)
plt.plot(indidices, arr_ay)
plt.plot(indidices, arr_az)

# Add labels and a title (optional)
plt.xlabel("X-axis Label")
plt.ylabel("Y-axis Label")
plt.title("IMU Accelerations AX AY AZ")

# Display the plot
plt.show()


def calc_var(arr):
    avg=np.mean(arr)
    d2d2=[(x-avg)**2 for x in arr]
    return sum(d2d2)/(len(arr)-1)

def calc_cov(arr1, arr2):
    assert len(arr1)==len(arr2), "Arrays' lengths should match!"
    avg1, avg2=np.mean(arr1), np.mean(arr2)
    a2b2=[(x-avg1)*(y-avg2) for x,y in zip(arr1, arr2)]
    return sum(a2b2)/(len(arr1)-1)

var_x=calc_var(arr_ax)
print(var_x)

var_y=calc_var(arr_ay)
print(var_y)

var_z=calc_var(arr_az)
print(var_z)


cov_xy=calc_cov(arr_ax, arr_ay)
print(cov_xy)

cov_yz=calc_cov(arr_ay, arr_az)
print(cov_yz)

cov_zx=calc_cov(arr_az, arr_ax)
print(cov_zx)

MCOV = np.zeros((3,3))
MCOV[0,0]=var_x
MCOV[1,1]=var_y
MCOV[2,2]=var_z
MCOV[1,0]=MCOV[0,1]=cov_xy
MCOV[2,0]=MCOV[0,2]=cov_zx
MCOV[2,1]=MCOV[1,2]=cov_yz
print(MCOV)

from scipy.linalg import sqrtm
# Compute the matrix square root
C = sqrtm(MCOV)

print("square root")
print(C)
print("multiplied back")
print(C*C)
#TODO: понять математику и почему не всегда сходится обратное произведение

W=np.linalg.inv(C)

print("W")
print(W)


arr_ax_=np.subtract(arr_ax, np.mean(arr_ax))
arr_ay_=np.subtract(arr_ay, np.mean(arr_ay))
arr_az_=np.subtract(arr_az, np.mean(arr_az))

#arr_ax_=W@arr_ax_
#arr_ay_=W@arr_ay_
#arr_az_=W@arr_az_

A=[W@xyz for xyz in zip(arr_ax_, arr_ay_, arr_az_)]
#print(A)
with open("result.txt", "w") as f:
    lines=[f"{ax:.3f}, {ay:.3f}, {az:.3f}\n"\
    for ax, ay, az in A]
    f.writelines(lines)

