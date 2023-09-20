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
                    # add Vertex Index
                    self.faces.append((int(strs[1]), int(strs[2]), int(strs[3])))
        self.points=np.array(self.points)
        self.faces=np.array(self.faces)
        self.number_of_points=self.points.shape[0]
        self.number_of_faces=self.faces.shape[0]
        # Select the first two columns of each row 1 2
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
        # contain unique edges
        self.edges=self.edges[unique_edges_locs,:]
    
    def calculate_plane_equations(self):
        self.plane_equ_para = []
        for i in range(0, self.number_of_faces):
            # solving equation ax+by+cz+d=0, a^2+b^2+c^2=1
            # set d=-1, give three points (x1, y1 ,z1), (x2, y2, z2), (x3, y3, z3)
            point_1=self.points[self.faces[i,0]-1, :]
            point_2=self.points[self.faces[i,1]-1, :]
            point_3=self.points[self.faces[i,2]-1, :]
            point_mat=np.array([point_1, point_2, point_3])
            abc=np.matmul(np.linalg.inv(point_mat), np.array([[1],[1],[1]]))
            self.plane_equ_para.append(np.concatenate([abc.T, np.array(-1).reshape(1, 1)], axis=1)/(np.sum(abc**2)**0.5))
        self.plane_equ_para=np.array(self.plane_equ_para)
        self.plane_equ_para=self.plane_equ_para.reshape(self.plane_equ_para.shape[0], self.plane_equ_para.shape[2])
    
    def calculate_Q_matrices(self):
        self.Q_matrices = []
        for i in range(0, self.number_of_points):
            point_index=i+1
            # each point is the solution of the intersection of a set of planes
            # find the planes for point_index
            face_set_index=np.where(self.faces==point_index)[0]
            Q_temp=np.zeros((4,4))
            for j in face_set_index:
                p=self.plane_equ_para[j,:]
                p=p.reshape(1, len(p))
                Q_temp=Q_temp+np.matmul(p.T, p)
            self.Q_matrices.append(Q_temp)