
import numpy as np
from power_toys.components.mosfet import MOSFET
from power_toys.topology.buck import BUCK
from power_toys.components.inductor import Inductor
import matplotlib.pyplot as plt

mos1 = MOSFET.load_from_lib(_id='BSC074N15NS5').parallel(2)
mos2 = MOSFET.load_from_lib(_id='BSC074N15NS5').parallel(4)
ind = Inductor('XGL1010-562')
b = BUCK(100,12,mos1,mos2,ind,100e3,12**2/750,1)

eff  = []
temp = []
fs = np.arange(50e3,150e3,20e3)

for f in fs:
    print(f)
    b.update_ind_loss()
    b.fs = f
    eff.append(b.efficiency_with_optimize)
    temp.append(b.ind.temp)
    print(f"DC loss is {b.ind.dc_loss} and AC loss is {b.ind.ac_loss}")

plt.plot(fs,eff)
plt.figure()
plt.plot(fs,temp)
plt.show()

