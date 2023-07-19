from power_toys.components.mosfet import MOSFET

mos1 = MOSFET.load_from_lib('BSC061N08NS5')
print(mos1.FoM)

mos2 = MOSFET.load_from_lib('BSC074N15NS5')
print(mos2.FoM)