from power_toys.curve import Curve
import numpy as np
from power_toys.components.mosfet.base_mosfet import MOSFET
from power_toys.curve import Curve
import matplotlib.pyplot as plt
from power_toys.topology.buck import BUCK
from power_toys.components.inductor.coilcraft import Coilcraft

mos1 = MOSFET.load_from_lib(_id='BSZ0506NS')
mos2 = MOSFET.load_from_lib(_id='IQE008N03LM5')
ind = Coilcraft('XGL6060-153')
b = BUCK(48,12,mos1,mos2,ind,500e3,100)

# 扫描功率
# po = np.linspace(1,100,100)
# eff = []
# for p in po:
#     b.po = p
#     eff.append(b.efficiency)
# plt.plot(po,eff)
# plt.show()

# 扫描频率
eff = []
fs = np.linspace(10e3,500e3,100)
for f in fs:
    b.set_fs(f)
    eff.append(b.efficiency)
plt.plot(fs,eff)
plt.show()
