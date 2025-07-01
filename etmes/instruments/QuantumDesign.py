from .insEnum import *
from .ins import ins, TempController, MagnetController
from .insio import insioNone
import clr, time
from abc import abstractmethod
from typing import List

clr.AddReference("etmes/instruments/QDInstrument")

from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

class QDTempApproach(eEnum):
    FastSettle = QDInstrumentBase.TemperatureApproach.FastSettle
    NoOvershoot = QDInstrumentBase.TemperatureApproach.NoOvershoot

class QDFieldApproach(eEnum):
    Linear = QDInstrumentBase.FieldApproach.Linear
    NoOvershoot = QDInstrumentBase.FieldApproach.NoOvershoot
    Oscillate = QDInstrumentBase.FieldApproach.Oscillate

class vIns(insioNone):
    def insInit(self):
        pass

class QDTempController(vIns, TempController):
    def __data__(self):
        super().__data__()
        self.error = 0.05
    def __init__(self, qd: ins):
        super().__init__("", qd.name + ".T")
        self.res = qd.res
    def stop(self):
        pass
    # get & check
    def getNow(self):
        self.now['T(K)'] = self.res.GetTemperature(0, QDInstrumentBase.TemperatureStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable):
        flag = waitFlag(flag)
        if self.targetpoint == None:
            targetTemp = self.setpoint['setpoint']
        else:
            targetTemp = self.targetpoint
        if self.now['T(K)'] != None:
            if flag == waitFlag.stable:
                return int(self.now['T(K)'][2]) in [1]
            else:
                return flag * (targetTemp - self.now['T(K)']) < self.error
        else:
            return True
    # show & record
    def flag2str(self) -> str:
        if self.setpoint['rate'] is not None:
            return f"{self.setpoint['rate']:>5.1f}K/min "
        else:
            return 11*" "
    def setpoint2str(self) -> str:
        if self.setpoint['setpoint'] is not None:
            return f"{self.setpoint['setpoint'][0]:>5.1f}K {self.setpoint['setpoint'][1].value.ToString():.4s}"
        else:
            return 11*" "
    def now2str(self) -> str:
        if self.now['T(K)'] is not None:
            if self.now['T(K)'][1] >= 99.9:
                s = f"{self.now['T(K)'][1]:>5.1f}K"
            elif self.now['T(K)'][1] >= 9.99:
                s = f"{self.now['T(K)'][1]:>5.2f}K"
            elif self.now['T(K)'][1] >= 0.999:
                s = f"{self.now['T(K)'][1]:>5.3f}K"
            else:
                s = f"{self.now['T(K)'][1]*1000:>4.0f}mK"
            return s + f" {self.res.TemperatureStatusString(self.now['T(K)'][2]):>.4s}"
        else:
            return 11*" "
    def now2record(self) -> List[str]:
        return []
    # set
    def setTemp(self, setpoint: float, rate: float, approach: QDTempApproach = QDTempApproach.FastSettle):
        approach = QDTempApproach(approach)
        self.res.SetTemperature(setpoint, rate, approach.value)
        self.setpoint['setpoint'] = [setpoint, approach]
        self.setpoint['rate'] = rate

