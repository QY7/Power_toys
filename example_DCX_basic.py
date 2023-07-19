from power_toys.curve import Curve
import numpy as np
from power_toys.components.mosfet import MOSFET
from power_toys.topology.dcx import DCX

mos = MOSFET.load_from_lib()
b = DCX(48,12,4,1e6,mos,mos,50e-9,100,DCX.HALF_BRIDGE)

print(b.p_con(DCX.PRIMARY_MOS))
print(f"原边电流有效值为{b.rms_current(DCX.PRIMARY_MOS)}")
print(f"副边电流有效值为{b.rms_current(DCX.SECONDARY_MOS)}")
print(f"原边励磁电流为{b.ilm(DCX.PRIMARY_MOS)}")
print(f"励磁电感为{b.lm}")
print(f"导通损耗为{b.p_total()}")
print(f"总损耗为{b.p_total()}")
print(f"效率为{b.efficiency()}")
