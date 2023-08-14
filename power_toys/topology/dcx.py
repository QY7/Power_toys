import numpy as np
from power_toys.log import log_error
from operator import methodcaller
from math import pi
from ..components.Base import BaseCircuit
from ..common.const import DCX_COMPONENT,TWO_TER_TRANSFORMER

class DCX(BaseCircuit):
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

        super().__init__()
        self.topology_p = topology_p
        self.topology_s = topology_s
        self.vin = vin
        self.vo = vo
        self.n_t = n_t
        self.set_fs(fs)
        self.td = td
        self.po = po

        if(topology_p == DCX.HALF_BRIDGE or topology_p == DCX.CENTER_TAPE):
            # 半桥或者是中抽，管子数量为2
            self.register_component(q_p,DCX_COMPONENT.PRIMARY_MOS,2)
        elif(topology_p == DCX.FULL_BRIDGE):
            # 全桥管子数量为4
            self.register_component(q_p,DCX_COMPONENT.PRIMARY_MOS,4)

        if(topology_s == DCX.HALF_BRIDGE or topology_s == DCX.CENTER_TAPE):
            # 半桥或者是中抽，管子数量为2
            self.register_component(q_s,DCX_COMPONENT.SECONDARY_MOS,2)
        elif(topology_s == DCX.FULL_BRIDGE):
            # 全桥管子数量为4
            self.register_component(q_s,DCX_COMPONENT.SECONDARY_MOS,4)

        self.transformer = transformer

    @property
    def mos_p(self):
        return self.get_component(DCX_COMPONENT.PRIMARY_MOS)
    
    @property
    def mos_s(self):
        return self.get_component(DCX_COMPONENT.SECONDARY_MOS)
    
    def irms(self,c_index,subcomponent_idx=None):
        """返回元件的电流

        Args:
            c_index (int): 元件的index
            subcomponent_idx (int, optional): 元件的子index，比如变压器的rms电流就可能有原边和副边的不同电流. Defaults to None.

        Returns:
            float: rms电流大小
        """
        Ts = self.ts
        td = self.td
        Po = self.po

        if( c_index == DCX_COMPONENT.PRIMARY_MOS \
            or (c_index == DCX_COMPONENT.TRANSFORMER \
            and subcomponent_idx == TWO_TER_TRANSFORMER.PRIMARY_WINDING)):
            topology = self.topology_p
            mos = self.get_component(DCX_COMPONENT.PRIMARY_MOS)
            vs = self.vin
        elif(c_index == DCX_COMPONENT.SECONDARY_MOS \
            or (c_index == DCX_COMPONENT.TRANSFORMER \
            and subcomponent_idx == TWO_TER_TRANSFORMER.SECONDARY_WINDING)):
            topology = self.topology_s
            mos = self.get_component(DCX_COMPONENT.SECONDARY_MOS)
            vs = self.vo
        else:
            print("invalid c_index for dcx")
                
        if topology == 'F' or topology == 'H':
            ilm = 2*mos.cosst**vs/td
            if topology == 'F':
                Ipower = Po*pi*Ts/(2*vs*(Ts-2*td))
            else:
                Ipower = Po*pi*Ts/(vs*(Ts-2*td))
        else:
            ilm = 2*(mos.cosst)*2*vs/td
            Ipower = Po*pi*Ts/(2*vs*(Ts-2*td))
        
        if(c_index == DCX_COMPONENT.PRIMARY_MOS or c_index == DCX_COMPONENT.SECONDARY_MOS):
            # 如果是计算管子的rms，那么不需要加上死区时间的电流有效值
            rms = ((Ipower**2)/2 + (ilm**2)/3)*(Ts-2*td)/Ts
            return np.sqrt(rms/2)
        else:
            # 如果是计算变压器的rms，那么需要加上死区时间的电流有效值
            rms = ((Ipower**2)/2 + (Ipower**2)/3)*(Ts-2*td)/Ts + Ipower**2*2*td/Ts
            return np.sqrt(rms)
    
    def off_current(self,c_index):
        if(c_index == DCX_COMPONENT.PRIMARY_MOS):
            return self.ilm
        else:
            return 0

    def on_current(self,c_index):
        return 0
    
    def off_voltage(self,c_index):
        return 0

    def on_voltage(self,c_index):
        return 0

    def cap_voltage(self,c_index):
        return 0
    
    def qrr_voltage(self,c_index):
        return 0
        
    @property
    def ts(self):
        return 1/self._fs

    def fs(self,c_index):
        return self._fs
        
    def ilm(self,c_index):
        if(c_index == DCX.PRIMARY_MOS):
            topology = self.topology_p
            mos = self.mos_p
            vs = self.vin
        else:
            topology = self.topology_s
            mos = self.mos_s
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