from .insEnum import *
from .ins import TempController
import pyvisa as visa
import time

class LakeShore340(TempController):
    def __data__(self):
        super().__data__()
        self.flag = {'output': False}
        self.now['power(%)'] = None
        self.error = 0.05
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name, insType.visa)
    def insInit(self):
        self.res.baud_rate = 9600
        self.res.parity = visa.constants.Parity(1)
        self.res.data_bits = 7
        self.res.write_termination = ""
        self.res.read_termination = "\r\n"
        self.res.write(f"RANGE 5\n")
        time.sleep(1)
    def stop(self):
        self.res.write(f"RANGE 0\n")
    # get & check
    def getNow(self):
        self.now['T(K)'] = float(self.res.query("KRDG? 0\n"))
        self.now['power(%)'] = float(self.res.query("HTR?\n"))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return super().reach(flag)
    # show & record
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag['output']]:>20s}"
    def setpoint2str(self) -> str:
        if (self.setpoint['setpoint'] != None) and (self.setpoint['rate'] != None):
            return f"{self.setpoint['setpoint']:>9.2f}K{self.setpoint['rate']:>7.2f}K/m"
        else:
            return 20*" "
    def now2str(self) -> str:
        return f"{self.now['T(K)']:>9.2f}K{self.now['power(%)']:>9.1f}%"
    def now2record(self) -> str:
        if (self.now['T(K)'] != None) and (self.now['power(%)'] != None):
            return [f"{self.now['T(K)']:>6.3f}", f"{self.now['power(%)']:>6.3f}"]
        else:
            return super().now2record()
    # set
    def setTemp(self, setpoint: float):
        self.res.write(f"SETP 1,{setpoint:f}\n")
        time.sleep(0.5)
        self.setpoint['setpoint'] = setpoint
        self.flag['output'] = True
    def setRamp(self, rate: float):
        if not rate:
            self.res.write(f"RAMP 1,0\n")
            self.setpoint['rate'] = 0
        else:
            self.res.write(f"RAMP 1,1,{rate:f}\n")
            self.setpoint['rate'] = abs(rate)
        time.sleep(0.5)
