from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from power_toys.waveform import poly2_func
x_data = [1,2,3]
y_data = [1,4,9]
# 目标函数定义
# 拟合数据
[propt,pcov]=curve_fit(poly2_func,x_data,y_data)

# 数据显示
fitting_data = [poly2_func(x,propt[0],propt[1],propt[2]) for x in x_data]
plt.plot(x_data,fitting_data)
plt.scatter(x_data,y_data)
plt.show()