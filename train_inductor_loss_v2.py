import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
import joblib
from power_toys.ml_model.fc_net import FC_Net

# 加载数据
file_list = os.listdir('./power_toys/data/combined_more_loss_for_training')
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f'Running on {device}')

# ind_id_list = ['XGL5030-223']
for idx,ind_id in enumerate(file_list):
    data = pd.read_csv(f"./power_toys/data/combined_more_loss_for_training/{ind_id}", header=None)
    # shuffle data
    data = data.sample(frac=1).reset_index(drop=True)

    X = data.iloc[:, 0:4].values  # 输入值
    y = data.iloc[:, 4:6].values  # 输出值

    # 数据标准化
    X_scaler = StandardScaler().fit(X)
    y_scaler = StandardScaler().fit(y)
    X_scaled = X_scaler.transform(X)
    y_scaled = y_scaler.transform(y)

    # 实例化网络和优化器
    net = FC_Net(input_size=4, hidden_size=2000, output_size=2).to(device)
    optimizer = torch.optim.Adam(net.parameters(), lr=0.0002)
    criterion = nn.MSELoss().to(device)

    # 训练网络
    for epoch in range(10000):  # 训练次数可能需要调整
        inputs = torch.from_numpy(X_scaled).float().to(device)
        targets = torch.from_numpy(y_scaled).float().to(device)
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        if epoch % 500 == 0:  # 每500次打印一次损失值
            print('Epoch [%d/20000], Loss: %.4f' % (epoch, loss.item()))
        if(loss.item()<0.0001):
            break

    torch.save(net.state_dict(), f'./power_toys/data/combined_more_trained_model/{ind_id[:-4]}.pth')
    joblib.dump(X_scaler, f'./power_toys/data/combined_more_trained_model/{ind_id[:-4]}_x_scaler.pkl')
    joblib.dump(y_scaler, f'./power_toys/data/combined_more_trained_model/{ind_id[:-4]}_y_scaler.pkl')
    print(f"{idx}/{len(file_list)} finished")
