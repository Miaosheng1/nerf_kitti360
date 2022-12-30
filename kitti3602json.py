import os,imageio
import torch
import numpy as np
import json

'''
Output: images, poses, bds, render_pose, itest;
poses (是指的 c2w 的pose)
'''

def main(datadir):
    poses, imgs, K =_load_data(datadir)
    focal = K[0][0]
    ## 设第一张相机的Pose 是单位矩阵，对其他相机的Pose 需要进行调整为相对于第一帧的Pose 相对位姿
    poses = Normailize_T(poses)   ## 对于 平移translation 进行归一化

    return tojson(poses,focal,imgs)

def tojson(poses,focal,imgs):
    def listify_matrix(matrix):
        matrix_list = []
        for row in matrix:
            matrix_list.append(list(row))
        return matrix_list

    spilts = ['train','val']
    skip_spilt={
        'train':1,
        'val':3
    }


    for spilt in spilts:
        out_data = {'camera_angle_x': 1.8107}
        out_data['frames'] = []

        os.makedirs(spilt, exist_ok=True)

        for i in range(0,poses.shape[0],skip_spilt[spilt]):

            frame_data = {
                'file_path': './'+ spilt + '/r_' + str(i),
                'transform_matrix': listify_matrix(poses[i])
            }
            filename =os.path.join(spilt,'r_'+ str(i))+".png"
            imageio.imwrite(filename,imgs[i])

            out_data['frames'].append(frame_data)

        with open(f'transforms_{spilt}.json', 'w') as out_file:
            json.dump(out_data, out_file, indent=4)



def _load_data(datadir,end_iterion=424,sequence ='2013_05_28_drive_0000_sync'):
    '''Load intrinstic matrix'''
    intrinstic_file = os.path.join(os.path.join(datadir, 'calibration'), 'perspective.txt')
    with open(intrinstic_file) as f:
        lines = f.readlines()
        for line in lines:
            lineData = line.strip().split()
            if lineData[0] == 'P_rect_00:':
                K_00 = np.array(lineData[1:]).reshape(3,4).astype(np.float)
            elif lineData[0] == 'P_rect_01:':
                K_01 = np.array(lineData[1:]).reshape(3,4).astype(np.float)
            elif lineData[0] == 'R_rect_01:':
                R_rect_01 = np.eye(4)
                R_rect_01[:3,:3] = np.array(lineData[1:]).reshape(3,3).astype(np.float)

    '''Load extrinstic matrix'''
    CamPose_00 = {}
    CamPose_01 = {}
    extrinstic_file = os.path.join(datadir,os.path.join('data_poses',sequence))
    cam2world_file_00 = os.path.join(extrinstic_file,'cam0_to_world.txt')
    pose_file = os.path.join(extrinstic_file,'poses.txt')


    ''' Camera_00  to world coordinate '''
    with open(cam2world_file_00,'r') as f:
        lines = f.readlines()
        for line in lines:
            lineData = list(map(float,line.strip().split()))
            CamPose_00[lineData[0]] = np.array(lineData[1:]).reshape(4,4)

    ''' Camera_01 to world coordiante '''
    CamToPose_01 = loadCameraToPose(os.path.join(os.path.join(datadir, 'calibration'),'calib_cam_to_pose.txt'))
    poses = np.loadtxt(pose_file)
    frames = poses[:, 0]
    poses = np.reshape(poses[:, 1:], [-1, 3, 4])
    for frame, pose in zip(frames, poses):
        pose = np.concatenate((pose, np.array([0., 0., 0., 1.]).reshape(1, 4)))
        pp = np.matmul(pose, CamToPose_01)
        CamPose_01[frame] = np.matmul(pp, np.linalg.inv(R_rect_01))



    ''' Load corrlected images camera 00--> index    camera 01----> index+1'''
    def imread(f):
        if f.endswith('png'):
            return imageio.imread(f, ignoregamma=True)
        else:
            return imageio.imread(f)

    imgae_dir = os.path.join(datadir,sequence)
    image_00 = os.path.join(imgae_dir,'image_00/data_rect')
    image_01 = os.path.join(imgae_dir,'image_01/data_rect')

    start_index = 3353
    num = 8
    all_images = []
    all_poses = []

    for idx in range(start_index,start_index+num,1):
        ## read image_00
        image = imread(os.path.join(image_00,"{:010d}.png").format(idx))
        all_images.append(image)
        all_poses.append(CamPose_00[idx])

        ## read image_01
        image = imread(os.path.join(image_01, "{:010d}.png").format(idx))
        all_images.append(image)
        all_poses.append(CamPose_01[idx])


    imgs = np.stack(all_images,-1)
    imgs = np.moveaxis(imgs, -1, 0)
    c2w = np.stack(all_poses)


    return c2w,imgs, K_00

def Normailize_T(poses):
    for i,pose in enumerate(poses):
        if i == 0:
            inv_pose = np.linalg.inv(pose)
            poses[i] = np.eye(4)
        else:
            poses[i] = np.dot(inv_pose,poses[i])

    '''New Normalization '''
    scale = poses[-1,2,3]
    print(f"scale:{scale}\n")
    for i in range(poses.shape[0]):
        poses[i,:3,3] = poses[i,:3,3]/scale
        poses[i,:3,:3] = poses[i,:3,:3] * np.array([1, -1, -1])  ## opencv2openGL
        print(poses[i])
    return poses


def loadCameraToPose(filename):
    # open file
    Tr = {}
    lastrow = np.array([0, 0, 0, 1]).reshape(1, 4)
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            lineData = list(line.strip().split())
            if lineData[0] == 'image_01:':
                data = np.array(lineData[1:]).reshape(3,4).astype(np.float)
                data = np.concatenate((data,lastrow), axis=0)
                Tr[lineData[0]] = data

    return Tr['image_01:']

if __name__ == '__main__':
    main('/data/datasets/KITTI-360')
