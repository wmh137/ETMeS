from .insEnum import *
from .ins import ins
import pyvisa as visa

class Keithley2182A(ins):
    def __data__(self):
        super().__data__()
        self.flag = {'channel': None}
        self.now = {'V(V)': None}
        self.channel = ["CH1", "CH2"]
    def __init__(self, address: str, name: str = "Keithley2182A"):
        super().__init__(address, name, insType.visa)
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.res.write("*RST\n:SENS:FUNC 'VOLT'\n")
        self.flag['channel'] = int(self.res.query(":SENS:CHAN?"))
    def stop(self):
        pass
    # get & check
    def getNow(self):
        self.now['V(V)'] = float(self.res.query(":READ?\n"))
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return super().reach(flag)
    # show & record
    def flag2str(self) -> str:
        return f"{self.channel[self.flag['channel']-1]:>20s}"
    def setpoint2str(self):
        return super().setpoint2str()
    def now2str(self) -> str:
        if not ((self.now['V(V)'] == None) ):
            return f"{self.now['V(V)']:>19.5e}V"
        else:
            return 20*" "
    def now2record(self) -> str:
        if not ((self.now['V(V)'] == None)):
            return [f"{self.now['V(V)']:>.8e}"]
        else:
            return super().now2record()
    # set
    def setChannel(self, flag: int):
        self.res.write(f":SENS:CHAN {flag:d}\n:SENS:VOLT:RANG:AUTO ON\n")
        self.flag['channel'] = flag
    def setNPLC(self, n: int):
        self.res.write(f":SENS:VOLT:NPLC {n:f}\n")
