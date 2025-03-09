from .insEnum import *
from .ins import TempController
import pyvisa as visa
from enum import IntEnum

class CH(Enum):
    HO = 0 # Heat Only
    HC = 1 # Heat and Cool
    CO = 2 # Cool Only

class InstecMK2000B(TempController):
    def __data__(self):
        super().__data__()
        self.flag = {'CH': None}
        self.now = {'T(K)': None, 'power(%)': None}
        self.CHStr = ["Heat Only", "Heat&Cool", "Cool Only"]
        self.error = 0.1
    def __init__(self, address: str, name: str = "InstecMK2000B"):
        super().__init__(address, name, insType.visa)
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\r\n"
        self.flag['CH'] = int(self.res.query("TEMP:CHSW?\n"))
        self.setpoint['setpoint'] = float(self.res.query("TEMP:SPO?\n"))+273.15
        self.setpoint['rate'] = float(self.res.query("TEMP:RAT?\n"))
    def stop(self):
        self.res.write("TEMP:STOP\n")
    # get & check
    def getNow(self):
        self.now['T(K)'] = float(self.res.query("TEMP:RTIN?\n").split(":")[2])+273.15
        self.now['power(%)'] = float(self.res.query("TEMP:POW?\n"))*100
    def reach(self, flag = waitFlag.stable):
        return super().reach(flag)
    # show & record
    def flag2str(self) -> str:
        return f"{self.CHStr[self.flag['CH']]:>20s}"
    def setpoint2str(self) -> str:
        if (self.setpoint['setpoint'] != None) and (self.setpoint['rate'] != None):
            return f"{self.setpoint['setpoint']:>9.3f}K{self.setpoint['rate']:>7.2f}K/m"
        else:
            return 20*" "
    def now2str(self) -> str:
        return f"{self.now['T(K)']:>9.3f}K{self.now['power(%)']:>+9.1f}%"
    def now2record(self):
        r = []
        r.append(f"{self.now['T(K)']:>.3f}" if self.now['T(K)'] is not None else "")
        r.append(f"{self.now['power(%)']:>.3f}" if self.now['power(%)'] is not None else "")
        return r
    # set
    def setTemp(self, setpoint: float, rate: float):
        self.res.write(f"TEMP:RAMP {setpoint-273.15:f},{rate:f}\n")
        self.setpoint['setpoint'] = setpoint
        self.setpoint['rate'] = abs(rate)
    def setCH(self, flag: CH):
        self.res.write(f"TEMP:CHSW {flag:d}\n")
        self.flag['CH'] = flag
