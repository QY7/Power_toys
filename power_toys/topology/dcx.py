import numpy as np
from power_toys.log import log_error
from operator import methodcaller
from math import pi


class DCX():
    PRIMARY_MOS = 'p'
    SECONDARY_MOS = 's'
    HALF_BRIDGE = 'H'
    CENTER_TAPE = 'C'
    FULL_BRIDGE = 'F'

    def __init__(self,
                 vin = None,
                 vo = None,
                 n_t = None,
                 fs = None,
                 q_p = None,
                 q_s = None,
                 td = None,
                 po = None,
                 transformer = None,
                 topology_p = HALF_BRIDGE,
                 topology_s = CENTER_TAPE
        ) -> None:
        self.topology_p = topology_p
        self.topology_s = topology_s
        self.vin = vin
        self.vo = vo
        self.n_t = n_t
        self.fs = fs
        self.q_p = q_p
        self.q_s = q_s
        self.td = td
        self.po = po
        self.transformer = transformer

    @property
    def ts(self):
        return self._ts
    
    @ts.setter
    def ts(self,value):
        self._ts = value
        self._fs = 1/value

    @property
    def fs(self):
        return self._fs
    
    @fs.setter
    def fs(self,value):
        self._fs = value
        self._ts = 1/value

    @property
    def po(self):
        return self._po
    
    @po.setter
    def po(self,value):
        self._ro = np.power(self.vo,2)/value
        self._po = value

    @property
    def ro(self):
        return self._ro
    
    @ro.setter
    def ro(self,value):
        self._ro = value
        self._po = np.power(self.vo,2)/value

    def rms_current(self,q_index):
        Ts = self.ts
        td = self.td
        Po = self.po
        if(q_index == DCX.PRIMARY_MOS):
            topology = self.topology_p
            mos = self.q_p
            vs = self.vin
        else:
            topology = self.topology_s
            mos = self.q_s
            vs = self.vo
        
        if topology == 'F' or topology == 'H':
            ilm = 2*mos.cosst**vs/td
            if topology == 'F':
                Ipower_p = Po*pi*Ts/(2*vs*(Ts-2*td))
            else:
                Ipower_p = Po*pi*Ts/(vs*(Ts-2*td))
        else:
            ilm = 2*(mos.cosst)*2*vs/td
            Ipower_p = Po*pi*Ts/(2*vs*(Ts-2*td))
        
        if(q_index == DCX.PRIMARY_MOS or q_index == DCX.SECONDARY_MOS):
            # 如果是计算管子的rms，那么不需要加上死区时间的电流有效值
            rms = ((Ipower_p**2)/2 + (ilm**2)/3)*(Ts-2*td)/Ts
        else:
            # 如果是计算变压器的rms，那么需要加上死区时间的电流有效值
            rms = ((Ipower_p**2)/2 + (Ipower_p**2)/3)*(Ts-2*td)/Ts + Ipower_p**2*2*td/Ts
        return np.sqrt(rms)
    
    def p_dri(self,q_index):
        if(q_index == DCX.PRIMARY_MOS):
            topology = self.topology_p
        else:
            topology = self.topology_s
        mos = getattr(self,f"q_{q_index}")

        if(topology == DCX.FULL_BRIDGE):
            return mos.dri_loss(self.fs)*4
        else:
            return mos.dri_loss(self.fs)*2 
        
    def p_con(self,q_index):
        mos = getattr(self,f"q_{q_index}")
        if(q_index == DCX.PRIMARY_MOS):
            topology = self.topology_p
        else:
            topology = self.topology_s
        
        if(topology == DCX.FULL_BRIDGE):
            return mos.con_loss(self.rms_current(q_index))*2
        else:
            return mos.con_loss(self.rms_current(q_index))*1
        
    def ilm(self,q_index):
        if(q_index == DCX.PRIMARY_MOS):
            topology = self.topology_p
            mos = self.q_p
            vs = self.vin
        else:
            topology = self.topology_s
            mos = self.q_s
            vs = self.vo
        
        if topology == 'F' or topology == 'H':
            ilm = 2*mos.cosst*vs/self.td
        else:
            # 由于中抽的电压应力是两倍输出电压，所以需要充电到两倍vs
            ilm = 2*(mos.cosst)*2*vs/self.td
        return ilm
    
    @property
    def lm(self):
        # 副边电流折算到原边要除以匝比
        ilm_total = self.ilm(DCX.PRIMARY_MOS)+self.ilm(DCX.SECONDARY_MOS)/self.n_t
        return self.vo*(self.ts-2*self.td)/2/ilm_total
    
    def p_total(self):
        mos_idx_list = [DCX.PRIMARY_MOS,DCX.SECONDARY_MOS]
        loss_list = ["p_con","p_dri"]
        loss_total = 0
        for mos_idx in mos_idx_list:
            for loss_name in loss_list:
                loss_total += methodcaller(loss_name,mos_idx)(self)
        return loss_total
    
    def efficiency(self):
        return self.po/(self.po+self.p_total())