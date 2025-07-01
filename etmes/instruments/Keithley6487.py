from typing import List
from .insEnum import *
from .ins import SMU
from .insio import insioVisaMsg
import time

class Keithley6487(insioVisaMsg, SMU):
    def __data__(self):
        super().__data__()
        self.now = {'I(A)': None, 'V(V)': None}
    def __init__(self, address: str, name: str = "Keithley 6487"):
        super().__init__(address, name, insType.visa)
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.write("*RST\n:FORM:ELEM ALL\nFUNC 'CURR'\nSYST:ZCH ON\nRANG 2e-9\nINIT\nSYST:ZCOR:STAT OFF\n")
        time.sleep(0.5)
        self.write("SYST:ZCOR:ACQ\nSYST:ZCOR ON\nCURR:RANG:AUTO ON\nSYST:ZCH OFF\n")
    def stop(self):
        pass
    # get & check
    def getNow(self):
        now_str = self.query(":READ?\n").split(",")
        self.now['I(A)'] = float(now_str[0][:-1])
        self.now['V(V)'] = float(now_str[3])
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return super().reach(flag)
    # show & record
    def flag2str(self) -> str:
        return super().flag2str()
    def setpoint2str(self):
        return super().setpoint2str()
    def now2str(self) -> str:
        if not ((self.now['I(A)'] == None) and (self.now['V(V)'] == None)):
            return f" {self.now['I(A)']:>8.1e}A {self.now['V(V)']:>8.1e}V"
        else:
            return 20*" "
    def now2record(self) -> List[str]:
        if not ((self.now['I(A)'] == None) and (self.now['V(V)'] == None)):
            return [f"{self.now['I(A)']:>.8e}", f"{self.now['V(V)']:>.8e}"]
        else:
            return super().now2record()
    # set
    def setOutput(self, flag: bool):
        self.write(f"SOUR:VOLT:STAT {flag:d}\n")
    def setSrc(self, source: float):
        self.write(f"SOUR:VOLT {source:f}\n")
    def setNPLC(self, n: int):
        self.write(f"VOLT:NPLC {n:f}\n")
