import numpy as np
import os
import json
import requests
from scipy.interpolate import griddata
import torch
import torch.nn as nn
import joblib
from ..Base import BaseComponent

class BaseInductor(BaseComponent):

    def __init__(self) -> None:
        super().__init__()
        self._inductance = 0
        
    @property
    def inductance(self):
        return self._inductance
    
    @inductance.setter
    def inductance(self,value):
        self._inductance = value
    
    @property
    def ripple(self):
        volt_sec = self.circuit_param('volt_sec')
        return volt_sec/self.inductance