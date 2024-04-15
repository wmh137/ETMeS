from .ins import ins, direction
import clr
from enum import Flag, auto

clr.AddReference('etmes/instruments/QDInstrument')

from QuantumDesign.QDInstrument import QDInstrumentBase, QDInstrumentFactory

class waitFlag(Flag):
    none = auto()
    T = auto() # temperature
    F = auto() # field
    P = auto() # position
    C = auto() # chamber
    all = T|F|P|C

class QuantumDesign(ins):
    def __init__(self, type: QDInstrumentBase.QDInstrumentType, address: str, port: int, name: str):
        super().__init__(address, name, False)
        self.flag = [None, None, None] # temperature rate, field rate, position rate
        self.setpoint = [None, None, None] # temperature&approach, field&approach, position
        self.now = [None, None, None, None] #  temperature&status, field&status, position&status, chamber
        self.nowName = ["T(K)", "H(Oe)", "Pos(deg)"]
        self.type = type
        self.port = port
        self.waitFlag = waitFlag.none
    def open(self):
        self.res = QDInstrumentFactory.GetQDInstrument(self.type, True, self.address, self.port)
    def close(self):# in build
        pass
    def setWait(self, flag: waitFlag):
        self.waitFlag = flag
    def setTemp(self, setpoint: float, rate: float, approach: QDInstrumentBase.TemperatureApproach = QDInstrumentBase.TemperatureApproach.FastSettle):# in build
        self.res.SetTemperature(setpoint, rate, approach)
        self.setpoint[0] = [setpoint, approach]
        self.flag[0] = rate
    def setField(self, setpoint: float, rate: float, approach: QDInstrumentBase.FieldApproach = QDInstrumentBase.FieldApproach.Linear):# in build
        self.res.SetField(setpoint, rate, approach, QDInstrumentBase.FieldMode.Persistent)
        self.setpoint[1] = [setpoint, approach]
        self.flag[1] = rate
    def setPosition(self, setpoint: float, rate: float, mode: QDInstrumentBase.PositionMode = QDInstrumentBase.PositionMode.MoveToPosition):# in build
        self.res.SetPosition("Horizontal Rotator", setpoint, rate, mode)
        self.setpoint[2] = setpoint
        self.flag[2] = rate
    def setChamber(self, command: QDInstrumentBase.ChamberCommand):
        self.res.SetChamber(command)
    def name2str(self) -> str:
        return f"{self.name:>40s}"
    def getNow(self):
        self.now[0] = self.res.GetTemperature(0, QDInstrumentBase.TemperatureStatus(0))
        self.now[1] = self.res.GetField(0, QDInstrumentBase.FieldStatus(0))
        self.now[2] = self.res.GetPosition("Horizontal Rotator", 0, QDInstrumentBase.PositionStatus(0))
        self.now[3] = self.res.GetChamber(QDInstrumentBase.ChamberStatus(0))[1]
    def flag2str(self) -> str:
        s = ""
        if self.flag[0] is not None:
            s += f"{self.flag[0]:>5.1f}K/min |"
        else:
            s += 12*" "
        if self.flag[1] is not None:
            s += f"{self.flag[1]:>7.0f}Oe/s   |"
        else:
            s += 15*" "
        if self.flag[2] is not None:
            s += f"{self.flag[2]:>5.1f}Dg/s    "
        else:
            s += 13*" "
        return s
    def setpoint2str(self) -> str:
        s = ""
        if self.setpoint[0] is not None:
            s += f"{self.setpoint[0][0]:>5.1f}K {self.setpoint[0][1].ToString():.4s}|"
        else:
            s += 12*" "
        if self.setpoint[1] is not None:
            s += f"{self.setpoint[1][0]:>+7.0f}Oe {self.setpoint[1][1].ToString():.4s}|"
        else:
            s += 15*" "
        if self.setpoint[2] is not None:
            s += f"{self.setpoint[2]:>5.1f}Dg      "
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
            s += f"{self.res.ChamberStatusString(self.now[3]):>.5s}"
        else:
            s += 5*""
        return s
    def now2record(self) -> str:
        return f"{self.now[0][1]:>.5f},{self.now[1][1]:>.3f},{self.now[2][1]:>.3f}"
    def reach(self) -> bool:
        if self.waitFlag&waitFlag.none:
            return True
        if self.waitFlag&waitFlag.T and self.now[0][2] != QDInstrumentBase.TemperatureStatus.Stable:
            return False
        if self.waitFlag&waitFlag.F and self.now[1][2] != QDInstrumentBase.FieldStatus.StablePersistent and self.now[1][2] != QDInstrumentBase.FieldStatus.StableDriven:
            return False
        if self.waitFlag&waitFlag.P and self.now[2][2] != QDInstrumentBase.PositionStatus.AtTarget:
            return False
        if self.waitFlag&waitFlag.C and int(self.now[3]) not in [1, 2, 3, 7, 8, 9]:
            return False
        return True
    def crossReach(self, dir: direction) -> bool:
        return True
class QuantumDesignDynaCool(QuantumDesign):
    def __init__(self, address: str, port: int = 11000, name: str  = "Quantum Design DynaCool"):
        super().__init__(QDInstrumentBase.QDInstrumentType.DynaCool, address, port, name)
