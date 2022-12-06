import os,imageio
import torch
import numpy as np
import cv2 as cv
from camera_pose_visualizer import CameraPoseVisualizer
'''
Output: images, poses, bds, render_pose, itest;

poses (是指的 c2w 的pose)
'''

def load_kitti360_data(basedir, factor=8):
    poses, imgs, K, i_test =_load_data(basedir,factor= factor)
    H,W = imgs.shape[1:3]
    focal = K[0][0]

    ## 设第一张相机的Pose 是单位矩阵，对其他相机的Pose 需要进行调整为相对于第一帧的Pose 相对位姿
    poses = Normailize_T(poses)   ## 对于 平移translation 进行归一化


    render_pose = np.stack(poses[i] for i in i_test)

    '''     Visual Camera Pose 
     visualizer = CameraPoseVisualizer([-5, 5], [-5, 5], [0, 5])
    for i in np.arange(render_pose.shape[0]):
        if i % 1 == 0:
            visualizer.extrinsic2pyramid(render_pose[i], 'y', 10)
    visualizer.show()
    '''

    return poses,imgs,render_pose,[H,W,focal],i_test


def _load_data(basedir, factor = None, width=None,height=None,end_iterion=424):
    imgs_idx =[]
    c2w=[]
    cam2world_file = os.path.join(basedir,'cam0_to_world.txt')
    with open(cam2world_file) as f:
        lines = f.readlines()
        for line in lines:
            if end_iterion <= 10:
                lineData = line.strip().split()
                imgs_idx.append(eval(lineData[0]))
                c2w.append(np.array(lineData[1:]).astype(np.float).reshape(4,4))

            end_iterion -= 1
            if end_iterion < 0:
                break
    c2w = np.array(c2w).astype(np.float32)
    print("cam2world Loaded!")

    ''' Load corrlected images'''
    def imread(f):
        if f.endswith('png'):
            return imageio.imread(f, ignoregamma=True)
        else:
            return imageio.imread(f)

    imgae_dir = os.path.join(basedir,'2013_05_28_drive_0000_sync/image_00/data_rect')

    imga_file = [os.path.join(imgae_dir,f"{'%010d'% idx}.png") for idx in imgs_idx ]  ##"010d“ 将 idx前面补成10位
    # length = len(imga_file)
    imgs = [imread(f)[...,:3]/255. for f in imga_file]
    for i,idx in enumerate(imgs_idx):
        cv.imwrite(f"train/{'%010d'% idx}.png", imgs[i] * 255)

    imgs = np.stack(imgs,-1)
    imgs = np.moveaxis(imgs, -1, 0)

    '''Load intrinstic matrix'''
    intrinstic_file = os.path.join(basedir,'perspective.txt')
    with open(intrinstic_file) as f:
        lines = f.readlines()
        for line in lines:
            lineData = line.strip().split()
            if lineData[0] == 'P_rect_00:':
                K = [float(x) for x in lineData[1:]]
                K = np.array(K).reshape(3,4)[:,:3]

    '''Generate test file'''
    i_test = np.array([5,7])

    return c2w,imgs,K,i_test

def Normailize_T(poses):
    for i,pose in enumerate(poses):
        if i == 0:
            inv_pose = np.linalg.inv(pose)
            poses[i] = np.eye(4)
        else:
            poses[i] = np.dot(inv_pose,poses[i])
    return poses


