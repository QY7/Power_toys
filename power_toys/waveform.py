import numpy as np
from power_toys.curve import Curve
def power_func(x,k,a,b):
    """用于拟合的幂指数函数,y=k*x^a+b

    Args:
        x (float): x
        k (float): k
        a (float): a
        b (float): b

    Returns:
        float: y
    """
    return k*np.power(x,a)*x+b

def poly2_func(x,k,a,b):
    return k*np.power(x,2)+a*x+b

def poly3_func(x,k,a,b,c):
    return k*np.power(x,3)+a*np.power(x,2)+b*x+c

def gain_sin_ave2pk():
    return np.pi/2

def gain_sin_pk2ave():
    return 2/np.pi

def gain_sin_pk2rms():
    return 1/np.sqrt(2)

def gain_sin_ave2rms():
    return gain_sin_ave2pk()*gain_sin_pk2rms()

def gain_sin_rms2pk():
    return np.sqrt(2)

def gain_sin_rms2ave():
    return 1/gain_sin_ave2rms()

def triangle_rms(ave,ripple_pk2pk):
    return np.sqrt(np.power(ave,2)+np.power(ripple_pk2pk,2)/12)