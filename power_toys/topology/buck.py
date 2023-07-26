import numpy as np
from power_toys.log import log_error
from operator import methodcaller
from power_toys.waveform import triangle_rms
from numpy import floor
from power_toys.components.inductor import Inductor
from ..components.mosfet import MOSFET
from ..common.const import *
from ..components.BaseComponent import BaseComponent

class BUCK():
    def __init__(self,vin = None,vo = None,q_active:MOSFET = None,q_passive:MOSFET = None,ind:Inductor = None,fs = None,ro = None,Ncell = 1) -> None:
        self.vin = vin
        self.vo = vo
        self._fs = fs
        self.ro = ro
        self.Ncell = Ncell

        self.register_component(q_active,BUCK_COMPONENT.ACTIVE_MOS)
        self.register_component(q_passive,BUCK_COMPONENT.PASSIVE_MOS)
        self.register_component(ind,BUCK_COMPONENT.INDUCTOR)

    def get_component(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        return getattr(self,f"q_{q_index}")
    
    def register_component(self,component:BaseComponent,q_index = BUCK_COMPONENT.INDUCTOR):
        component.assign_circuit(self)
        component.circuit_idx = q_index
        setattr(self,f"q_{q_index}",component)

    @property
    def ind(self):
        return getattr(self,f"q_{BUCK_COMPONENT.INDUCTOR}")
    
    @property
    def duty_eff(self):
        duty_tmp = self.duty*self.Ncell
        return duty_tmp - floor(duty_tmp)
    
    @property
    def volt_sec(self):
        v_step = self.vin/self.Ncell
        vo_eff = self.vo%v_step
        return (v_step - vo_eff)*self.duty_eff/(self._fs*self.Ncell)
    
    @property
    def inductor_ripple(self):
        return self.iripple()
    
    def iripple(self,q_index = BUCK_COMPONENT.INDUCTOR):
        if(q_index == BUCK_COMPONENT.INDUCTOR):
            try:
                if(isinstance(self.ind,float)):
                    return self.volt_sec/self.ind
                else:
                    return self.volt_sec/self.ind.inductance
            except TypeError:
                log_error("参数不完整")
                return 0
        else:
            return 0
    
    @property
    def duty(self):
        try:
            return self.vo/self.vin
        except TypeError:
            log_error("参数不完整")
            return 0

    @property
    def po(self):
        return np.power(self.vo,2)/self.ro
    
    def irms(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        """计算电流有效值

        Args:
            q_index (int, optional): 
            - 0: 主动管
            - 1: 整流管
            - 2: 电感

        Returns:
            _type_: 电流有效值
        """
        if(q_index == BUCK_COMPONENT.ACTIVE_MOS):
            return np.sqrt(self.duty)*triangle_rms(self.io,self.inductor_ripple)
            # return np.sqrt(self.duty*(np.power(self.io,2)+np.power(self.inductor_ripple,2)/12))
        elif(q_index == BUCK_COMPONENT.PASSIVE_MOS):
            return np.sqrt(1-self.duty)*triangle_rms(self.io,self.inductor_ripple)
        else:
            return triangle_rms(self.io,self.inductor_ripple)
    
    def off_current(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(q_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.io+self.inductor_ripple/2
        else:
            return self.io-self.inductor_ripple/2

    def on_current(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(q_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.io-self.inductor_ripple/2
        else:
            return self.io+self.inductor_ripple/2
    
    def off_voltage(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(q_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.vin/self.Ncell
        else:
            return 0

    def on_voltage(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(q_index == BUCK_COMPONENT.ACTIVE_MOS):
            return self.vin/self.Ncell
        else:
            return 0

    def cap_voltage(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        return self.vin/self.Ncell
    
    def iave(self,q_index = BUCK_COMPONENT.INDUCTOR):
        if(q_index == BUCK_COMPONENT.INDUCTOR):
            return self.vo/self.ro
        return 0
    
    def qrr_voltage(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        if(q_index == BUCK_COMPONENT.PASSIVE_MOS):
            return self.vin/self.Ncell
        else:
            return 0
    
    @property
    def io(self):
        return self.vo/self.ro
    
    def p_con(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        mos = getattr(self,f"q_{q_index}")
        return mos.con_loss*self.Ncell
    
    def p_dri(self,q_index):
        mos = getattr(self,f"q_{q_index}")
        return mos.dri_loss*self.Ncell
    
    def p_on(self,q_index):
        # Q2为软开通
        mos = getattr(self,f"q_{q_index}")
        return mos.switch_on_loss*self.Ncell
    
    def p_off(self,q_index):
        mos = getattr(self,f"q_{q_index}")
        return mos.switch_off_loss*self.Ncell
    
    def p_qrr(self,q_index):
        mos = getattr(self,f"q_{q_index}")
        return mos.qrr_loss*self.Ncell
        
    def p_cap(self,q_index):
        mos = getattr(self,f"q_{q_index}")
        return mos.cap_loss*self.Ncell

    def fs(self,q_index):
        if(q_index == BUCK_COMPONENT.INDUCTOR):
            return self._fs * self.Ncell
        else:
            return self._fs
    
    def p_ind_dc(self):
        return self.ind.loss_dc
    
    def p_ind_ac(self):
        return self.ind.loss_ac
    
    def temperature_ind(self):
        return self.ind.temperature
    
    def param(self,component:BaseComponent,param_name):
        func = getattr(self, param_name, None)
        if func is not None and callable(func):
            return func(q_index=component.circuit_idx)
        else:
            raise ValueError(f"No such method: {param_name}")
        
    def p_total(self):
        mos_idx_list = [BUCK_COMPONENT.ACTIVE_MOS,BUCK_COMPONENT.PASSIVE_MOS]
        loss_list = ["p_con",'p_on',"p_off","p_dri","p_qrr","p_cap"]
        loss_total = 0
        for mos_idx in mos_idx_list:
            for loss_name in loss_list:
                loss_total += methodcaller(loss_name,mos_idx)(self)
        try:
            loss_total = loss_total+ self.p_ind_ac() + self.p_ind_dc()
        except AttributeError:
            log_error("No inductor loss")
        return loss_total
    
    def p_total_on_mos(self,q_index = BUCK_COMPONENT.ACTIVE_MOS):
        loss_list = ["p_con",'p_on',"p_off","p_dri","p_qrr","p_cap"]
        loss_total = 0
        for loss_name in loss_list:
            loss_total += methodcaller(loss_name,q_index)(self)
        return loss_total
    
    def calc_replace_mos(self,rdson):
        mos_ori = self.get_component(BUCK_COMPONENT.ACTIVE_MOS)
        mos_in_series = mos_ori.mos_in_series(rdson)
        setattr(self,f"q_{BUCK_COMPONENT.ACTIVE_MOS}",mos_in_series)
        setattr(self,f"q_{BUCK_COMPONENT.PASSIVE_MOS}",mos_in_series)
        loss = self.p_total_on_mos(BUCK_COMPONENT.ACTIVE_MOS)+self.p_total_on_mos(BUCK_COMPONENT.PASSIVE_MOS)
        setattr(self,f"q_{BUCK_COMPONENT.ACTIVE_MOS}",mos_ori)
        setattr(self,f"q_{BUCK_COMPONENT.PASSIVE_MOS}",mos_ori)
        return loss
    
    def optimize_rdson(self,max_iter = 100):
        mos = self.get_component(BUCK_COMPONENT.ACTIVE_MOS)
        rdson_tmp = mos.rdson
        b,a = rdson_tmp/100,rdson_tmp*100
        phi = (1 + 5**0.5) / 2  # 黄金比例
        c = b - (b - a) / phi
        d = a + (b - a) / phi
        cnt_iter = 0
        while abs(b - a) > 1e-6:
            mos1_loss = self.calc_replace_mos(c)
            mos2_loss = self.calc_replace_mos(d)
            if mos1_loss < mos2_loss:
                b = d
            else:
                a = c
            c = b - (b - a) / phi
            d = a + (b - a) / phi
            cnt_iter+=1
            if(cnt_iter > max_iter):
                break
        return [(b + a) / 2,mos1_loss]
    
    @property
    def efficiency(self):
        return self.po/(self.po+self.p_total())

    @property
    def efficiency_with_optimize(self):
        rdson,loss_opt = self.optimize_rdson()
        return self.po/(self.po+loss_opt+self.p_ind())
    
    def print_loss(self):
        print(f"电感温度为{self.ind.temp}")
        print(f"平均电流为{self.ave_current_ind}")
        print(f"纹波为{self.inductor_ripple}")
        print(f"q1电流有效值为{self.rms_current(BUCK_COMPONENT.ACTIVE_MOS)}")
        print(f"q2电流有效值为{self.rms_current(BUCK_COMPONENT.PASSIVE_MOS)}")
        print(f"导通损耗为 Q1:{self.p_con(BUCK_COMPONENT.ACTIVE_MOS)},Q2:{self.p_con(BUCK_COMPONENT.PASSIVE_MOS)}")
        print(f"开通损耗为 Q1:{self.p_on(BUCK_COMPONENT.ACTIVE_MOS)},Q2:{self.p_on(BUCK_COMPONENT.PASSIVE_MOS)}")
        print(f"关断损耗为 Q1:{self.p_off(BUCK_COMPONENT.ACTIVE_MOS)},Q2:{self.p_off(BUCK_COMPONENT.PASSIVE_MOS)}")
        print(f"容性损耗为 Q1:{self.p_cap(BUCK_COMPONENT.ACTIVE_MOS)},Q2:{self.p_cap(BUCK_COMPONENT.PASSIVE_MOS)}")
        print(f"驱动损耗为 Q1:{self.p_dri(BUCK_COMPONENT.ACTIVE_MOS)},Q2:{self.p_dri(BUCK_COMPONENT.PASSIVE_MOS)}")
        print(f"Qrr损耗为  Q1:{self.p_qrr(BUCK_COMPONENT.ACTIVE_MOS)},Q2:{self.p_qrr(BUCK_COMPONENT.PASSIVE_MOS)}")
        print(f"电感损耗为 {self.p_ind()}")
        print(f"总损耗为{self.p_total()}")
        print(f"效率为{self.efficiency}")