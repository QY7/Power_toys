# -*- coding: UTF-8 -*-

import json
import os
from power_toys.log import log_error,log_info
from power_toys.model_params import mosfet_param_list
import numpy as np
import sqlite3 as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String,Float
from ...data.database import component_session,component_engine
import pandas as pd
from sqlalchemy.sql import select, text
from ..Base import BaseComponent
from ...common.const import *
import copy

DBBase = declarative_base()

class MOSFET(DBBase,BaseComponent):
    __tablename__ = 'MOSFET'

    id      = Column(String, primary_key=True)
    rdson   = Column(Float)
    vbr     = Column(Float)
    vgsth   = Column(Float)
    rg      = Column(Float)
    qg      = Column(Float)
    qgd     = Column(Float)
    qg_soft = Column(Float)
    cosse   = Column(Float)
    cosst   = Column(Float)
    qrr     = Column(Float)
    qgs2    = Column(Float)
    vplateau= Column(Float)
    kdyn    = Column(Float)
    ktemp   = Column(Float)
    vgs     = Column(Float)
    vgs_min = Column(Float)
    footprint = Column(String(50))
    
    def __init__(self,**kwargs) -> None:
        super().__init__()
        for key in mosfet_param_list.keys():
            setattr(self, key, None)
        for key, value in kwargs.items():
            try:
                value = float(value)
            except:
                value = value
            setattr(self, key.lower(), value)
    
    @property
    def loss_list(self):
        return ['con_loss','dri_loss','cap_loss','switch_off_loss','switch_on_loss','qrr_loss']

    def parallel(self,N=2):
        mos_tmp = copy.deepcopy(self)
        mos_tmp.rdson   = self.rdson/N
        # 假定并联使用不同的驱动器
        mos_tmp.rg      = self.rg
        mos_tmp.qg      = N*self.qg
        mos_tmp.qgd     = N*self.qgd
        mos_tmp.qg_soft = N*self.qg_soft
        mos_tmp.cosse   = N*self.cosse
        mos_tmp.cosst   = N*self.cosst
        mos_tmp.qrr     = N*self.qrr
        mos_tmp.qgs2    = N*self.qgs2
        return mos_tmp

    def mos_in_series(self,rdson):
        """获取同系列的mos的推测参数，根据FoM参数来

        Args:
            rdson (_type_): _description_

        Returns:
            _type_: _description_
        """
        N = self.rdson/rdson
        return self.parallel(N)
    
    def check_param_valid(self):
        for param in mosfet_param_list.keys():
            if(param == 'id' or param == 'footprint'):
                continue
            if(not isinstance(getattr(self,param) ,float)):
               return [param,self.id]
        return ['','']
    
    @classmethod
    def list_all_model(cls,condition):
        """查询数据库中所有的model，返回ID的数组

        Returns:
            _type_: _description_
        """
        items = component_session.query(MOSFET).filter(condition).all()
        return items
    
    @classmethod
    def load_from_lib(cls,_id = None):
        """从数据库中载入数据

        Args:
            _id (str, optional): MOSFET的型号. Defaults to None.

        Returns:
            MOSFET: MOSFET的实例
        """
        mosfet = component_session.query(MOSFET).filter_by(id=_id).first()
        return copy.deepcopy(mosfet)
    
