from power_toys.curve import Curve
import numpy as np
from power_toys.components.mosfet import MOSFET
from power_toys.curve import Curve
import matplotlib.pyplot as plt
from power_toys.topology.buck import BUCK
from power_toys.components.inductor import INDUCTOR

mos1 = MOSFET.load_from_lib(_id='BSZ0506NS')
mos2 = MOSFET.load_from_lib(_id='IQE008N03LM5')
ind = INDUCTOR(0.44e-6,10e-3)
b = BUCK(12,2,mos1,mos2,ind,500e3,0.1)

ro = np.linspace(0.1,1,100)
eff = []
for r in ro:
    b.ro = r
    eff.append(b.efficiency())
plt.plot(ro,eff)
plt.show()