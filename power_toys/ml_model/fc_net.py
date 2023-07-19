import torch
import torch.nn as nn
import joblib
import torch.nn.functional as F

# 定义网络结构
class FC_Net(nn.Module):
    def __init__(self,input_size = 3,output_size = 3,hidden_size = 50,model_path = '',scaler_x_path = '',scaler_y_path = ''):
        super(FC_Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        if(model_path):
            self.load_state_dict(torch.load(model_path))
            self.eval()
            if(scaler_x_path and scaler_y_path):
                self.X_scaler = joblib.load(scaler_x_path)
                self.y_scaler = joblib.load(scaler_y_path)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
    def predict(self,x):
        new_scaled =self.X_scaler.transform(x)
        inputs = torch.from_numpy(new_scaled).float()
        outputs = self.forward(inputs)
        xyz_out = self.y_scaler.inverse_transform(outputs.detach().numpy())
        return xyz_out