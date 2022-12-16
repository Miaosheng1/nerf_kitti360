## load_kitti360.py 是针对Nerf代码如何读取Kitti360的文件

文件目录如下

>├── 2013_05_28_drive_0000_sync  
>├── cam0_to_world.txt  
>└── perspective.txt  

1. *perspective.txt* 存放 相机内参矩阵  
2. *cam0_to_world.txt* 存放 相机到世界系的位子变换矩阵T  
3. *2013_05_28_drive_0000_sync* 存放RGB 图像  
**输出位姿pose、 images、 render_pose、 hwf、 itest 等返回值**  
设定：Near=0 Far=100

***
## Camera_Pose.py 是将相机的外参位姿使用matpltLib 绘制出来进行可视化的


