from .ins import ins, waitFlag
from typing import List, Union
import clr

clr.AddReference("etmes/instruments/QDInstrument")

from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

class QuantumDesign(ins):
    def __init__(self, type: QDInstrumentBase.QDInstrumentType, address: str, port: int, name: str):
        super().__init__(address, name, False)
        self.flag = {'temprate': None, 'fieldrate': None, 'posrate': None}
        self.setpoint = {'temp': None, 'field': None, 'pos': None, 'chamber': None}
        self.targetpoint = {'temp': None, 'field': None, 'pos': None, 'chamber': None}
        self.now = [None, None, None, None] # temperature&status, field&status, position&status, chamber
        self.nowName = ["T(K)", "H(Oe)", "Pos(deg)"]
        self.defaultWait = [waitFlag.stable, waitFlag.stable, waitFlag.stable, waitFlag.stable]
        self.type = type
        self.port = port
        self.error = [0.05, 1, 0.1]
        self.waitStable = [[1], [1, 4], [1], [1, 2, 3, 7, 8, 9]]
    def open(self):
        self.res = QDInstrumentFactory.GetQDInstrument(self.type, True, self.address, self.port)
    def close(self):# in build
        pass
    def setTemp(self, setpoint: float, rate: float, approach: QDInstrumentBase.TemperatureApproach = QDInstrumentBase.TemperatureApproach.FastSettle):# in build
        self.res.SetTemperature(setpoint, rate, approach)
        self.setpoint['temp'] = [setpoint, approach]
        self.flag['temprate'] = rate
    def setField(self, setpoint: float, rate: float = 100, approach: QDInstrumentBase.FieldApproach = QDInstrumentBase.FieldApproach.Linear):# in build
        self.res.SetField(setpoint, rate, approach, QDInstrumentBase.FieldMode.Persistent)
        self.setpoint['field'] = [setpoint, approach]
        self.flag['fieldrate'] = rate
    def setPosition(self, setpoint: float, rate: float, mode: QDInstrumentBase.PositionMode = QDInstrumentBase.PositionMode.MoveToPosition):# in build
        self.res.SetPosition("Horizontal Rotator", setpoint, rate, mode)
        self.setpoint['pos'] = [setpoint]
        self.flag['posrate'] = rate
    def setChamber(self, command: QDInstrumentBase.ChamberCommand):
        self.res.SetChamber(command)
        self.setpoint['chamber'] = command
    def setTempTarget(self, target: Union[float, None]):
        self.targetpoint['temp'] = [target, None] # consistent with the structure of setpoint
    def name2str(self) -> str:
        return f"{self.name:>40s}"
    def getNow(self):
        self.now[0] = self.res.GetTemperature(0, QDInstrumentBase.TemperatureStatus(0))
        self.now[1] = self.res.GetField(0, QDInstrumentBase.FieldStatus(0))
        self.now[2] = self.res.GetPosition("Horizontal Rotator", 0, QDInstrumentBase.PositionStatus(0))
        self.now[3] = self.res.GetChamber(QDInstrumentBase.ChamberStatus(0))
    def flag2str(self) -> str:
        s = ""
        if self.flag['temprate'] is not None:
            s += f"{self.flag['temprate']:>5.1f}K/min |"
        else:
            s += 12*" "
        if self.flag['fieldrate'] is not None:
            s += f"{self.flag['fieldrate']:>7.0f}Oe/s   |"
        else:
            s += 15*" "
        if self.flag['posrate'] is not None:
            s += f"{self.flag['posrate']:>5.1f}Dg/s    "
        else:
            s += 13*" "
        return s
    def setpoint2str(self) -> str:
        s = ""
        if self.setpoint['temp'] is not None:
            s += f"{self.setpoint['temp'][0]:>5.1f}K {self.setpoint['temp'][1].ToString():.4s}|"
        else:
            s += 12*" "
        if self.setpoint['field'] is not None:
            s += f"{self.setpoint['field'][0]:>+7.0f}Oe {self.setpoint['field'][1].ToString():.4s}|"
        else:
            s += 15*" "
        if self.setpoint['pos'] is not None:
            s += f"{self.setpoint['pos'][0]:>5.1f}Dg      "
        else:
            s += 13*" "
        return s
    def now2str(self) -> str:
        s = ""
        if self.now[0] is not None:
            s += f"{self.now[0][1]:>5.1f}K {self.res.TemperatureStatusString(self.now[0][2]):>.4s}|"
        else:
            s += 12*" "
        if self.now[1] is not None:
            s += f"{self.now[1][1]:>+7.0f}Oe {self.res.FieldStatusString(self.now[1][2]):>.4s}|"
        else:
            s += 15*" "
        if self.now[2] is not None:
            s += f"{self.now[2][1]:>5.1f}Dg|"
        else:
            s += 8*" "
        if self.now[3] is not None:
            s += f"{self.res.ChamberStatusString(self.now[3][1]):>.5s}"
        else:
            s += 5*" "
        return s
    def now2record(self) -> str:
        return f"{self.now[0][1]:>.5f},{self.now[1][1]:>.3f},{self.now[2][1]:>.3f}"
    def reach(self, flag: List[waitFlag]) -> bool:
        '''reach([Tflag, Fflag, Pflag, Cflag])'''
        reached = 4*[False]
        for i, key in enumerate(self.setpoint.keys()):
            if flag[i] == waitFlag.none:
                reached[i] = True
            elif flag[i] == waitFlag.stable:
                reached[i] = int(self.now[i][2]) in self.waitStable[i]
            else:
                if self.setpoint[key] != None:
                    target = self.targetpoint[key] if self.targetpoint[key] != None else self.setpoint[key]
                    if i < 3:
                        reached[i] = bool(flag[i] * (target[0] - self.now[i][1]) < self.error[i])
                    else:
                        reached[i] = True
                else:
                    reached[i] = True
        return all(reached)
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
