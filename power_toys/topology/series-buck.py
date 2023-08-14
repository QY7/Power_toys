import numpy as np
from power_toys.log import log_error
from operator import methodcaller
from power_toys.waveform import triangle_rms
from numpy import floor
from power_toys.components.inductor import Inductor
from ..components.mosfet.base_mosfet import MOSFET
from ..common.const import *
from ..components.Base import BaseComponent,BaseCircuit
import copy

class SeriesBuck(BaseCircuit):
    def __init__(self) -> None:
        super().__init__()
        