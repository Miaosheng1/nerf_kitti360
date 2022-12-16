## load_kitti360.py 是针对Nerf代码如何读取Kitti360的文件

文件目录如下

>├── 2013_05_28_drive_0000_sync  
>├── cam0_to_world.txt  
>└── perspective.txt  

单目：
1. *perspective.txt* 存放 相机0 1内参矩阵  
2. *cam0_to_world.txt* 存放 相机0到世界系的位子变换矩阵T  
3. *2013_05_28_drive_0000_sync* 存放RGB 图像  
**输出位姿pose、 images、 render_pose、 hwf、 itest 等返回值**  
设定：Near=0 Far=100

双目：
需要读取kitti360的pose.txt 文件 和 cam1topose.txt 文件，才能求出cam1toworld 的变换矩阵

*目前的代码是按照双目去写的*
***
## Camera_Pose.py 是将相机的外参位姿使用matpltLib 绘制出来进行可视化的

## 遇到的Bug
* kitti360 的pose 矩阵中用到的相机坐标系是 Opencv系，Nerf 中原本生成的光线Code 是按照OpenGL系写的，因此需要修改get_ray 函数
* 不同的Kitti360的序列集的 PSNR 不一样，选择 start_index = 3353 附近，PSnr 可以训练到25左右。testview 的PSNR 可以训练到21左右
