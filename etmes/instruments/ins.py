from .insEnum import insType, waitFlag
from typing import Dict, Union, List, Any
from abc import ABC, abstractmethod



class ins(ABC):
    '''
    The superclass of all instruments classes().

    Attributes
    ----------
        address : str
            address of the instrument
        name : str
            name of the instrument
        type : insType
            type of the instrument
    '''
    flag: Dict[str, Any]
    setpoint: Dict[str, Any]
    now: Dict[str, Any]
    res: Any
    @abstractmethod
    def __data__(self):
        self.flag = {}
        self.setpoint = {}
        self.now = {}
    def __init__(self, address: str, name: str = "ins", type: insType = insType.other):
        self.address = address
        if name:
            self.name = name
        else:
            self.name = address
        self.type = type
        self.res = None
        self.ONOFF = ["OFF", "ON"]
        self.log = ""
        self.__data__()
    # basic o/i
    @abstractmethod
    def write(self, cmd: str):
        return
    @abstractmethod
    def query(self, cmd: str) -> str:
        return ""
    # ins close
    @abstractmethod
    def close(self):
        pass
    @abstractmethod
    def insInit(self):
        pass
    @abstractmethod
    def stop(self):
        pass
    # get & check
    @abstractmethod
    def getNow(self):
        pass
    @abstractmethod
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return True
    # show & record
    def name2str(self) -> str:
        return f"{self.name:>20s}"
    @abstractmethod
    def flag2str(self) -> str:
        return 20*" "
    @abstractmethod
    def setpoint2str(self) -> str:
        return 20*" "
    @abstractmethod
    def now2str(self) -> str:
        return 20*" "
    @abstractmethod
    def now2record(self) -> List[str]:
        return [""]*len(self.now)

class SMU(ins):
    # set
    @abstractmethod
    def setSrc(self, source: float): # override
        pass

class TempController(ins):
    targetpoint: Union[float, None]
    @abstractmethod
    def __data__(self):
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'T(K)': 0.0}
        self.targetpoint = None # temperature target
        self.error = 0.0
    @abstractmethod
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        flag = waitFlag(flag)
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
    # set
    @abstractmethod
    def setTemp(self, setpoint: float, rate: float):
        pass
    def setTempTarget(self, target: Union[float, None]):
        self.targetpoint = target

class MagnetController(ins):
    @abstractmethod
    def __data__(self):
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'H(Oe)': None}
        self.error = None
    @abstractmethod
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        if self.setpoint['setpoint'] == None or self.now['H(Oe)'] == None:
            return True
        flag = waitFlag(flag)
        if flag == waitFlag.stable:
            return abs(self.now['H(Oe)'] - self.setpoint['setpoint']) < self.error
        else:
            return (self.setpoint['setpoint'] - self.now['H(Oe)']) * flag < self.error
    # set
    @abstractmethod
    def setField(self, field: float, rate: float):
        pass
