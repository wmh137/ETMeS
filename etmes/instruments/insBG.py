from .ins import ins
from .insEnum import waitFlag
from typing import Union
class insBG():
    '''
    The superclass of instruments' background (send commands, store data).
    '''
    def __init__(self):
        if hasattr(self, "name"):
            pass
        else:
            self.name = ""
        self.flag = {} # override
        self.setpoint = {} # override
        self.now = {} # override
    def getNow(self): # override
        pass
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return True

class SMU(insBG):
    def __init__(self):
        super().__init__()
    def setSrc(src: float): # override
        pass

class TempController(insBG):
    def __init__(self):
        super().__init__()
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'T(K)': None}
        self.targetpoint = None # temperature
        self.error = None # override
    def setTemp(self, setpoint: float, rate: float): # override
        pass
    def setTempTarget(self, target: Union[float, None]):
        self.targetpoint = target
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        if self.targetpoint == None:
            targetTemp = self.setpoint['setpoint']
        else:
            targetTemp = self.targetpoint
        if self.now['T(K)'] != None:
            if flag == waitFlag.stable:
                return abs(self.now['T(K)'] - targetTemp) < self.error
            else:
                return flag * (targetTemp - self.now['T(K)']) < self.error
        else:
            return True

class MagnetController(insBG):
    def __init__(self):
        super().__init__()
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'H(Oe)': None}
        self.error = None # override
    def setField(self, field: float, rate: float): # override
        pass
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        if flag == waitFlag.stable:
            return abs(self.now['H(Oe)'] - self.setpoint['setpoint']) < self.error
        else:
            return (self.setpoint['setpoint'] - self.now['H(Oe)']) * flag < self.error
