from .ins import ins
from .insBG import insBG, TempController, MagnetController
from .insEnum import insType, waitFlag
import clr

clr.AddReference("etmes/instruments/QDInstrument")

from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

class QDTempController(TempController):
    def __init__(self, qd: ins):
        super().__init__()
        self.name = qd.name + ".T"
        self.res = qd.res
        self.error = 0.05
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
    def __init__(self, qd:ins):
        super().__init__()
        self.name = qd.name + ".M"
        self.res = qd.res
        self.error = 1
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

class QDRotator(insBG):
    def __init__(self, qd:ins):
        super().__init__()
        self.name = qd.name + ".R"
        self.res = qd.res
        self.setpoint = {'setpoint': None, 'rate': None}
        self.now = {'Pos(deg)' : None}
        self.error = 0.1
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

class QDChamber(insBG):
    def __init__(self, qd:ins):
        super().__init__()
        self.name = qd.name + ".C"
        self.res = qd.res
        self.setpoint = {'setpoint' : None}
        self.now = {'Chamber' : None}
    def setChamber(self, command: QDInstrumentBase.ChamberCommand):
        self.res.SetChamber(command)
        self.setpoint['setpoint'] = command
    def getNow(self):
        self.now['Chamber'] = self.res.GetChamber(QDInstrumentBase.ChamberStatus(0))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return int(self.now['Chamber'][1]) in [1, 2, 3, 7, 8, 9]

class QuantumDesign(ins, insBG):
    def __init__(self, type: QDInstrumentBase.QDInstrumentType, address: str, port: int, name: str):
        super().__init__(address, name, insType.other)
        self.type = type
        self.port = port
        self.T = None
        self.M = None
        self.R = None
        self.C = None
    # ins method
    def open(self):
        self.res = QDInstrumentFactory.GetQDInstrument(self.type, True, self.address, self.port)
        self.T = QDTempController(self)
        self.M = QDMagnetController(self)
        self.R = QDRotator(self)
        self.C = QDChamber(self)
        self.getNow()
    def close(self):# in build
        pass
    def name2str(self) -> str:
        return f"{self.name:>40s}"
    def flag2str(self) -> str:
        s = ""
        if self.T.setpoint['rate'] is not None:
            s += f"{self.flag['rate']:>5.1f}K/min |"
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
            if self.T.now['T(K)'][1] >= 100:
                s += f"{self.T.now['T(K)'][1]:>5.1f}K"
            elif self.T.now['T(K)'][1] >= 10:
                s += f"{self.T.now['T(K)'][1]:>5.2f}K"
            elif self.T.now['T(K)'][1] >= 1:
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
        return f"{self.T.now['T(K)'][1]:>.5f},{self.M.now['H(Oe)'][1]:>.3f},{self.R.now['Pos(deg)'][1]:>.3f}"
    # insBG method
    def setTemp(self, setpoint: float, rate: float, approach: QDInstrumentBase.TemperatureApproach = QDInstrumentBase.TemperatureApproach.FastSettle):
        self.T.setTemp(setpoint, rate, approach)
    def setField(self, setpoint: float, rate: float, approach: QDInstrumentBase.FieldApproach = QDInstrumentBase.FieldApproach.Linear):
        self.M.setField(setpoint, rate, approach)
    def setPosition(self, setpoint: float, rate: float, mode: QDInstrumentBase.PositionMode = QDInstrumentBase.PositionMode.MoveToPosition):
        self.R.setPosition(setpoint, rate, mode)
    def setChamber(self, command: QDInstrumentBase.ChamberCommand):
        self.C.setChamber(command)
    def getNow(self):
        self.T.getNow()
        self.M.getNow()
        self.R.getNow()
        self.C.getNow()
    def reach(self, flag: waitFlag = waitFlag.stable):
        return all([self.T.reach(flag), self.M.reach(flag), self.R.reach(flag), self.C.reach(flag)])
    '''def reach(self, flag: List[waitFlag]) -> bool:
        reached = 4*[False]
        spKeys = list(self.setpoint.keys())
        nowKeys = list(self.now.keys())
        for i in range(len(spKeys)):
            if flag[i] == waitFlag.none:
                reached[i] = True
            elif flag[i] == waitFlag.stable:
                if spKeys[i] == "chamber":
                    reached[i] = int(self.now[nowKeys[i]][1]) in self.waitStable[i]
                else:
                    reached[i] = int(self.now[nowKeys[i]][2]) in self.waitStable[i]
            else:
                if self.targetpoint[spKeys[i]] != None:
                    target = self.targetpoint[spKeys[i]]
                elif self.setpoint[spKeys[i]] != None:
                    target = self.setpoint[spKeys[i]]
                else:
                    reached[i] = True
                    continue
                if i < 3:
                    reached[i] = bool(flag[i] * (target - self.now[nowKeys[i]][1]) < self.error[i])
                else:
                    reached[i] = True
        return all(reached)'''
class QuantumDesignPPMS(QuantumDesign):
    def __init__(self, address: str, port: int = 11000, name: str  = "Quantum Design PPMS"):
        super().__init__(QDInstrumentBase.QDInstrumentType.PPMS, address, port, name)
class QuantumDesignVersaLab(QuantumDesign):
    def __init__(self, address: str, port: int = 11000, name: str  = "Quantum Design VersaLab"):
        super().__init__(QDInstrumentBase.QDInstrumentType.VersaLab, address, port, name)
class QuantumDesignDynaCool(QuantumDesign):
    def __init__(self, address: str, port: int = 11000, name: str  = "Quantum Design DynaCool"):
        super().__init__(QDInstrumentBase.QDInstrumentType.DynaCool, address, port, name)
class QuantumDesignSVSM(QuantumDesign):
    def __init__(self, address: str, port: int = 11000, name: str  = "Quantum Design SVSM"):
        super().__init__(QDInstrumentBase.QDInstrumentType.SVSM, address, port, name)
