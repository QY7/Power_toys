from math import pi,sqrt
import numpy as np
import matplotlib.pyplot as plt
import control

class Filter():
    def __init__(self):
        self.poles = []
        self.zeros = []
        self.k = 1

    def set_type2PID(self,R1,C1,Cp):
        self.poles.append(0)
        self.poles.append(1/(2*pi*(R1*(C1+Cp))))
        self.zeros.append(1/(2*pi*R1*C1))
    
    def plot_bode(self, freq_start=1, freq_end=10000):
        # 使用 zeros 和 poles 创建系统传递函数
        num = np.poly(self.zeros)*self.k
        den = np.poly(self.poles)
        system = control.TransferFunction(num,den)

        # 生成对数等间距的频率数组
        w = np.logspace(np.log10(freq_start), np.log10(freq_end), num=500)

        # 计算在这个频率范围内的波特图
        mag, phase, freq = control.bode_plot(system, w, dB=True, deg=True)
        plt.grid(which='both')
        plt.ylim([-95,-85])
        plt.show()

    def series_RC(self,R,C):
        self.poles.append(0)
        self.poles.append(1/(R*C))
        self.k = R

if __name__ == '__main__':
    filter = Filter()
    filter.series_RC(R=100e3,C=10e-12)
    filter.plot_bode(0.1e3,5e6)