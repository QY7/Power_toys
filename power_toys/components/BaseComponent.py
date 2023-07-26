class BaseComponent():
    """
    所有component的基类，具备通用的属性和方法，通过继承这个类来继承属性
    """
    def __init__(self) -> None:
        pass

    def assign_circuit(self,circuit):
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