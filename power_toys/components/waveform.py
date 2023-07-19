from scipy.signal import find_peaks, sawtooth
import numpy as np
import matplotlib.pyplot as plt

class Waveform():
    def __init__(self, arr):
        if not isinstance(arr, np.ndarray):
            raise TypeError("Input should be a numpy array")
        if len(arr.shape) != 2:
            raise ValueError("Input array should be 2-dimensional")
        if arr.shape[0] == 2:
            arr = arr.T  # Transpose the array if it's 2*n
        if arr.shape[1] != 2:
            raise ValueError("Input array should have exactly 2 columns")
        self.arr = arr

    @classmethod
    def load_np(cls, arr):
        return cls(arr)

    @classmethod
    def from_txt(cls, filepath):
        arr = np.loadtxt(filepath)
        return cls(arr)

    @property
    def rms(self):
        # Compute RMS value (second dimension is assumed to be the waveform values)
        return np.sqrt(np.mean(np.square(self.arr[:, 1])))

    @property
    def avg(self):
        # Compute average value using trapezoidal rule
        return np.trapz(self.arr[:, 1], self.arr[:, 0]) / (self.arr[-1, 0] - self.arr[0, 0])

    @property
    def peak(self):
        # Find peak value
        return np.max(np.abs(self.arr[:, 1]))

    @property
    def mean_abs(self):
        # Compute mean of absolute values
        return np.mean(np.abs(self.arr[:, 1]))

    @property
    def period(self):
        # Calculate the period of the waveform
        peaks, _ = find_peaks(self.arr[:, 1])
        if len(peaks) < 2:
            raise ValueError("Not enough peaks in waveform to calculate period")
        periods = np.diff(self.arr[peaks, 0])
        return np.mean(periods)

    @property
    def integral(self):
        # Compute integral of the waveform
        return np.trapz(self.arr[:, 1], self.arr[:, 0])
    
    def integral_range(self,xmax = 0,xmin = 0):
        x = self.arr[:,0]
        y = self.arr[:,1]
        if(xmax == xmin and xmin == 0):
            return self.integral
        else:
            idx_filter = (x<=xmax) & (x >= xmin)
            return np.trapz(y[idx_filter],x[idx_filter])
    
    def ydx(self,xmax,xmin=0):
        self.integral_range(xmax=xmax,xmin=xmin)
    
    def charge(self,vmax,vmin = 0):
        """根据电压和电容数组数值积分计算电荷

        Args:
            v (array): 电压数组
            c (array): 电容数组
            vmax (float): 积分的电压最大值
            vmin (float, optional): 积分的电压最小值. Defaults to 0.

        Returns:
            C: 电荷量
        """
        return self.ydx(vmax,vmin)
    
    def time_equivalent(self,vmax,vmin=0):
        """根据C-V曲线计算时间等效电容，根据C*deltaV计算等效电荷

        Args:
            vmax (float): 电压最大值
            vmin (float, optional): 电压最小值. Defaults to 0.

        Returns:
            float: 时间等效电容
        """
        return self.charge(vmax,vmin)/vmax
    
    def yxdx(self,xmax,xmin = 0):
        x = self.arr[:,0]
        y = self.arr[:,1]
        idx_filter = (x<=xmax) & (x >= xmin)
        return np.trapz((x*y)[idx_filter],x[idx_filter])

    def energy(self,vmax,vmin = 0):
        """根据C-V曲线计算等效，根据C*V*deltaV计算

        Args:
            v (list)): 电压数组
            c (list): 电容数组
            vmax (float): 电压最大值
            vmin (float, optional): 电压最小值. Defaults to 0.
        """
        return self.yxdx(vmax,vmin)
    
    def energy_equivalent(self,vmax,vmin=0):
        """根据C-V曲线计算能量等效电容，根据C*V*deltaV计算能量

        Args:
            v (list): 电压数组
            c (list): 电容数组
            vmax (float): 电压最大值
            vmin (float, optional): 电压最小值. Defaults to 0.

        Returns:
            float: 能量等效电容
        """
        return self.energy(vmax,vmin)/vmax**2*2
    
    def time_equivalent(self,vmax,vmin=0):
        """根据C-V曲线计算时间等效电容，根据C*deltaV计算等效电荷

        Args:
            vmax (float): 电压最大值
            vmin (float, optional): 电压最小值. Defaults to 0.

        Returns:
            float: 时间等效电容
        """
        return self.charge(vmax,vmin)/vmax
    
    def plot(self):
        plt.plot(self.arr[:,0],self.arr[:,1])
    
    @classmethod
    def gen_sine(cls,t,Ts,Am):
        if not isinstance(t, np.ndarray):
            raise TypeError("Input t should be a numpy array")
        if len(t.shape) != 1:
            raise ValueError("Input t should be 1-dimensional")
        return cls(np.array([t,np.sin(2*np.pi/Ts*t)*Am]))
    
    @classmethod
    def gen_triangle(cls, t, Am = 1, Ts = 1, duty = 0.5,biased = True):
        # Generate triangle wave
        waveform_values = Am * sawtooth(2 * np.pi * t / Ts, duty)
        if(biased):
            waveform_values += Am
        arr = np.column_stack((t, waveform_values))
        return cls(arr)
    
    @classmethod
    def gen_LLC_sine_wave_with_deadtime(cls, ILm_pk, td, Ts,A):
        Tr = Ts-2*td
        omega_r = 2*np.pi/Tr
        t = np.arange(0,Ts,Ts/1000)
        iLr = np.array([0]*1000,dtype=np.float64)
        iLm = np.array([0]*1000,dtype=np.float64)
        if(ILm_pk/A < 1):
            initial_phase = np.arcsin(-ILm_pk/A)
        else:
            initial_phase = np.arcsin(-1)
        # idx
        idx1 = t<(Ts/2-td)
        idx2 = (t>=(Ts/2-td))&(t<Ts/2)
        idx3 = (t>=Ts/2)&(t<(Ts-td))
        idx4 = (t>=(Ts-td))
        # time slice
        t1 = t[idx1]
        t2 = t[idx2]
        t3 = t[idx3]
        t4 = t[idx4]
        # iLm
        iLm[idx1] = 2*ILm_pk/(0.5*Ts-td)*t1-ILm_pk
        iLm[idx2] = ILm_pk
        iLm[idx3] = -2*ILm_pk/(0.5*Ts-td)*(t3-Ts/2)+ILm_pk
        iLm[idx4] = -ILm_pk
        # iLr
        iLr[idx1] = np.sin(omega_r*t1+initial_phase)*A
        iLr[idx2] = ILm_pk
        iLr[idx3] = np.sin(omega_r*(t3-Ts/2)+initial_phase+np.pi)*A
        iLr[idx4] = -ILm_pk
        # isec
        isec = iLr-iLm
        # arr
        arr1 = np.column_stack((t, iLr))
        arr2 = np.column_stack((t, iLm))
        arr3 = np.column_stack((t, isec))
        # result
        return [cls(arr1),cls(arr2),cls(arr3)]
    
    @classmethod
    def gen_LLC_sine_wave_with_deadtime_by_isec_ave(cls,isec_ave, ILm_pk, td, Ts, tol=1e-3, max_iter=100):
        # Initialize A
        A = isec_ave/10
        A_end = isec_ave*10
        A_start = 0

        # Perform the iteration
        for _ in range(max_iter):
            # Generate waveform and calculate isec average
            _,_, isec_avg = cls.gen_LLC_sine_wave_with_deadtime(ILm_pk, td, Ts, A)

            # Check if the isec average is close to 1
            if abs(isec_avg.mean_abs - 1) < tol:
                break

            # Update A
            if isec_avg.mean_abs > 1:
                A_end = A
                A = (A_start + A_end) / 2
            else:
                A_start = A
                A = (A_start + A_end) / 2

        return cls.gen_LLC_sine_wave_with_deadtime(ILm_pk, td, Ts, A)