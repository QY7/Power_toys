import matplotlib.pyplot as plt
import numpy as np
import os
from power_toys.model_params import curve_type_list
from power_toys.log import log_error,log_info

curve_path = f"{os.path.dirname(__file__)}\data\curve"

class Curve():
    def __init__(self,id = None,curve_type = None) -> None:
        """从数据库中载入曲线数据

        Args:
            id (str): 曲线对应的元器件的型号
            curve_type (str): 曲线对应的类型，比如Coss曲线等
        """
        self.data = None
        if id:
            id = id.lower().strip()
        if curve_type:
            curve_type = curve_type.lower().strip()
        
        self.id = id
        self.curve_type = curve_type
        
        if(curve_type and id):
            # Check whether the type is valid
            if(curve_type not in curve_type_list):
                log_error("Unregistered curve type, register it in model_params.py")
                return
            self.load_from_db(id,curve_type)
        return

    def load_from_file(self,filename,delimeter = ';'):
        """载入文件中的数据

        Args:
            filename (str): 数据文件名字
            delimeter (str, optional): 分隔符. Defaults to ';'.

        Returns:
            Curve(): 返回实例
        """
        if ( os.path.exists(filename)):
            # The dimension of self.data is n x 2
            self.data = np.loadtxt(filename,delimiter=delimeter,unpack=True).T
        return self
    
    def load_from_db(self,id,curve_type):
        """从已有的数据库中载入数据

        Args:
            id (str): 曲线对应的元器件的型号
            curve_type (str): 曲线对应的类型，比如Coss曲线等
        """
        self.id = id.lower().strip()
        self.curve_type = curve_type.lower().strip()
        curve_file = self.file_name()
        self.load_from_file(curve_file)
        self.save_curve()
        
    def file_name(self):
        return f"{curve_path}\{self.id}_{self.curve_type}.txt"
    
    def load_from_x_y(self,x,y):
        """给定np_array类型进行初始化

        Args:
            x (list): x数组
            y (list): y数组

        Returns:
            Curve(): 返回实例
        """
        self.data = np.concatenate((np.array([x]).T,np.array([y]).T),axis=1)
        return self
    
    def save_curve(self):
        
        if(self.id == None):
            self.id = input("输入型号:\n")

        if(self.curve_type == None):
            self.curve_type = input("请输入曲线类型:\n")
        while(self.curve_type not in curve_type_list):
            log_error("未知曲线类型，重新输入。")
            self.curve_type = input("请输入曲线类型:\n")
            
        file_path=self.file_name()
        data_tmp = np.column_stack((self.x,self.y)).reshape(len(self.x),2)
        if(os.path.isfile(file_path)):
            log_info("文件已经存在，是否覆盖？Y/N")
            answer = input().lower().strip()
            if(answer[0] == 'y'):
                np.savetxt(file_path,data_tmp,delimiter=";")
                log_info(f"{self.file_name()} has been saved")
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
