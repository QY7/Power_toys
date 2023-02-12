import matplotlib.pyplot as plt
import numpy as np
import os

class Curve():
    def __init__(self,data = None) -> None:
        self._data = data

    def load_from_file(self,filename,delimeter = ','):
        if ( os.path.exists(filename)):
            self.data = np.loadtxt(filename,delimiter=delimeter,unpack=True)
        return self

    def load_from_x_y(self,x,y):
        self.data = np.concatenate((np.array([x]).T,np.array([y]).T),axis=1)
        return self

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self,d):
        self._data = d

    @property
    def x(self):
        return self._data[:,0]
    
    @property
    def y(self):
        return self._data[:,1]
    
    def yxdx(self,xmax,xmin = 0):
        idx_filter = (self.x<=xmax) & (self.x >= xmin)
        return np.trapz((self.x*self.y)[idx_filter],self.x[idx_filter])

    def energy(self,vmax,vmin = 0):
        """根据C-V曲线计算等效，根据C*V*deltaV计算

        Args:
            v (list)): 电压数组
            c (list): 电容数组
            vmax (float): 电压最大值
            vmin (float, optional): 电压最小值. Defaults to 0.
        """
        return self.yxdx(vmax,vmin)
    
    def energy_equivalent(self,vmax,vmin=0):
        """根据C-V曲线计算能量等效电容，根据C*V*deltaV计算能量

        Args:
            v (list): 电压数组
            c (list): 电容数组
            vmax (float): 电压最大值
            vmin (float, optional): 电压最小值. Defaults to 0.

        Returns:
            float: 能量等效电容
        """
        return self.energy(vmax,vmin)/vmax**2*2
        
    def ydx(self,xmax,xmin=0):
        idx_filter = (self.x<=xmax) & (self.x >= xmin)
        return np.trapz(self.y[idx_filter],self.x[idx_filter])
    @property
    def average(self):
        return np.trapz(self.y,self.x)/np.abs(self.x[0]-self.x[-1])

    def charge(self,vmax,vmin = 0):
        """根据电压和电容数组数值积分计算电荷

        Args:
            v (array): 电压数组
            c (array): 电容数组
            vmax (float): 积分的电压最大值
            vmin (float, optional): 积分的电压最小值. Defaults to 0.

        Returns:
            C: 电荷量
        """
        return self.ydx(vmax,vmin)
    
    def time_equivalent(self,vmax,vmin=0):
        """根据C-V曲线计算时间等效电容，根据C*deltaV计算等效电荷

        Args:
            vmax (float): 电压最大值
            vmin (float, optional): 电压最小值. Defaults to 0.

        Returns:
            float: 时间等效电容
        """
        return self.charge(vmax,vmin)/vmax
