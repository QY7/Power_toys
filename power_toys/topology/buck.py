import numpy as np
from power_toys.log import log_error
from operator import methodcaller
from power_toys.waveform import triangle_rms
from numpy import floor
from power_toys.components.inductor.coilcraft import Coilcraft
from power_toys.components.inductor.base_inductor import BaseInductor
from ..components.mosfet.base_mosfet import MOSFET
from ..common.const import *
from ..components.Base import BaseComponent,BaseCircuit
import copy

class BUCK(BaseCircuit):
    def __init__(self,vin = None,vo = None,q_active:MOSFET = None,q_passive:MOSFET = None,ind:BaseInductor = None,fs = None,po = None,Ncell = 1) -> None:
        super().__init__()
        self.vin = vin
        self.vo = vo
        self._fs = fs
        self.po = po
        self.Ncell = Ncell
        
        self.register_component(q_active,BUCK_COMPONENT.ACTIVE_MOS,quantity=Ncell)
        self.register_component(q_passive,BUCK_COMPONENT.PASSIVE_MOS,quantity=Ncell)
        self.register_component(ind,BUCK_COMPONENT.INDUCTOR)

    @property
    def ind(self):
        return getattr(self,f"c_{BUCK_COMPONENT.INDUCTOR}")
    
    @property
    def duty_eff(self):
        duty_tmp = self.duty*self.Ncell
        return duty_tmp - floor(duty_tmp)
    
    def volt_sec(self,c_index = BUCK_COMPONENT.INDUCTOR):
        v_step = self.vin/self.Ncell
        vo_eff = self.vo%v_step
        return (v_step - vo_eff)*self.duty_eff/(self._fs*self.Ncell)
    
    # def inductor_ripple(self,c_index = BUCK_COMPONENT.INDUCTOR):
    #     if(isinstance(self.ind,float)):
    #         return self.volt_sec()/self.ind
    #     else:
    #         return self.ind.ripple
    
    def iripple(self,c_index = BUCK_COMPONENT.INDUCTOR):
        if(c_index == BUCK_COMPONENT.INDUCTOR):
            return self.volt_sec()/self.ind.inductance
        return 0
    
    @property
    def duty(self):
        try:
            return self.vo/self.vin
        except TypeError:
            log_error("参数不完整")
            return 0
    
    def irms(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        """计算电流有效值

        Args:
            c_index (int, optional): 
            - 0: 主动管
            - 1: 整流管
            - 2: 电感

        Returns:
            _type_: 电流有效值
        """
        if(c_index == BUCK_COMPONENT.ACTIVE_MOS):
            return np.sqrt(self.duty)*triangle_rms(self.io,self.iripple())
            # return np.sqrt(self.duty*(np.power(self.io,2)+np.power(self.iripple(),2)/12))
        elif(c_index == BUCK_COMPONENT.PASSIVE_MOS):
            return np.sqrt(1-self.duty)*triangle_rms(self.io,self.iripple())
        else:
            return triangle_rms(self.io,self.iripple())
    
    def off_current(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(c_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.io+self.iripple()/2
        else:
            return self.io-self.iripple()/2

    def on_current(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(c_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.io-self.iripple()/2
        else:
            return self.io+self.iripple()/2
    
    def off_voltage(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(c_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.vin/self.Ncell
        else:
            return 0

    def on_voltage(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(c_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.vin/self.Ncell
        else:
            return 0

    def cap_voltage(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        return self.vin/self.Ncell
    
    def iave(self,c_index = BUCK_COMPONENT.INDUCTOR):
        if(c_index == BUCK_COMPONENT.INDUCTOR):
            return self.vo/self.ro
        return 0
    
    def qrr_voltage(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(c_index == BUCK_COMPONENT.PASSIVE_MOS):
            return self.vin/self.Ncell
        else:
            return 0
    
    @property
    def io(self):
        return self.vo/self.ro

    def fs(self,c_index = BUCK_COMPONENT.ACTIVE_MOS):
        """获取电路的fs，注意不能直接修改fs，需要调用set_fs来设置

        Args:
            c_index (_type_, optional): _description_. Defaults to BUCK_COMPONENT.ACTIVE_MOS.

        Returns:
            _type_: _description_
        """
        if(c_index == BUCK_COMPONENT.INDUCTOR):
            return self._fs * self.Ncell
        else:
            return self._fs
        
    def set_fs(self,val):
        self._fs = val

    @property
    def optimize_eff_by_rdson(self):
        mos1 = self.get_component(BUCK_COMPONENT.ACTIVE_MOS)
        mos2 = self.get_component(BUCK_COMPONENT.PASSIVE_MOS)

        mos1_opt = mos1.mos_in_series(mos1.opt_rdson)
        mos2_opt = mos2.mos_in_series(mos2.opt_rdson)

        buck_tmp = copy.deepcopy(self)
        buck_tmp.register_component(mos1_opt,BUCK_COMPONENT.ACTIVE_MOS)
        buck_tmp.register_component(mos2_opt,BUCK_COMPONENT.PASSIVE_MOS)
        return buck_tmp
    
    @property
    def optimize_eff_by_fs(self):
        max_iter = MAX_ITER_NUM
        fs_tmp = self.fs()
        b,a = fs_tmp/100,fs_tmp*100
        phi = (1 + 5**0.5) / 2  # 黄金比例
        c = b - (b - a) / phi
        d = a + (b - a) / phi
        cnt_iter = 0
        while abs(b - a) > 1e-6:
            buck1 = copy.deepcopy(self)
            buck1.set_fs(c)
            buck2 = copy.deepcopy(self)
            buck2.set_fs(d)

            if buck1.total_loss < buck2.total_loss:
                b = d
            else:
                a = c
            c = b - (b - a) / phi
            d = a + (b - a) / phi
            cnt_iter+=1
            if(cnt_iter > max_iter):
                print(f"{max_iter}次迭代后，不收敛")
                return (b + a) / 2
        return buck1

    @property
    def optimize_eff_by_same_rdson(self):
        mos = self.get_component(BUCK_COMPONENT.ACTIVE_MOS)
        rdson_tmp = mos.rdson
        b,a = rdson_tmp/100,rdson_tmp*100
        phi = (1 + 5**0.5) / 2  # 黄金比例
        c = b - (b - a) / phi
        d = a + (b - a) / phi
        cnt_iter = 0
        while abs(b - a) > 1e-6:
            mos1_opt = mos.mos_in_series(c)
            mos2_opt = mos.mos_in_series(c)

            buck1 = copy.deepcopy(self)
            buck1.register_component(mos1_opt,BUCK_COMPONENT.ACTIVE_MOS)
            buck1.register_component(mos2_opt,BUCK_COMPONENT.PASSIVE_MOS)

            mos3_opt = mos.mos_in_series(d)
            mos4_opt = mos.mos_in_series(d)

            buck2 = copy.deepcopy(self)
            buck2.register_component(mos3_opt,BUCK_COMPONENT.ACTIVE_MOS)
            buck2.register_component(mos4_opt,BUCK_COMPONENT.PASSIVE_MOS)

            mos1_loss = buck1.total_loss
            mos2_loss = buck2.total_loss
            if mos1_loss < mos2_loss:
                b = d
            else:
                a = c
            c = b - (b - a) / phi
            d = a + (b - a) / phi
            cnt_iter+=1
            if(cnt_iter > MAX_ITER_NUM):
                break
        return buck1
    
    @property
    def mos1(self)->MOSFET:
        return self.get_component(BUCK_COMPONENT.ACTIVE_MOS)
    
    @property
    def mos2(self)->MOSFET:
        return self.get_component(BUCK_COMPONENT.PASSIVE_MOS)
    
    @property
    def inductor(self)->BaseInductor:
        return self.get_component(BUCK_COMPONENT.INDUCTOR)