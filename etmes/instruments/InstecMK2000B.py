from .ins import ins, waitFlag
from typing import Union
import pyvisa as visa
from enum import IntEnum

class CH(IntEnum):
    HO = 0 # Heat Only
    HC = 1 # Heat and Cool
    CO = 2 # Cool Only

class InstecMK2000B(ins):
    def __init__(self, address: str, name: str = "InstecMK2000B"):
        super().__init__(address, name)
        self.flag = {'CH': None} # CH in build
        self.setpoint = {'setpoint': None, 'rate': None}
        self.targetpoint = None # temperature
        self.now = {'T(K)': None, 'power(%)': None}
        self.defaultWait = waitFlag.stable
        self.CHStr = ["Heat Only", "Heat&Cool", "Cool Only"]
        self.error = [0.1]
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\r\n"
        self.flag['CH'] = int(self.res.query("TEMP:CHSW?\n"))
    def setCH(self, flag: CH):
        self.res.write(f"TEMP:CHSW {flag:d}\n")
        self.flag['CH'] = flag
    def setTemp(self, setpoint: float, rate: float):
        self.res.write(f"TEMP:RAMP {setpoint-273.15:f},{rate:f}\n")
        self.setpoint['setpoint'] = setpoint
        self.setpoint['rate'] = abs(rate)
    def setTempTarget(self, target: Union[float, None]):
        self.targetpoint = target
    def stop(self):
        self.res.write("TEMP:STOP\n")
    def getNow(self):
        self.now['T(K)'] = float(self.res.query("TEMP:RTIN?\n").split(":")[2])+273.15
        self.now['power(%)'] = float(self.res.query("TEMP:POW?\n"))*100
    def flag2str(self) -> str:
        return f"{self.CHStr[self.flag['CH']]:>20s}"
    def setpoint2str(self) -> str:
        if (self.setpoint['setpoint'] != None) and (self.setpoint['rate'] != None):
            return f"{self.setpoint['setpoint']:>9.3f}K{self.setpoint['rate']:>7.2f}K/m"
        else:
            return 20*" "
    def now2str(self) -> str:
        return f"{self.now['T(K)']:>9.3f}K{self.now['power(%)']:>+9.1f}%"
    def now2record(self) -> str:
        if (self.now['T(K)'] != None) and (self.now['power(%)'] != None):
            return f"{self.now['T(K)']:>6.3f},{self.now['power(%)']:>6.3f}"
        else:
            return super().now2record()
    def reach(self, flag: waitFlag) -> bool:
        if self.targetpoint == None:
            targetTemp = self.setpoint['setpoint']
        else:
            targetTemp = self.targetpoint
        if (self.now['T(K)'] != None) and (targetTemp != None):
            if flag == waitFlag.stable:
                return abs(self.now['T(K)'] - targetTemp) < self.error[0]
            else:
                return flag * (targetTemp - self.now['T(K)']) < self.error[0]
        else:
            return True