# TODO 如果mos是深拷贝出来的，可能会有BUG
    def save_to_db(self):
        """如果已经存在，就返回已经存在的数据，否则保存数据
        """
        component_session.merge(self)
        component_session.commit()

    @property
    def NFoM(self):
        """获取等效的NFoM,考虑了温度系数和动态电阻系数

        Returns:
            _type_: _description_
        """
        return self.rdson*self.cosst*self.kdyn*self.ktemp
    
    @property
    def FoM(self):
        """获取等效的FoM,考虑了温度系数和动态电阻系数

        Returns:
            _type_: _description_
        """
        return self.rdson*self.qg*self.kdyn*self.ktemp
    
    @property
    def FoM_vgs(self):
        return self.rdson*self.qg*self.kdyn*self.ktemp*(self.vgs-self.vgs_min)
    
    @property
    def NFoMoss(self):
        """获取等效的NFoMoss,考虑了温度系数和动态电阻系数

        Returns:
            _type_: _description_
        """
        return self.cosse*self.rdson*self.kdyn*self.ktemp
    
    # @staticmethod
    # def get_FoM(vds,kind='si',vgs = '5V'):
    #     kind = kind.lower().strip()
    #     FoM = json.load()
    #     for v in FoM[kind].keys():
    #         if(int(v)>=vds):
    #             return FoM[kind][v][vgs]
            
    def _con_loss(self,irms):
        """返回导通损耗

        Args:
            irms (A): 流经桥臂的电流的有效值
        """
        try:
            return self.rdson*self.kdyn*self.ktemp*irms**2
        except TypeError:
            log_error("con_loss参数不完整，请检查mos参数")
    
    @property
    def con_loss(self):
        irms = self.circuit_param('irms')
        return self._con_loss(irms)

    def _dri_loss(self,fs):
        """计算驱动损耗

        Args:
            fs (Hz): 开关频率
        Returns:
            [W]: 驱动损耗
        """
        return self.qg*(self.vgs-self.vgs_min)*fs
        

    @property
    def dri_loss(self):
        fs = self.circuit_param('fs')
        return self._dri_loss(fs=fs)
    
    def _switch_off_loss(self,fs,vds,ids,rgo=0.6):
        """计算一个桥臂的关断损耗，采用分段线性模型进行计算

        Args:
            mos (MOSFET): MOSFET实例
            fs (Hz): 开关频率
            vds (V): Vds电压
            ids (A): DS电流
            rgo (Ohm, optional): 驱动off的电阻. Defaults to 0.6

        Returns:
            W: 损耗
        """
        try:
            # 这个时间是和外部条件没有关系的。所以可以直接由外部计算再穿入
            t = self.qgs2/((self.vplateau+self.vgsth)/2)+self.qgd/(self.vplateau)
            loss = vds*ids*(rgo+self.rg)/2*t
            return loss*fs
        except TypeError:
            log_error("off_loss参数不完整，请检查mos参数")

    @property
    def switch_off_loss(self):
        fs = self.circuit_param('fs')
        vds = self.circuit_param('off_voltage')
        ids = self.circuit_param('off_current')
        return self._switch_off_loss(fs,vds,ids)

    def _switch_on_loss(self,fs,vds,ids,rgo = 1):
        """计算一个桥臂的开通损耗，采用分段线性模型进行计算

        Args:
            mos (MOSFET): MOSFET实例
            fs (Hz): 开关频率
            vds (V): Vds电压
            ids (A): DS电流
            rgo (Ohm, optional): 驱动on的电阻. Defaults to 2.1.

        Returns:
            W: 损耗
        """
        try:
            t = self.qgs2/(self.vgs-(self.vplateau+self.vgsth)/2)+self.qgd/(self.vgs-self.vplateau)
            loss = vds*ids*(rgo+self.rg)/2*t
            return loss*fs
        except TypeError:
            log_error("switch_on_loss参数不完整，请检查mos参数")
    
    @property
    def switch_on_loss(self):
        fs = self.circuit_param('fs')
        vds = self.circuit_param('on_voltage')
        ids = self.circuit_param('on_current')
        return self._switch_on_loss(fs,vds,ids)

    def _qrr_loss(self,fs,vds):
        """反向恢复损耗计算，计算模型直接以qrr*Vds*fs来考虑

        Args:
            mos (MOSFET): MOSFET类的实例
            fs (Hz): 开关频率
            vds (V): Vds电压

        Returns:
            _type_: _description_
        """
        try:
            return self.qrr*fs*vds
        except TypeError:
            log_error("qrr_loss参数不完整，请检查mos参数")
        
    @property
    def qrr_loss(self):
        fs = self.circuit_param('fs')
        vds = self.circuit_param('qrr_voltage')
        return self._qrr_loss(fs=fs,vds=vds)

    def _cap_loss(self,fs,vds):
        """反向恢复损耗计算，计算模型直接以qrr*Vds*fs来考虑

        Args:
            mos (MOSFET): MOSFET类的实例
            fs (Hz): 开关频率
            vds (V): Vds电压

        Returns:
            _type_: _description_
        """
        try:
            return 0.5*self.cosse*fs*np.power(vds,2)
        except TypeError:
            log_error("cap_loss参数不完整，请检查mos参数")
            
    @property
    def cap_loss(self):
        fs = self.circuit_param('fs')
        vds = self.circuit_param('cap_voltage')
        return self._cap_loss(fs=fs,vds=vds)
    
    def __str__(self) -> str:
        value_list = []
        for key in mosfet_param_list:
            value = getattr(self,key)
            if(value == None):
                value_list.append(f"{key}:NULL\t")
            elif(type(value) == float):
                value_list.append(f"{key}:{value:.1E}\t")
            else:
                value_list.append(f"{key}:{value}\t")
        return ''.join(value_list)
    
    @classmethod
    def export_excel(cls,path):
        path = path.strip()
        if(path[-5:] == '.xlsx'):
            sql = "SELECT * FROM MOSFET"
            df = pd.read_sql_query(sql, component_engine)
            df.to_excel(path, engine='openpyxl', index=False)
        else:
            print("invalid file path")
            return
    
    @classmethod
    def append_from_excel(cls,path):
        df = pd.read_excel(path, engine='openpyxl')
        table_name = "MOSFET"
        with component_engine.connect() as connection:
            for index, row in df.iterrows():
                select_query = text(f"SELECT * FROM {table_name} WHERE id = :id")
                result = connection.execute(select_query, {'id': row['ID']}).fetchone()
                if result is None:
                    df.iloc[index:index+1].to_sql(table_name, con=component_engine, if_exists='append', index=False)
                else:
                    print(f"{row['ID']} 已经存在")

    @property
    def opt_rdson(self):
        """根据电路条件，通过二分法找最优的rdson

        Args:
            max_iter (int, optional): 最大的迭代次数. Defaults to 100.

        Returns:
            float: 优化的rdson
        """
        rdson_tmp = self.rdson
        b,a = rdson_tmp/100,rdson_tmp*100
        phi = (1 + 5**0.5) / 2  # 黄金比例
        c = b - (b - a) / phi
        d = a + (b - a) / phi
        cnt_iter = 0
        while abs(b - a) > 1e-6:
            mos1_loss = self.mos_in_series(c).total_loss
            mos2_loss = self.mos_in_series(d).total_loss
            if mos1_loss < mos2_loss:
                b = d
            else:
                a = c
            c = b - (b - a) / phi
            d = a + (b - a) / phi
            cnt_iter += 1
            if(cnt_iter > MAX_ITER_NUM):
                print(f"{MAX_ITER_NUM}次迭代后，不收敛")
                return (b + a) / 2
        return (b + a) / 2
    
    @property
    def vf(self):
        """反向导通电压
        """
        return 0.7
        