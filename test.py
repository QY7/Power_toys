from power_toys.curve import Curve
import numpy as np
from power_toys.mosfet import MOSFET

mos = MOSFET(id = 'BSC023').load_from_lib()
print(mos.vgs)