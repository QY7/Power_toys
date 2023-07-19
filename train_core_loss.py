import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
import joblib
from power_toys.ml_model.fc_net import FC_Net
# 加载数据

_type = 'Bmax'
data = pd.read_csv(f"./power_toys/data/FEA data/arranged_data/arrange_{_type}.csv", header=None)
X = data.iloc[:, 1:4].values  # 输入值
y = data.iloc[:, 4].values  # 输出值
y = y.reshape(-1, 1)
# 数据标准化
X_scaler = StandardScaler().fit(X)
y_scaler = StandardScaler().fit(y)
X_scaled = X_scaler.transform(X)
y_scaled = y_scaler.transform(y)

# 实例化网络和优化器
net = FC_Net(input_size=3,output_size=1,hidden_size=500)
optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
criterion = nn.MSELoss()

# 训练网络
for epoch in range(5000):  # 训练次数可能需要调整
    inputs = torch.from_numpy(X_scaled).float()
    targets = torch.from_numpy(y_scaled).float()
    optimizer.zero_grad()
    outputs = net(inputs)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()
    if epoch % 500 == 0:  # 每500次打印一次损失值
        print('Epoch [%d/5000], Loss: %.4f' % (epoch, loss.item()))

torch.save(net.state_dict(), f'./power_toys/data/trained_model/transformer/{_type}.pth')
joblib.dump(X_scaler, f'./power_toys/data/scaler/transformer/{_type}_x_scaler.pkl')
joblib.dump(y_scaler, f'./power_toys/data/scaler/transformer/{_type}_y_scaler.pkl')