class QDMagnetController(vIns, MagnetController):
    def __data__(self):
        super().__data__()
        self.error = 1
    def __init__(self, qd:ins):
        super().__init__("", qd.name + ".M")
        self.res = qd.res
    def stop(self):
        pass
    # get & check
    def getNow(self):
        self.now['H(Oe)'] = self.res.GetField(0, QDInstrumentBase.FieldStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        flag = waitFlag(flag)
        if flag == waitFlag.stable:
            return int(self.now['H(Oe)'][2]) in [1, 4]
        else:
            return (self.setpoint['setpoint'] - self.now['H(Oe)']) * flag < self.error
    # show & record
    def flag2str(self) -> str:
        if self.setpoint['rate'] is not None:
            return f"{self.setpoint['rate']:>7.0f}Oe/s   "
        else:
            return 14*" "
    def setpoint2str(self) -> str:
        if self.setpoint['setpoint'] is not None:
            return f"{self.setpoint['setpoint'][0]:>+7.0f}Oe {self.setpoint['setpoint'][1].value.ToString():.4s}"
        else:
            return 14*" "
    def now2str(self) -> str:
        if self.now['H(Oe)'] is not None:
            return f"{self.now['H(Oe)'][1]:>+7.0f}Oe {self.res.FieldStatusString(self.now['H(Oe)'][2]):>.4s}"
        else:
            return 14*" "
    def now2record(self) -> List[str]:
        return []
    # set
    def setField(self, setpoint: float, rate: float, approach: QDFieldApproach = QDFieldApproach.Linear):
        approach = QDFieldApproach(approach)
        self.res.SetField(setpoint, rate, approach.value, QDInstrumentBase.FieldMode.Persistent)
        self.setpoint['setpoint'] = [setpoint, approach]
        self.setpoint['rate'] = rate

class QDRotator(vIns, ins):
    def __data__(self):
        super().__data__()
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'Pos(deg)' : None}
        self.error = 0.1
    def __init__(self, qd:ins):
        super().__init__("", qd.name + ".R")
        self.res = qd.res
    def stop(self):
        pass
    # get & check
    def getNow(self):
        self.now['Pos(deg)'] = self.res.GetPosition("Horizontal Rotator", 0, QDInstrumentBase.PositionStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        flag = waitFlag(flag)
        if flag == waitFlag.stable:
            return int(self.now['Pos(deg)'][2]) in [1]
        else:
            return (self.setpoint['setpoint'] - self.now['Pos(deg)']) * flag < self.error
    # show & record
    def flag2str(self) -> str:
        if self.setpoint['rate'] is not None:
            return f"{self.setpoint['rate']:>5.1f}Dg/s    "
        else:
            return 13*" "
    def setpoint2str(self) -> str:
        if self.setpoint['setpoint'] is not None:
            return f"{self.setpoint['setpoint'][0]:>5.1f}Dg      "
        else:
            return 13*" "
    def now2str(self) -> str:
        if self.now['Pos(deg)'] is not None:
            return f"{self.now['Pos(deg)'][1]:>5.1f}Dg"
        else:
            return 7*" "
    def now2record(self) -> List[str]:
        return []
    # set
    def setPosition(self, setpoint: float, rate: float, mode: QDInstrumentBase.PositionMode = QDInstrumentBase.PositionMode.MoveToPosition):
        self.res.SetPosition("Horizontal Rotator", setpoint, rate, mode)
        self.setpoint['setpoint'] = [setpoint]
        self.setpoint['rate'] = rate

class QDChamber(vIns, ins):
    def __data__(self):
        super().__data__()
        self.setpoint = {'setpoint' : None}
        self.now = {'Chamber' : None}
    def __init__(self, qd:ins):
        super().__init__("", qd.name + ".C")
        self.res = qd.res
    def stop(self):
        pass
    # get & check
    def getNow(self):
        self.now['Chamber'] = self.res.GetChamber(QDInstrumentBase.ChamberStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return int(self.now['Chamber'][1]) in [1, 2, 3, 7, 8, 9]
    # show & record
    def flag2str(self) -> str:
        return ""
    def setpoint2str(self) -> str:
        return ""
    def now2str(self) -> str:
        if self.now['Chamber'] is not None:
            return f"{self.res.ChamberStatusString(self.now['Chamber'][1]):>.5s}"
        else:
            return 5*" "
    def now2record(self) -> List[str]:
        return []
    # set
    def setChamber(self, command: QDInstrumentBase.ChamberCommand):
        self.res.SetChamber(command)
        self.setpoint['setpoint'] = command

class QuantumDesign(insioNone, ins):
    T: QDTempController
    M: QDMagnetController
    R: QDRotator
    C: QDChamber
    def __data__(self):
        super().__data__()
        '''
        self.T = None
        self.M = None
        self.R = None
        self.C = None
        '''
        self.now = {}
        self.__lastgetNowTime = 0.0
    @abstractmethod
    def __init__(self, type: QDInstrumentBase.QDInstrumentType, address: str, name: str, port: int):
        super().__init__(address, name, insType.other)
        self.type = type
        self.port = port
    def insInit(self):
        self.res = QDInstrumentFactory.GetQDInstrument(self.type, True, self.address, self.port)
        self.T = QDTempController(self)
        self.M = QDMagnetController(self)
        self.R = QDRotator(self)
        self.C = QDChamber(self)
        self.getNow()
    def close(self):
        pass
    def stop(self):
        pass
    # get & check
    def getNow(self):
        if time.time() - self.__lastgetNowTime < 0.4:
            return
        self.__lastgetNowTime = time.time()
        self.T.getNow()
        self.M.getNow()
        try:
            self.R.getNow()
        except:
            self.R.now['Pos(deg)'] = [0,0.,1]
        self.C.getNow()
        self.now = {**self.T.now, **self.M.now, **self.R.now, **self.C.now}
    def reach(self, flag: waitFlag = waitFlag.stable):
        return all([self.T.reach(flag), self.M.reach(flag), self.R.reach(flag), self.C.reach(flag)])
    # show & record
    def name2str(self) -> str:
        return f"{self.name:>40s}"
    def flag2str(self) -> str:
        s = "|".join([self.T.flag2str(), self.M.flag2str(), self.R.flag2str()])
        return s
    def setpoint2str(self) -> str:
        s = "|".join([self.T.setpoint2str(), self.M.setpoint2str(), self.R.setpoint2str()])
        return s
    def now2str(self) -> str:
        s = "|".join([self.T.now2str(), self.M.now2str(), self.R.now2str(), self.C.now2str()])
        return s
    def now2record(self) -> List[str]:
        r = []
        if self.T.now['T(K)'] is not None:
            r.append(f"{self.T.now['T(K)'][1]:>.5f}")
        if self.M.now['H(Oe)'] is not None:
            r.append(f"{self.M.now['H(Oe)'][1]:>.3f}")
        if self.R.now['Pos(deg)'] is not None:
            r.append(f"{self.R.now['Pos(deg)'][1]:>.3f}")
        if self.C.now['Chamber'] is not None:
            r.append(f"{self.res.ChamberStatusString(self.C.now['Chamber'][1])}")
        return r
    # set
    def setTemp(self, setpoint: float, rate: float, approach: QDTempApproach = QDTempApproach.FastSettle):
        self.T.setTemp(setpoint, rate, approach)
    def setField(self, setpoint: float, rate: float, approach: QDFieldApproach = QDFieldApproach.Linear):
        self.M.setField(setpoint, rate, approach)
    def setPosition(self, setpoint: float, rate: float, mode: QDInstrumentBase.PositionMode = QDInstrumentBase.PositionMode.MoveToPosition):
        self.R.setPosition(setpoint, rate, mode)
    def setChamber(self, command: QDInstrumentBase.ChamberCommand):
        self.C.setChamber(command)
class QuantumDesignPPMS(QuantumDesign):
    def __init__(self, address: str, name: str  = "QD PPMS", port: int = 11000):
        super().__init__(QDInstrumentBase.QDInstrumentType.PPMS, address, name, port)
class QuantumDesignVersaLab(QuantumDesign):
    def __init__(self, address: str, name: str  = "QD VersaLab", port: int = 11000):
        super().__init__(QDInstrumentBase.QDInstrumentType.VersaLab, address, name, port)
class QuantumDesignDynaCool(QuantumDesign):
    def __init__(self, address: str, name: str  = "QD DynaCool", port: int = 11000):
        super().__init__(QDInstrumentBase.QDInstrumentType.DynaCool, address, name, port)
class QuantumDesignSVSM(QuantumDesign):
    def __init__(self, address: str, name: str  = "QD SVSM", port: int = 11000):
        super().__init__(QDInstrumentBase.QDInstrumentType.SVSM, address, name, port)
