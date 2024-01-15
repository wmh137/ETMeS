import pyvisa as visa
from enum import IntEnum
import time

class SM(IntEnum):
    V  = 0
    I  = 1

class direction(IntEnum):
    positive = 1
    negative = -1

class ins():
    def __init__(self, address: str, name: str = None):
        self.address = address
        if name:
            self.name = name
        else:
            self.name = address
        self.res = None
        self.flag = []
        self.setpoint = []
        self.now = []
        self.nowName = []
        self.error = []
        self.ONOFF = ["OFF", "ON"]
    def write(self, cmd: str):
        self.res.write(cmd)
    def query(self, cmd: str) -> str:
        return self.res.query(cmd)
    def insInit(self): # override
        pass
    def stop(self): # override
        pass
    def getNow(self): # override
        pass
    def name2str(self) -> str:
        return f"{self.name:>20s}"
    def flag2str(self) -> str: # override
        return 20*' '
    def setpoint2str(self) -> str: # override
        return 20*' '
    def now2str(self) -> str: # override
        return 20*' '
    def now2record(self) -> str: # override
        return len(self.now)*','
    def reach(self) -> bool: # override
        return True
    def crossReach(self, dir: direction) -> bool: # override
        return True

class Keithley2400(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = [False, False] # output on/off, 2/4 wire
        self.setpoint = [None, None] # source, V/I
        self.now = [None, None] # V, I
        self.nowName = ["V", "I"]
        self.VI = ["VOLT", "CURR"]
        self.wire = ["2W", "4W"]
    def insInit(self):
        self.res.write_termination = ''
        self.res.read_termination = '\n'
        self.res.write("*RST\n:SENS:FUNC:CONC ON\n:FORM:ELEM VOLT,CURR\n")
    def setRSEN(self, flag: bool):
        self.res.write(f":SYST:RSEN {flag:d}\n")
        self.flag[1] = flag
    def setSMU(self, srcFlag: SM, compliance: float):
        meas = (srcFlag + 1) % 2
        self.res.write(":SOUR:FUNC %s\n:SOUR:%s:MODE FIX\n:SOUR:%s:RANG:AUTO ON\n" % (self.VI[srcFlag], self.VI[srcFlag], self.VI[srcFlag]))
        self.res.write(":SENS:FUNC \"%s\"\n:SENS:%s:RANG:AUTO ON\n:SENS:%s:PROT %f\n" % (self.VI[meas], self.VI[meas], self.VI[meas], compliance))
        self.setpoint[1] = srcFlag
    def setSrc(self, source: float):
        self.res.write(f":SOUR:{self.VI[self.setpoint[1]]}:LEV {source}\n")
        self.setpoint[0] = source
    def setOutput(self, flag: bool):
        self.res.write(f"OUTP {flag:d}\n")
        self.flag[0] = flag
    def stop(self):
        self.res.write("OUTP 0\n")
        self.flag[0] = False
    def getNow(self) -> list:
        if self.flag[0]:
            self.now = [float(elem) for elem in self.res.query(":READ?\n").split(",")]
        else:
            self.now = [None, None]
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag[0]]:>10s}{self.wire[self.flag[1]]:>10s}"
    def setpoint2str(self):
        if not ((self.setpoint[0] == None) | (self.setpoint[1] == None)):
            return f"{self.setpoint[0]:>10.3e}{self.VI[self.setpoint[1]]:>10s}"
        else:
            return 20*' '
    def now2str(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f" {self.now[0]:>8.1e}V {self.now[1]:>8.1e}A"
        else:
            return 20*' '
    def now2record(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f"{self.now[0]:>6e},{self.now[1]:>6e}"
        else:
            return super().now2record()

class InstecMK2000B(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = [False] # output on/off
        self.setpoint = [None, None] # target temperature, rate
        self.now = [None, None] # temperarure, power
        self.nowName = ["T", "power"]
        self.error = [0.1]
    def insInit(self):
        self.res.write_termination = ''
        self.res.read_termination = '\r\n'
    def setTemp(self, setpoint: float, rate: float):
        self.res.write(f"TEMP:RAMP {setpoint-273.15:f},{rate:f}\n")
        self.setpoint[0] = setpoint
        self.setpoint[1] = abs(rate)
        self.flag[0] = True
    def stop(self):
        self.res.write("TEMP:STOP\n")
    def getNow(self):
        self.now[0] = float(self.res.query("TEMP:RTIN?\n").split(":")[2])+273.15
        self.now[1] = float(self.res.query("TEMP:POW?\n"))*100
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag[0]]:>10s}"
    def setpoint2str(self) -> str:
        if not ((self.setpoint[0] == None) | (self.setpoint[1] == None)):
            return f"{self.setpoint[0]:>9.2f}K{self.setpoint[1]:>7.2f}K/m"
        else:
            return 20*' '
    def now2str(self) -> str:
        return f"{self.now[0]:>9.2f}K{self.now[1]:>9.1f}%"
    def now2record(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f"{self.now[0]:>6.3f},{self.now[1]:>6.3f}"
        else:
            return super().now2record()
    def reach(self) -> bool:
        if not ((self.now[0] == None) | (self.setpoint[0] == None)):
            if abs(self.now[0] - self.setpoint[0]) < self.error[0]:
                return True
            else:
                return False
        else:
            return True
    def crossReach(self, dir: direction) -> bool:
        if not ((self.now[0] == None) | (self.setpoint[0] == None)):
            if self.setpoint[0] - self.now[0] < self.error[0] * dir:
                return True
            else:
                return False
        else:
            return True

class LakeShore340(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = [False] # output on/off
        self.setpoint = [None, None] # target temperature, rate
        self.now = [None, None] # temperarure, power
        self.nowName = ["T", "power"]
        self.error = [0.1]
    def insInit(self):
        self.res.baud_rate = 9600
        self.res.parity = visa.constants.Parity(1)
        self.res.data_bits = 7
        self.res.write_termination = ''
        self.res.read_termination = '\r\n'
        self.res.write(f"RANGE 5\n")
        time.sleep(1)
    def setTemp(self, setpoint: float, rate: float):
        self.res.write(f"RAMP 1,1,{rate:f}\nSETP 1,{setpoint:f}\n")
        time.sleep(2)
        self.setpoint[0] = setpoint
        self.setpoint[1] = abs(rate)
        self.flag[0] = True
    def stop(self):
        self.res.write(f"RANGE 0\n")
    def getNow(self):
        self.now[0] = float(self.res.query("KRDG? 0\n"))
        self.now[1] = float(self.res.query("HTR?\n"))
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag[0]]:>10s}"
    def setpoint2str(self) -> str:
        if not ((self.setpoint[0] == None) | (self.setpoint[1] == None)):
            return f"{self.setpoint[0]:>9.2f}K{self.setpoint[1]:>7.2f}K/m"
        else:
            return 20*' '
    def now2str(self) -> str:
        return f"{self.now[0]:>9.2f}K{self.now[1]:>9.1f}%"
    def now2record(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f"{self.now[0]:>6.3f},{self.now[1]:>6.3f}"
        else:
            return super().now2record()
    def reach(self) -> bool:
        if not ((self.now[0] == None) | (self.setpoint[0] == None)):
            if abs(self.now[0] - self.setpoint[0]) < self.error[0]:
                return True
            else:
                return False
        else:
            return True
    def crossReach(self, dir: direction) -> bool:
        if not ((self.now[0] == None) | (self.setpoint[0] == None)):
            if self.setpoint[0] - self.now[0] < self.error[0] * dir:
                return True
            else:
                return False
        else:
            return True
