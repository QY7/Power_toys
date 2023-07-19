from power_toys.components.tranformer import Round_transformer
import numpy as np
import matplotlib.pyplot as plt

r = np.arange(1e-3,6e-3,1e-3)
w = np.arange(2e-3,10e-3,1e-3)

[R2,W2] = np.meshgrid(r,w)
trans = Round_transformer(r=R2,w=W2,k=3)
plt.contour(R2,W2,trans.footprint)
plt.show()