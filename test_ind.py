from power_toys.components.inductor import Inductor
import matplotlib.pyplot as plt
ind_id = 'XGL6020-102'
ind = Inductor(ind_id)
freq,ac,dc,temp = ind.get_loss_by_frequency(5.36,5.36,0.2e6,2e6)
plt.plot(freq,dc+ac)
plt.grid()
plt.show()
# 测试