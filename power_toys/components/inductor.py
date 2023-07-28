import numpy as np
import os
import json
import requests
from scipy.interpolate import griddata
import torch
import torch.nn as nn
import joblib
from .BaseComponent import BaseComponent

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(3, 50)
        self.fc2 = nn.Linear(50, 50)
        self.fc3 = nn.Linear(50, 3)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
class Inductor(BaseComponent):
    def __init__(self,id) -> None:
        self.id = id
        self.load_loss_model()
        self.dc_loss = 0
        self.ac_loss = 0
        self.temp = 0
        self.N_series = 1

    def series_connect(self,N):
        self.N_series = N
        return self
    
    @property
    def series(self):
        return self.model['PhotoId'].upper()
        
    @property
    def inductance(self):
        data = self.model['L']*1e-6*self.N_series
        return data
    
    @property
    def isat(self):
        """这个参数是电感值下降30%的饱和电流

        Returns:
            _type_: _description_
        """
        data = self.model['Isat']
        return data

    @property
    def length(self):
        return self.model['Length']
    
    @property
    def width(self):
        return self.model['Width']*self.N_series
    
    @property
    def height(self):
        return self.model['Height']
    
    @property
    def dcr(self):
        """返回DCR的typical

        Returns:
            _type_: _description_
        """
        data = self.model['DCRTyp']
        return data*self.N_series

    def load_loss_model(self):
        if(os.path.exists(self.loss_model_file)):
            with open(self.loss_model_file,'r') as f:
                model = json.load(f)
            self.model = model
        else:
            print("Model not found")
            self.model = None

    @classmethod
    def list_all(cls):
        __root__ = os.path.dirname(__file__)
        result = os.listdir(__root__+"/../data/coilcraft_model")
        return [x[:-4] for x in result]

    @property
    def loss_model_file(self):
        __root__ = os.path.dirname(__file__)
        return __root__+f"/../data/coilcraft_model/{self.id}.txt"
    
    def get_loss(self,dc,ac_lower,ac_upper,freq_lower,freq_upper,calc_type):
        """计算损耗

        Args:
            dc (A): 直流电流
            ac_lower (A): 纹波pk-pk的最大值
            ac_upper (A): 纹波pk-pk的最小值
            freq_lower (Hz): 频率的最小值
            freq_upper (Hz): 频率的最大值
            calc_type(str): Frequency|Ripple
        Returns:
            list:分别是0:电流ripple，1：交流损耗,2:直流损耗
        """
        _url = 'https://www.coilcraft.com/api/partssearch/explore-losses'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Mobile Safari/537.36',
            'request-context':'appId=cid-v1:b8de02ec-3510-4f92-b94d-04ab30614bc6',
            'accept':'application/json, text/plain, */*',
            'content-type':'application/json;charset=UTF-8',
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'zh-CN,zh;q=0.9'
        }
        freq_lower = freq_lower/1e6
        freq_upper = freq_upper/1e6
        
        if(freq_upper<freq_lower):
            print("Check frequency value")
            return
        if(ac_upper<ac_lower):
            print("Check ripple value")
        payload ={
            "ExploreLossesInputModel":{
                "Frequency":{
                    "Lower":freq_lower,
                    "Upper":freq_upper
                },
                "RippleCurrent":{
                    "Lower":ac_lower,
                    "Upper":ac_upper,
                    "UnitString":"A"
                },
                "CurrentIDC":dc,
                "AmbientTemperature":25,
                "Interval":10,
                "GraphType":calc_type
            },
            "LossCalculationData":[self.model]
        }
        x = requests.post(_url, data =json.dumps(payload),headers=headers)
        data = json.loads(x.text)
        data = data['LossCalculationData'][0]['LossCalculations']
        x_val = []
        ac_loss_val = np.array([])
        dc_loss_val = np.array([])
        temp_val = np.array([])

        for item in data:
            x_val.append(item['XAxis'])
            ac_loss_val = np.append(ac_loss_val,item['ACLoss']/1e3)
            dc_loss_val = np.append(dc_loss_val,item['DCLoss']/1e3)
            temp_val    = np.append(temp_val,item['PartTemperature'])
        return [x_val,ac_loss_val,dc_loss_val,temp_val]

    def get_loss_by_ripple(self,dc,ac_lower,ac_upper,freq):
        """固定频率，计算损耗

        Args:
            dc (A): 直流电流
            ac_lower (A): 纹波pk-pk的最大值
            ac_upper (A): 纹波pk-pk的最小值
            freq (Hz): 频率的最小值
        Returns:
            list:分别是0:电流ripple，1：交流损耗,2:直流损耗
        """
        return self.get_loss(dc,ac_lower,ac_upper,freq,freq,"Ripple")
    
    def get_loss_by_frequency(self,dc,ac,freq_lower,freq_upper):
        """固定纹波量，计算损耗

        Args:
            dc (A): 直流电流
            ac (A): 纹波pk-pk的最大值
            freq_lower (MHz): 频率的最小值
            freq_upper (MHz): 频率的最大值
        Returns:
            list:分别是0:电流ripple，1：交流损耗,2:直流损耗
        """
            # print(model)
        return self.get_loss(dc,ac,ac,freq_lower,freq_upper,"Frequency")
    
    def predict_loss(self,dc,ac,freq):
        """根据本地的数据进行预测

        Args:
            dc (_type_): _description_
            ac (_type_): _description_
            freq (_type_): _description_

        Returns:
            _type_: _description_
        """
        if(dc+ac/2 > self.isat):
            print("Saturated by current")
            return 0
        else:
            data = np.loadtxt(f'{os.path.dirname(__file__)}/../data/coilcraft_loss_for_training/{self.id}.txt',delimiter=',')

            # # 将数据分割为输入（features）和输出（targets）
            features = data[:, 0:3]
            targets = data[:, 3:6]

            arr = np.array([[dc,ac,freq]])
            xyz_new = griddata(features, targets, arr, method='linear')[0]
            return(xyz_new[:-1])
    
    def predict_AI(self,dc,ac,freq):
        """根据机器学习的模型来预测损耗

        Args:
            dc (A): 直流电流
            ac (A): 交流电流
            freq (Hz): 频率

        Returns:
            _type_: [DC损耗,AC损耗,温度]
        """
        # 加载模型
        model = Net()
        model.load_state_dict(torch.load(f'{os.path.dirname(__file__)}/../data/trained_model/coilcraft/{self.id}.pth'))
        model.eval()
        input_new = np.array([[dc,ac,freq/1e6]])

        X_scaler = joblib.load(f"{os.path.dirname(__file__)}/../data/scaler/coilcraft/{self.id}_x_scaler.pkl")
        y_scaler = joblib.load(f"{os.path.dirname(__file__)}/../data/scaler/coilcraft/{self.id}_y_scaler.pkl")

        new_scaled = X_scaler.transform(input_new)
        inputs = torch.from_numpy(new_scaled).float()
        outputs = model(inputs)
        xyz_out = y_scaler.inverse_transform(outputs.detach().numpy())[0]
        return xyz_out
    
    @property
    def loss_dc(self):
        idc = self.circuit_param('iave')
        iac = self.circuit_param('iripple')
        fs = self.circuit_param('fs')
        return self.predict_AI(idc,iac,fs)[0]

    @property
    def loss_ac(self):
        idc = self.circuit_param('iave')
        iac = self.circuit_param('iripple')
        fs = self.circuit_param('fs')
        return self.predict_AI(idc,iac,fs)[1]

    @property
    def temperature(self):
        idc = self.circuit_param('iave')
        iac = self.circuit_param('iripple')
        fs = self.circuit_param('feq')
        return self.predict_AI(idc,iac,fs)[2]

    def __str__(self) -> str:
        return f"Inductor: {self.id} with inductance: {self.inductance}, DCR: {self.dcr}, dimensions: {self.length}mm *{self.width}mm *{self.height}mm."

    @classmethod
    def id_from_inductance(cls,inductance,series):
        if(inductance>=9.9e-6):
            id = f"{series}-{inductance*1e6:.0f}3"
        elif(inductance >= 0.99e-6):
            id = f"{series}-{inductance*1e7:.0f}2"
        elif(inductance >= 0.099e-6):
            id = f"{series}-{inductance*1e8:.0f}1"  
        return id