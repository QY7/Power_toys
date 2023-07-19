from power_toys.components.mosfet import MOSFET
from power_toys.topology.buck import BUCK
from power_toys.components.inductor import Inductor

Po = 110
# 由于Buck输入是200V，如果输出也是200V，那么设计开关频率没有意义，这里以100V作为优化点
Vo = 45

Vin_Buck = 48
Vo_Buck = Vo
Io = Po/Vo

mos1 = MOSFET.load_from_lib("BSZ900N15NS3G").parallel(1)
mos2 = MOSFET.load_from_lib("BSZ900N15NS3G").parallel(1)

ind = Inductor(id='XGL6060-103')
print(ind)

buck = BUCK(vin=Vin_Buck,vo=Vo_Buck,Ncell = 2,q_active=mos1,q_passive=mos2,ind=ind,fs = 100e3,ro = 6)
print(buck.volt_sec)
print(buck.duty)
print(buck.duty_eff)
print(buck.inductor_ripple)

print(f"SR导通损耗为{buck.p_con(BUCK.PASSIVE_MOS)}")
print(f"Active导通损耗为{buck.p_con(BUCK.ACTIVE_MOS)}")
print(f"Qrr损耗为{buck.p_qrr(BUCK.ACTIVE_MOS)+buck.p_qrr(BUCK.PASSIVE_MOS)}")
print(f"On损耗为{buck.p_on(BUCK.ACTIVE_MOS)+buck.p_on(BUCK.PASSIVE_MOS)}")
print(f"Off损耗为{buck.p_off(BUCK.ACTIVE_MOS)+buck.p_off(BUCK.PASSIVE_MOS)}")
print(f"cap损耗为{buck.p_cap(BUCK.ACTIVE_MOS)+buck.p_cap(BUCK.PASSIVE_MOS)}")
print(f"Dri损耗为{buck.p_dri(BUCK.ACTIVE_MOS)+buck.p_dri(BUCK.PASSIVE_MOS)}")
print(f"总损耗为{buck.p_total()}")