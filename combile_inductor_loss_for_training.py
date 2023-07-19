import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
import joblib
from power_toys.ml_model.fc_net import FC_Net
# 加载数据
file_list = os.listdir('./power_toys/data/coilcraft_loss_for_training_more_data')
ind_id_list  = [x[:-4] for x in file_list]

for idx,ind_id in enumerate(ind_id_list):
    inductance  = float(ind_id[-3:-1])*np.power(10,float(ind_id[-1]))*1e-9
    series = ind_id[:-4]
    data = np.loadtxt(f"./power_toys/data/coilcraft_loss_for_training_more_data/{ind_id}.txt",delimiter=',')
    data = data[data[:,5]<125]
    print(data[data[:,3]<0])
    data = np.hstack((np.ones((data.shape[0],1))*inductance,data[:,:]))
    with open(f'./power_toys/data/combined_more_loss_for_training/{series}.txt','a') as f:
        np.savetxt(f,data,delimiter=',')