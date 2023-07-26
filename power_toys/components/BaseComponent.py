class BaseComponent():
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