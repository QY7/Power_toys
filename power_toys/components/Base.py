import numpy as np

class BaseComponent():
    """
    所有component的基类，具备通用的属性和方法，通过继承这个类来继承属性
    """

    def __init__(self) -> None:
        self.circuit_idx = -1
        self.quantity = 0

    def register_circuit(self,circuit):
        self.circuit = circuit
    
    def circuit_param(self,param_name):
        if(hasattr(self,'circuit')):
            return self.circuit.param(component = self,param_name = param_name)
        
    @property
    def circuit_idx(self):
        return self._circuit_idx

    @circuit_idx.setter
    def circuit_idx(self,val):
        self._circuit_idx = val
    
    @property
    def area(self):
        return self.width*self.length
    
    @property
    def volume(self):
        return self.area*self.height

    @property
    def total_loss(self):
        loss_list = self.loss_list
        loss_sum = 0
        for loss_name in loss_list:
            loss_sum += getattr(self,loss_name)
        return loss_sum

class BaseCircuit():
    def __init__(self) -> None:
        self.component_list = []
        # 元件数量，比如全桥电路中4个管子是相同的，就用4来记录有4个一样的管子
        self.po = 0
        pass

    def get_component(self,c_index) -> BaseComponent:
        """c_index是circuit中元件的标识

        Args:
            c_index (int): 元件标识

        Returns:
            _type_: _description_
        """
        return getattr(self,f"c_{c_index}")
        
    def register_component(self,component:BaseComponent,c_index,quantity = 1):
        component.register_circuit(self)
        component.circuit_idx = c_index
        setattr(self,f"c_{c_index}",component)

        for i,comp in enumerate(self.component_list):
            if(comp.circuit_idx == c_index):
                self.component_list.pop(i)

        component.quantity = quantity
        self.component_list.append(component)
    
    def param(self,component:BaseComponent,param_name):
        func = getattr(self, param_name, None)
        if func is not None and callable(func):
            return func(c_index=component.circuit_idx)
        else:
            raise ValueError(f"No such method: {param_name}")
    
    def fs(self,c_index):
        return self._fs
        
    def set_fs(self,val):
        self._fs = val

    def loss_sum_on_component(self,comp:BaseComponent):
        """获取电路中元件的损耗

        Args:
            c_index (int): 元件序号
        """
        loss_info = self.loss_on_component(comp)
        return loss_info['quantity']*sum(loss_info['loss_breakdown'].values())

    def loss_by_name(self,comp:BaseComponent,loss_name = ''):
        """获取电路中元件的损耗

        Args:
            c_index (int or list of int, optional): 如果只需要计算一个元件，填元件的序号，如果计算多个元件，填元件的数组
            loss_name (str, '损耗的名字'): 损耗名称

        Returns:
            _type_: _description_
        """

        if(loss_name in comp.loss_list):
            return getattr(comp,loss_name)*comp.quantity
        else:
            print("invalid loss name")
            return 0
    
    def loss_on_component(self,comp:BaseComponent):
        result = {
            'quantity':comp.quantity,
            'loss_breakdown':{}
        }

        for loss_name in comp.loss_list:
            # 获取元件数量
            result['loss_breakdown'][loss_name] = getattr(comp,loss_name)
        return result
            
    
    @property
    def total_loss(self):
        """
        获取所有元件的损耗，需要注意的是component_list中每个item的第一个元素是component，第二个是quantity
        """
        loss_sum = 0
        for comp in self.component_list:
            # 遍历所有元件
            loss_list = comp.loss_list
            for loss_name in loss_list:
                # 遍历所有损耗类型
                loss_sum += getattr(comp,loss_name)*comp.quantity
        return loss_sum
    
    @property
    def efficiency(self):
        return self.po/(self.po+self.total_loss)
    
    @property
    def ro(self):
        return np.power(self.vo,2)/self.po