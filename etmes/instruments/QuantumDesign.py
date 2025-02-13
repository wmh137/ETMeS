from .insEnum import *
from .ins import ins, TempController, MagnetController
import clr
from abc import abstractmethod

clr.AddReference("etmes/instruments/QDInstrument")

from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

class QDTempController(TempController):
    def __data__(self):
        super().__data__()
        self.error = 0.05
    def __init__(self, qd: ins):
        super().__init__("", qd.name + ".T")
        self.res = qd.res
    def setTemp(self, setpoint: float, rate: float, approach: QDInstrumentBase.TemperatureApproach = QDInstrumentBase.TemperatureApproach.FastSettle):
        self.res.SetTemperature(setpoint, rate, approach)
        self.setpoint['setpoint'] = [setpoint, approach]
        self.setpoint['rate'] = rate
    def getNow(self):
        self.now['T(K)'] = self.res.GetTemperature(0, QDInstrumentBase.TemperatureStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable):
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

class QDMagnetController(MagnetController):
    def __data__(self):
        super().__data__()
        self.error = 1
    def __init__(self, qd:ins):
        super().__init__("", qd.name + ".M")
        self.res = qd.res
    def setField(self, setpoint: float, rate: float, approach: QDInstrumentBase.FieldApproach = QDInstrumentBase.FieldApproach.Linear):
        self.res.SetField(setpoint, rate, approach, QDInstrumentBase.FieldMode.Persistent)
        self.setpoint['setpoint'] = [setpoint, approach]
        self.setpoint['rate'] = rate
    def getNow(self):
        self.now['H(Oe)'] = self.res.GetField(0, QDInstrumentBase.FieldStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        if flag == waitFlag.stable:
            return int(self.now['H(Oe)'][2]) in [1, 4]
        else:
            return (self.setpoint['setpoint'] - self.now['H(Oe)']) * flag < self.error

class QDRotator(ins):
    def __data__(self):
        super().__data__()
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'Pos(deg)' : None}
        self.error = 0.1
    def __init__(self, qd:ins):
        super().__init__("", qd.name + ".R")
        self.res = qd.res
    def setPosition(self, setpoint: float, rate: float, mode: QDInstrumentBase.PositionMode = QDInstrumentBase.PositionMode.MoveToPosition):
        self.res.SetPosition("Horizontal Rotator", setpoint, rate, mode)
        self.setpoint['setpoint'] = [setpoint]
        self.setpoint['rate'] = rate
    def getNow(self):
        self.now['Pos(deg)'] = self.res.GetPosition("Horizontal Rotator", 0, QDInstrumentBase.PositionStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        if flag == waitFlag.stable:
            return int(self.now['Pos(deg)'][2]) in [1]
        else:
            return (self.setpoint['setpoint'] - self.now['Pos(deg)']) * flag < self.error

class QDChamber(ins):
    def __data__(self):
        super().__data__()
        self.setpoint = {'setpoint' : None}
        self.now = {'Chamber' : None}
    def __init__(self, qd:ins):
        super().__init__("", qd.name + ".C")
        self.res = qd.res
    def setChamber(self, command: QDInstrumentBase.ChamberCommand):
        self.res.SetChamber(command)
        self.setpoint['setpoint'] = command
    def getNow(self):
        self.now['Chamber'] = self.res.GetChamber(QDInstrumentBase.ChamberStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return int(self.now['Chamber'][1]) in [1, 2, 3, 7, 8, 9]

class QuantumDesign(ins):
    def __data__(self):
        super().__data__()
        self.T = None
        self.M = None
        self.R = None
        self.C = None
        self.now = {}
    @abstractmethod
    def __init__(self, type: QDInstrumentBase.QDInstrumentType, address: str, name: str, port: int):
        super().__init__(address, name, insType.other)
        self.type = type
        self.port = port
    def open(self):
        self.res = QDInstrumentFactory.GetQDInstrument(self.type, True, self.address, self.port)
        self.T = QDTempController(self)
        self.M = QDMagnetController(self)
        self.R = QDRotator(self)
        self.C = QDChamber(self)
        self.getNow()
    def close(self):# in build
        pass
    def stop(self):
        pass
    # get & check
    def getNow(self):
        self.T.getNow()
        self.M.getNow()
        self.R.getNow()
        self.C.getNow()
        self.now = {**self.T.now, **self.M.now, **self.R.now, **self.C.now}
    def reach(self, flag: waitFlag = waitFlag.stable):
        return all([self.T.reach(flag), self.M.reach(flag), self.R.reach(flag), self.C.reach(flag)])
    # show & record
    def name2str(self) -> str:
        return f"{self.name:>40s}"
    def flag2str(self) -> str:
        s = ""
        if self.T.setpoint['rate'] is not None:
            s += f"{self.T.setpoint['rate']:>5.1f}K/min |"
        else:
            s += 12*" "
        if self.M.setpoint['rate'] is not None:
            s += f"{self.M.setpoint['rate']:>7.0f}Oe/s   |"
        else:
            s += 15*" "
        if self.R.setpoint['rate'] is not None:
            s += f"{self.R.setpoint['rate']:>5.1f}Dg/s    "
        else:
            s += 13*" "
        return s
    def setpoint2str(self) -> str:
        s = ""
        if self.T.setpoint['setpoint'] is not None:
            s += f"{self.T.setpoint['setpoint'][0]:>5.1f}K {self.T.setpoint['setpoint'][1].ToString():.4s}|"
        else:
            s += 12*" "
        if self.M.setpoint['setpoint'] is not None:
            s += f"{self.M.setpoint['setpoint'][0]:>+7.0f}Oe {self.M.setpoint['setpoint'][1].ToString():.4s}|"
        else:
            s += 15*" "
        if self.R.setpoint['setpoint'] is not None:
            s += f"{self.R.setpoint['setpoint'][0]:>5.1f}Dg      "
        else:
            s += 13*" "
        return s
    def now2str(self) -> str:
        s = ""
        if self.T.now['T(K)'] is not None:
            if self.T.now['T(K)'][1] >= 99.9:
                s += f"{self.T.now['T(K)'][1]:>5.1f}K"
            elif self.T.now['T(K)'][1] >= 9.99:
                s += f"{self.T.now['T(K)'][1]:>5.2f}K"
            elif self.T.now['T(K)'][1] >= 0.999:
                s += f"{self.T.now['T(K)'][1]:>5.3f}K"
            else:
                s += f"{self.T.now['T(K)'][1]*1000:>4.0f}mK"
            s += f" {self.res.TemperatureStatusString(self.T.now['T(K)'][2]):>.4s}|"
        else:
            s += 12*" "
        if self.M.now['H(Oe)'] is not None:
            s += f"{self.M.now['H(Oe)'][1]:>+7.0f}Oe {self.res.FieldStatusString(self.M.now['H(Oe)'][2]):>.4s}|"
        else:
            s += 15*" "
        if self.R.now['Pos(deg)'] is not None:
            s += f"{self.R.now['Pos(deg)'][1]:>5.1f}Dg|"
        else:
            s += 8*" "
        if self.C.now['Chamber'] is not None:
            s += f"{self.res.ChamberStatusString(self.C.now['Chamber'][1]):>.5s}"
        else:
            s += 5*" "
        return s
    def now2record(self) -> str:
        rstr = ""
        if self.T.now['T(K)'] is not None:
            rstr += f"{self.T.now['T(K)'][1]:>.5f}"
        rstr += ","
        if self.M.now['H(Oe)'] is not None:
            rstr += f"{self.M.now['H(Oe)'][1]:>.3f}"
        rstr += ","
        if self.R.now['Pos(deg)'] is not None:
            rstr += f"{self.R.now['Pos(deg)'][1]:>.3f}"
        rstr += ","
        if self.C.now['Chamber'] is not None:
            rstr += f"{self.res.ChamberStatusString(self.C.now['Chamber'][1])}"
        return rstr
    # set
    def setTemp(self, setpoint: float, rate: float, approach: QDInstrumentBase.TemperatureApproach = QDInstrumentBase.TemperatureApproach.FastSettle):
        self.T.setTemp(setpoint, rate, approach)
    def setField(self, setpoint: float, rate: float, approach: QDInstrumentBase.FieldApproach = QDInstrumentBase.FieldApproach.Linear):
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
