from .ins import ins, direction
import pyvisa as visa
from enum import IntEnum

class CH(IntEnum):
    HO = 0 # Heat Only
    HC = 1 # Heat and Cool
    CO = 2 # Cool Only

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
    def setCH(self, flag: CH):
        self.res.write(f"TEMP:CHSW {flag:d}\n")
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
            return f"{self.setpoint[0]:>9.3f}K{self.setpoint[1]:>7.2f}K/m"
        else:
            return 20*' '
    def now2str(self) -> str:
        return f"{self.now[0]:>9.3f}K{self.now[1]:>9.1f}%"
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
            if (self.setpoint[0] - self.now[0]) * dir < self.error[0]:
                return True
            else:
                return False
        else:
            return True
