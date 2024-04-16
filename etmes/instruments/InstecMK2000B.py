from .ins import ins, waitFlag
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
        self.nowName = ["T(K)", "power(%)"]
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
        return f"{self.ONOFF[self.flag[0]]:>20s}"
    def setpoint2str(self) -> str:
        if (self.setpoint[0] != None) and (self.setpoint[1] != None):
            return f"{self.setpoint[0]:>9.3f}K{self.setpoint[1]:>7.2f}K/m"
        else:
            return 20*' '
    def now2str(self) -> str:
        return f"{self.now[0]:>9.3f}K{self.now[1]:>+9.1f}%"
    def now2record(self) -> str:
        if (self.now[0] != None) and (self.now[1] != None):
            return f"{self.now[0]:>6.3f},{self.now[1]:>6.3f}"
        else:
            return super().now2record()
    def reach(self, flag: waitFlag) -> bool:
        if (self.now[0] != None) and (self.setpoint[0] != None):
            if flag == waitFlag.stable:
                return abs(self.now[0] - self.setpoint[0]) < self.error[0]
            else:
                return flag * (self.setpoint[0] - self.now[0]) < self.error[0]
        else:
            return True
