import numpy as np
from power_toys.log import log_error
from operator import methodcaller
from power_toys.waveform import triangle_rms
from numpy import floor
from power_toys.components.inductor import Inductor

class BUCK():
    ACTIVE_MOS = 1
    PASSIVE_MOS = 2
    INDUCTOR = 3

    def __init__(self,vin = None,vo = None,q_active = None,q_passive = None,ind:Inductor = None,fs = None,ro = None,Ncell = 1) -> None:
        self.vin = vin
        self.vo = vo
        self.ind = ind
        self.fs = fs
        self.ro = ro
        self.Ncell = Ncell

        setattr(self,f"q_{BUCK.ACTIVE_MOS}",q_active)
        setattr(self,f"q_{BUCK.PASSIVE_MOS}",q_passive) 

    def get_component(self,q_index = ACTIVE_MOS):
        return getattr(self,f"q_{q_index}")
    
    @property
    def duty_eff(self):
        duty_tmp = self.duty*self.Ncell
        return duty_tmp - floor(duty_tmp)
    
    @property
    def volt_sec(self):
        v_step = self.vin/self.Ncell
        vo_eff = self.vo%v_step
        return (v_step - vo_eff)*self.duty_eff/(self.fs*self.Ncell)
    
    @property    
    def inductor_ripple(self):
        try:
            if(isinstance(self.ind,float)):
                return self.volt_sec/self.ind
            else:
                return self.volt_sec/self.ind.inductance
        except TypeError:
            log_error("参数不完整")
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
    
    def rms_current(self,q_index = ACTIVE_MOS):
        """计算电流有效值

        Args:
            q_index (int, optional): 
            - 0: 主动管
            - 1: 整流管
            - 2: 电感

        Returns:
            _type_: 电流有效值
        """
        if(q_index == BUCK.ACTIVE_MOS):
            return np.sqrt(self.duty)*triangle_rms(self.io,self.inductor_ripple)
            # return np.sqrt(self.duty*(np.power(self.io,2)+np.power(self.inductor_ripple,2)/12))
        elif(q_index == BUCK.PASSIVE_MOS):
            return np.sqrt(1-self.duty)*triangle_rms(self.io,self.inductor_ripple)
        else:
            return triangle_rms(self.io,self.inductor_ripple)
    
    def off_current(self,q_index = ACTIVE_MOS):
        if(q_index == BUCK.ACTIVE_MOS):
            return self.io+self.inductor_ripple/2
        else:
            return self.io-self.inductor_ripple/2

    def on_current(self,q_index = ACTIVE_MOS):
        if(q_index == BUCK.ACTIVE_MOS):
            return self.io-self.inductor_ripple/2
        else:
            return self.io+self.inductor_ripple/2
        
    def off_voltage(self,q_index = ACTIVE_MOS):
        return self.vin/self.Ncell

    def on_voltage(self,q_index = ACTIVE_MOS):
        return self.vin/self.Ncell

    def ave_current(self,q_index = INDUCTOR):
        if(q_index == BUCK.INDUCTOR):
            return self.vo/self.ro
        return 0
    
    @property
    def ave_current_ind(self):
        return self.ave_current(q_index=3)
    
    @property
    def io(self):
        return self.ave_current_ind
    
    def p_con(self,q_index = ACTIVE_MOS):
        mos = getattr(self,f"q_{q_index}")
        return mos.con_loss(self.rms_current(q_index=q_index))*self.Ncell
    
    def p_dri(self,q_index):
        mos = getattr(self,f"q_{q_index}")
        return mos.dri_loss(self.fs)*self.Ncell
    
    def p_on(self,q_index):
        # Q2为软开通
        mos = getattr(self,f"q_{q_index}")
        if(q_index == BUCK.PASSIVE_MOS):
            return 0
        else:
            return mos.switch_on_loss(
                self.fs,
                self.on_voltage(q_index),
                self.on_current(q_index)
            )*self.Ncell
    
    def p_off(self,q_index):
        # Q2为软关断
        mos = getattr(self,f"q_{q_index}")
        if(q_index == BUCK.PASSIVE_MOS):
            return 0
        else:
            return mos.switch_off_loss(
                self.fs,
                self.off_voltage(q_index),
                self.off_current(q_index)
            )*self.Ncell
    
    def p_qrr(self,q_index):
        # Q1没有反向恢复损耗
        mos = getattr(self,f"q_{q_index}")
        if(q_index ==  BUCK.ACTIVE_MOS):
            return 0
        else:
            return mos.qrr_loss(self.fs,self.vin/self.Ncell)*self.Ncell
        
    def p_cap(self,q_index):
        # Q2也有容性损耗，在Q1强制开通的时候，Q2会强制充电
        mos = getattr(self,f"q_{q_index}")
        return mos.cap_loss(self.fs,self.vin/self.Ncell)*self.Ncell
    
    def p_ind_dc(self):
        if(self.io+self.inductor_ripple/2 > self.ind.isat):
            return -1

        return self.ind.predict_AI(
            dc = self.io,
            ac = self.inductor_ripple,
            freq = self.fs*self.Ncell
        )[0]
    
    def p_ind_ac(self):
        if(self.io+self.inductor_ripple/2 > self.ind.isat):
            return -1
        print(self.io)
        print(self.inductor_ripple)
        print(self.fs)
        return self.ind.predict_AI(
            dc = self.io,
            ac = self.inductor_ripple,
            freq = self.fs*self.Ncell
        )[1]
    
    def temp_ind(self):
        if(self.io+self.inductor_ripple/2 > self.ind.isat):
            return -1
        return self.ind.predict_AI(
            dc = self.io,
            ac = self.inductor_ripple,
            freq = self.fs*self.Ncell
        )[2]
    
    def p_total(self):
        mos_idx_list = [BUCK.ACTIVE_MOS,BUCK.PASSIVE_MOS]
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
    
    def p_total_on_mos(self,q_index = ACTIVE_MOS):
        loss_list = ["p_con",'p_on',"p_off","p_dri","p_qrr","p_cap"]
        loss_total = 0
        for loss_name in loss_list:
            loss_total += methodcaller(loss_name,q_index)(self)
        return loss_total
    
    def calc_replace_mos(self,rdson):
        mos_ori = self.get_component(BUCK.ACTIVE_MOS)
        mos_in_series = mos_ori.mos_in_series(rdson)
        setattr(self,f"q_{BUCK.ACTIVE_MOS}",mos_in_series)
        setattr(self,f"q_{BUCK.PASSIVE_MOS}",mos_in_series)
        loss = self.p_total_on_mos(BUCK.ACTIVE_MOS)+self.p_total_on_mos(BUCK.PASSIVE_MOS)
        setattr(self,f"q_{BUCK.ACTIVE_MOS}",mos_ori)
        setattr(self,f"q_{BUCK.PASSIVE_MOS}",mos_ori)
        return loss
    
    def optimize_rdson(self,max_iter = 100):
        mos = self.get_component(BUCK.ACTIVE_MOS)
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
    
    def update_ind_loss(self):
        self.ind.update_loss(self.io,self.inductor_ripple,self.fs)
        
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
        print(f"q1电流有效值为{self.rms_current(BUCK.ACTIVE_MOS)}")
        print(f"q2电流有效值为{self.rms_current(BUCK.PASSIVE_MOS)}")
        print(f"导通损耗为 Q1:{self.p_con(BUCK.ACTIVE_MOS)},Q2:{self.p_con(BUCK.PASSIVE_MOS)}")
        print(f"开通损耗为 Q1:{self.p_on(BUCK.ACTIVE_MOS)},Q2:{self.p_on(BUCK.PASSIVE_MOS)}")
        print(f"关断损耗为 Q1:{self.p_off(BUCK.ACTIVE_MOS)},Q2:{self.p_off(BUCK.PASSIVE_MOS)}")
        print(f"容性损耗为 Q1:{self.p_cap(BUCK.ACTIVE_MOS)},Q2:{self.p_cap(BUCK.PASSIVE_MOS)}")
        print(f"驱动损耗为 Q1:{self.p_dri(BUCK.ACTIVE_MOS)},Q2:{self.p_dri(BUCK.PASSIVE_MOS)}")
        print(f"Qrr损耗为  Q1:{self.p_qrr(BUCK.ACTIVE_MOS)},Q2:{self.p_qrr(BUCK.PASSIVE_MOS)}")
        print(f"电感损耗为 {self.p_ind()}")
        print(f"总损耗为{self.p_total()}")
        print(f"效率为{self.efficiency}")