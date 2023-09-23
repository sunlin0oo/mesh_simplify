# -*- coding: utf-8 -*-
"""
@author: Anton Wang
"""

# 3D model class

import numpy as np
# read 3d model , calculate_plane and calculate_Q
class a_3d_model:
    def __init__(self, filepath):
        self.model_filepath=filepath
        self.load_obj_file()
        self.calculate_plane_equations()
        self.calculate_Q_matrices()
    # 无冗余的顶点(几何结构)
    # 面的拓扑结构信息
    # 线的拓扑结构信息
    def load_obj_file(self):
        with open(self.model_filepath) as file:
            self.points = []
            self.faces = []
            while 1:
                line = file.readline()
                if not line:
                    break
                strs = line.split(" ")
                if strs[0] == "v":
                    # 在哪里定义了这个points数组
                    self.points.append((float(strs[1]), float(strs[2]), float(strs[3])))
                if strs[0] == "f":
                    # add Vertex Index ===>2维数组
                    self.faces.append((int(strs[1]), int(strs[2]), int(strs[3])))
        # 变成了多维数组  self.points (x,3)  row:vertexIndex column:xyz  
        self.points=np.array(self.points)
        # self.faces (x,3)  row:faceIndex column:vertexIndex  3 : 三角面片的顶点索引
        self.faces=np.array(self.faces)
        # 索引为 0 的维度表示行数，索引为 1 的维度表示列数
        self.number_of_points=self.points.shape[0]
        self.number_of_faces=self.faces.shape[0]
        # 选择每行的第0 1列==>使用逗号来分隔切片操作的维度。逗号的作用是分隔索引的维度，以指定要在每个维度上取的范围
        # [行,列] = [Cstart:Cend,Rstart:Rend]  edge （x,2）
        edge_1=self.faces[:,0:2]
        # Selected all columns starting from the second column of each row  2 3
        edge_2=self.faces[:,1:]
        # 1 3 axis=1 columns sorting
        edge_3=np.concatenate([self.faces[:,:1], self.faces[:,-1:]], axis=1)
        # rows sorting
        self.edges=np.concatenate([edge_1, edge_2, edge_3], axis=0)
        # unique_edges_trans 将包含 self.edges 数组中的唯一边的唯一标识符，并按照它们在 self.edges 中第一次出现的顺序进行排序。
        # unique_edges_locs 将包含唯一边在 self.edges 中第一次出现的索引位置。
        unique_edges_trans, unique_edges_locs=np.unique(self.edges[:,0]*(10**10)+self.edges[:,1], return_index=True)
        # contain unique edges ==> 挑选出不重叠的行
        self.edges=self.edges[unique_edges_locs,:]
    
    def calculate_plane_equations(self):
        # number_of_faces * 4 ===> p matrices
        self.plane_equ_para = []
        for i in range(0, self.number_of_faces):
            # solving equation ax+by+cz+d=0, a^2+b^2+c^2=1
            # set d=-1, give three points (x1, y1 ,z1), (x2, y2, z2), (x3, y3, z3)
            # 根据第 i 个面的第(0,1,2)个顶点索引，从 self.points 数组中取出对应的顶点坐标。
            point_1=self.points[self.faces[i,0]-1, :]
            point_2=self.points[self.faces[i,1]-1, :]
            point_3=self.points[self.faces[i,2]-1, :]
            # vertex matrices vi
            point_mat=np.array([point_1, point_2, point_3])
            # 通过求解线性方程组 point_mat * abc = [1, 1, 1]，计算得到系数矩阵 abc ==>解线性方程组的系数
            abc=np.matmul(np.linalg.inv(point_mat), np.array([[1],[1],[1]]))
            # np.concatenate([abc.T, np.array(-1).reshape(1, 1)] 拼接成(1, 4)==>表示完整的平面参数 (a, b, c, d)
            # (np.sum(abc**2)**0.5)计算 abc 矩阵的范数，即平方和的平方根
            # 归一化操作可以确保平面参数满足平方和为1的条件
            self.plane_equ_para.append(np.concatenate([abc.T, np.array(-1).reshape(1, 1)], axis=1)/(np.sum(abc**2)**0.5))
        self.plane_equ_para=np.array(self.plane_equ_para)
        # self.plane_equ_para row:面的数量, column:4 (a, b, c, d)
        self.plane_equ_para=self.plane_equ_para.reshape(self.plane_equ_para.shape[0], self.plane_equ_para.shape[2])
    # 计算出所有点的Q矩阵==>不怎么明白这样计算的目的，需要再进行仔细查看
    def calculate_Q_matrices(self):
        self.Q_matrices = []
        for i in range(0, self.number_of_points):
            point_index=i+1
            # each point is the solution of the intersection of a set of planes
            # find the planes for point_index
            # 找到了与当前点相关的面的索引
            face_set_index=np.where(self.faces==point_index)[0]
            Q_temp=np.zeros((4,4))
            for j in face_set_index:
                # 取出第j个平面(第j行)
                p=self.plane_equ_para[j,:]
                p=p.reshape(1, len(p))
                # np.matmul(p.T, p) == Kp
                Q_temp=Q_temp+np.matmul(p.T, p)
            self.Q_matrices.append(Q_temp)