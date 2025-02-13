from .insEnum import insType, waitFlag
from typing import Union
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
    @abstractmethod
    def __data__(self):
        self.flag = {}
        self.setpoint = {}
        self.now = {}
    def __init__(self, address: str, name: str = None, type: insType = insType.other):
        self.address = address
        if name:
            self.name = name
        else:
            self.name = address
        self.type = type
        self.res = None # resource
        self.ONOFF = ["OFF", "ON"]
        self.log = ""
        self.__data__()
    # basic o/i
    def write(self, cmd: str): # (override necessary for non-visa instrument)
        if self.type == insType.visa:
            self.res.write(cmd)
        else:
            raise Exception(f"{self.__class__.__name__}.write() not defined!")
    def query(self, cmd: str) -> str: # override (necessary for non-visa instrument)
        if self.type == insType.visa:
            return self.res.query(cmd)
        else:
            raise Exception(f"{self.__class__.__name__}.query() not defined!")
    # ins open and close
    def open(self): # (override necessary for non-visa instrument)
        raise Exception(f"{self.__class__.__name__}.open() not defined!")
    def close(self): # (override necessary for non-visa instrument)
        raise Exception(f"{self.__class__.__name__}.close() not defined!")
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
        pass
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
    def now2record(self) -> str:
        return (len(self.now)-1)*","

class SMU(ins):
    # set
    @abstractmethod
    def setSrc(src: float): # override
        pass

class TempController(ins):
    @abstractmethod
    def __data__(self):
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'T(K)': None}
        self.targetpoint = None # temperature target
        self.error = None
    @abstractmethod
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
        if flag == waitFlag.stable:
            return abs(self.now['H(Oe)'] - self.setpoint['setpoint']) < self.error
        else:
            return (self.setpoint['setpoint'] - self.now['H(Oe)']) * flag < self.error
    # set
    @abstractmethod
    def setField(self, field: float, rate: float):
        pass
