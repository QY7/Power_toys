from power_toys.components.mosfet.base_mosfet import MOSFET
from power_toys.topology.buck import BUCK
from power_toys.components.inductor.coilcraft import Coilcraft
from power_toys.common.const import *

Po = 110
# 由于Buck输入是200V，如果输出也是200V，那么设计开关频率没有意义，这里以100V作为优化点
Vo = 12

Vin_Buck = 48
Vo_Buck = Vo
Io = Po/Vo

mos1 = MOSFET.load_from_lib("BSC030N08NS5").parallel(1)
mos2 = MOSFET.load_from_lib("BSC030N08NS5").parallel(1)

ind = Coilcraft(id='XGL6060-103')

buck = BUCK(vin=Vin_Buck,vo=Vo_Buck,Ncell = 2,q_active=mos1,q_passive=mos2,ind=ind,fs = 100e3,po = Po)
print(mos1)
print(buck.volt_sec())
print(buck.duty)
print(buck.duty_eff)
print(buck.iripple())

print(f"SR导通损耗为{buck.loss_by_name(buck.mos2,'con_loss')}")

print(f"Active导通损耗为{buck.loss_by_name(buck.mos1,'con_loss')}")
print(f"Qrr损耗为{buck.loss_by_name(buck.mos1,'qrr_loss')+buck.loss_by_name(buck.mos2,'qrr_loss')}")
print(f"On损耗为{buck.loss_by_name(buck.mos1,'switch_on_loss')+buck.loss_by_name(buck.mos2,'switch_on_loss')}")
print(f"Off损耗为{buck.loss_by_name(buck.mos1,'switch_off_loss')+buck.loss_by_name(buck.mos2,'switch_off_loss')}")
print(f"cap损耗为{buck.loss_by_name(buck.mos1,'cap_loss')+buck.loss_by_name(buck.mos2,'cap_loss')}")
print(f"Dri损耗为{buck.loss_by_name(buck.mos1,'dri_loss')+buck.loss_by_name(buck.mos2,'dri_loss')}")
print(f"主动管总损耗为{buck.loss_sum_on_component(buck.mos1)}")
print(f"总损耗为{buck.total_loss}")
print(f"效率为{buck.loss_on_component(buck.mos1)}")

buck_opt_freq = buck.optimize_eff_by_fs
print(f"优化频率后使用的频率为{buck_opt_freq.fs()/1000:.1f}kHz")

buck_opt_rdson = buck.optimize_eff_by_rdson
print(f"优化Rdson之后的效率为{buck_opt_rdson.efficiency}")
buck_opt_freq = buck_opt_rdson.optimize_eff_by_fs
print(f"进一步优化频率后使用的频率为{buck_opt_freq.fs()/1000:.1f}kHz")
print(f"进一步优化fs之后的效率为{buck_opt_freq.efficiency}")
print(buck_opt_freq.ind.ripple)
