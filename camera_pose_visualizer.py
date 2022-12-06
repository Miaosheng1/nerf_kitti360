import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch
import mpl_toolkits.mplot3d.art3d as art3d

class CameraPoseVisualizer:
    def __init__(self,xlim,ylim,zlim):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        self.ax.set_aspect("auto")
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_zlim(zlim)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        print('initialize camera pose visualizer')

    def extrinsic2pyramid(self, extrinsic):
        ## 绘制平移向量
        T = extrinsic[:3, 3]
        print(T)
        self.ax.scatter(T[0], T[1], T[2], marker='o', color='k',s=1)

        Rx, Ry, Rz = extrinsic[:3, 0], extrinsic[:3, 1], extrinsic[:3, 2]

        endX_point = T + Rx
        endY_point = T + Ry
        endZ_point = T + Rz

        ## draw三个坐标轴
        self.ax.plot((T[0], endX_point[0]), (T[1], endX_point[1]), (T[2], endX_point[2]), color='r')
        self.ax.plot((T[0], endY_point[0]), (T[1], endY_point[1]), (T[2], endY_point[2]), color='b')
        self.ax.plot((T[0], endZ_point[0]), (T[1], endZ_point[1]), (T[2], endZ_point[2]), color='g')

    def pts_visualize(self,pts):
        print("pts count is {}".format(pts.shape[0]))
        rand_idx = np.random.randint(0,1024,size=2)
        for i in range(len(rand_idx)):
            self.ax.scatter(pts[rand_idx[i],:,0],pts[rand_idx[i],:,1],pts[rand_idx[i],:,2])
            print()
        plt.savefig("pts_volume.png")


    def show(self):
        plt.title('Extrinsic Parameters')
        plt.legend(['x axis','y axis','z axis'])
        plt.savefig("kitti360_trainview.png")
