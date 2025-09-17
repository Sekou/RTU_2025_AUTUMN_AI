import matplotlib.pyplot as plt
import numpy as np


with open("log_final.txt", "r") as f:
    lines=f.readlines() #строки
    vv=[l.split() for l in lines] #токены
    vv = [[float(v[1]), float(v[2]), float(v[3])] for v in vv]

print(vv)

from matplotlib import cm
from matplotlib.ticker import LinearLocator

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

N=5
# Make data.
# X = np.arange(-5, 5, 0.25)
A = [v[0] for v in vv]
A = np.reshape(A, (N,N))
# Y = np.arange(-5, 5, 0.25)
B = [v[1] for v in vv]
B = np.reshape(B, (N,N))
# X, Y = np.meshgrid(X, Y)
# A, B = np.meshgrid(A, B)
# R = np.sqrt(X**2 + Y**2)
# Z = np.sin(R)
Z=[v[2] for v in vv]
Z = np.reshape(Z, (N,N))

# Plot the surface.
surf = ax.plot_surface(A, B, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

ax.set_xlabel('A')
ax.set_ylabel('B')
ax.set_zlabel('Z')

# Customize the z axis.
ax.set_zlim(0, 2)
ax.zaxis.set_major_locator(LinearLocator(10))
# A StrMethodFormatter is used automatically
ax.zaxis.set_major_formatter('{x:.02f}')

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()