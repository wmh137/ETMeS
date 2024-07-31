from .ins import ins, waitFlag
import pyvisa as visa
import time

class LakeShore340(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = [False] # output on/off
        self.setpoint = [None, None] # target temperature, rate
        self.targetpoint = [None] # temperature
        self.now = [None, None] # temperarure, power
        self.nowName = ["T(K)", "power(%)"]
        self.error = [0.05]
    def insInit(self):
        self.res.baud_rate = 9600
        self.res.parity = visa.constants.Parity(1)
        self.res.data_bits = 7
        self.res.write_termination = ""
        self.res.read_termination = "\r\n"
        self.res.write(f"RANGE 5\n")
        time.sleep(1)
    def setRamp(self, rate: float):
        if not rate:
            self.res.write(f"RAMP 1,0\n")
            self.setpoint[1] = 0
        else:
            self.res.write(f"RAMP 1,1,{rate:f}\n")
            self.setpoint[1] = abs(rate)
        time.sleep(0.5)
    def setTemp(self, setpoint: float):
        self.res.write(f"SETP 1,{setpoint:f}\n")
        time.sleep(0.5)
        self.setpoint[0] = setpoint
        self.flag[0] = True
    def setTarget(self, flag: bool, target: float = None):
        if flag:
            self.targetpoint[0] = target
        else:
            self.targetpoint[0] = None
    def stop(self):
        self.res.write(f"RANGE 0\n")
    def getNow(self):
        self.now[0] = float(self.res.query("KRDG? 0\n"))
        self.now[1] = float(self.res.query("HTR?\n"))
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag[0]]:>20s}"
    def setpoint2str(self) -> str:
        if (self.setpoint[0] != None) and (self.setpoint[1] != None):
            return f"{self.setpoint[0]:>9.2f}K{self.setpoint[1]:>7.2f}K/m"
        else:
            return 20*" "
    def now2str(self) -> str:
        return f"{self.now[0]:>9.2f}K{self.now[1]:>9.1f}%"
    def now2record(self) -> str:
        if (self.now[0] != None) and (self.now[1] != None):
            return f"{self.now[0]:>6.3f},{self.now[1]:>6.3f}"
        else:
            return super().now2record()
    def reach(self, flag: waitFlag) -> bool:
        if self.targetpoint[0] == None:
            targetTemp = self.setpoint[0]
        else:
            targetTemp = self.targetpoint[0]
        if (self.now[0] != None) and (targetTemp != None):
            if flag == waitFlag.stable:
                return abs(self.now[0] - targetTemp) < self.error[0]
            else:
                return flag * (targetTemp - self.now[0]) < self.error[0]
        else:
            return True
