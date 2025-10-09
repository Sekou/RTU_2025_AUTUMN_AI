from scipy.linalg import lstsq
import matplotlib.pyplot as plt
import numpy as np
print(np.array([[0.44853636, 0.52266289], [0.52266289, 0.11520302]]).flatten())
#данные измерений
data=np.array([[1, 1, 2],[1, 2, 3],[2, 1, 4],[2, 2, 5],[1.5, 1.5, 6]])
def fit_matrix_A(data):
    x=data[:,0]
    y=data[:,1]
    z=data[:,2]
    n=len(z)
    Q=np.zeros((n, 4))
    Q[:,0]=x*x
    Q[:,1]=x*y
    Q[:,2]=y*x
    Q[:,3]=y*y
    a, res, rnk, s = np.linalg.lstsq(Q, z, rcond=None)
    A=a.reshape((2,2))
    return A

A=fit_matrix_A(data)
print(A)

X = np.arange(0, 2, 0.25)
Y = np.arange(0, 2, 0.25)
X, Y = np.meshgrid(X, Y)

aa=A.flatten(); xx=X.flatten(); yy=Y.flatten()
Z=[]
for x, y in zip(xx, yy):
    q=[x*x, x*y, y*x, y*y]
    z=aa@q
    Z.append(z)
    print (x, y, z)

Z=np.reshape(Z, X.shape)

from matplotlib import cm
from matplotlib.ticker import LinearLocator
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
# Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
# Customize the z axis.
ax.set_zlim(0, 6)
ax.zaxis.set_major_locator(LinearLocator(10))
# A StrMethodFormatter is used automatically
ax.zaxis.set_major_formatter('{x:.02f}')
# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)
for x, y, z in data: ax.scatter(x, y, z)
plt.show()

