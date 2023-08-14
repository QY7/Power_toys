import sys
sys.path.insert(0,'.')

from power_toys.components.mosfet.base_mosfet import MOSFET
from power_toys.topology.dcx import DCX
from power_toys.common.const import DCX_COMPONENT
mos = MOSFET.load_from_lib('BSC030N08NS5')
b = DCX(48,12,4,1e6,mos,mos,50e-9,100,DCX.HALF_BRIDGE)

print(b.loss_by_name(b.mos_p,'con_loss'))
print(f"原边电流有效值为{b.irms(DCX_COMPONENT.PRIMARY_MOS)}")
print(f"副边电流有效值为{b.irms(DCX_COMPONENT.SECONDARY_MOS)}")
print(f"原边励磁电流为{b.ilm(DCX_COMPONENT.PRIMARY_MOS)}")
print(f"励磁电感为{b.lm}")
print(f"总损耗为{b.total_loss}")
print(f"效率为{b.efficiency}")
