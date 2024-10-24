from .ins import ins
import pyvisa as visa

class Keithley2182A(ins):
    def __init__(self, address: str, name: str = "Keithley2182A"):
        super().__init__(address, name)
        self.flag = {'channel': 1}#[None] # channel 1/2
        self.now = [None] # V
        self.nowName = ["V(V)"]
        self.channel = ["CH1", "CH2"]
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.res.write("*RST\n:SENS:FUNC 'VOLT'\n")
        self.flag['channel'] = int(self.res.query(":SENS:CHAN?"))
    def setChannel(self, flag: int):
        self.res.write(f":SENS:CHAN {flag:d}\n:SENS:VOLT:RANG:AUTO ON\n")
        self.flag['channel'] = flag
    def setNPLC(self, n: int):
        self.res.write(f":SENS:VOLT:NPLC {n:f}\n")
    def getNow(self):
        self.now = [float(self.res.query(":READ?\n"))]
    def flag2str(self) -> str:
        return f"{self.channel[self.flag['channel']-1]:>20s}"
    def now2str(self) -> str:
        if not ((self.now[0] == None) ):
            return f"{self.now[0]:>19.5e}V"
        else:
            return 20*" "
    def now2record(self) -> str:
        if not ((self.now[0] == None)):
            return f"{self.now[0]:>9e}"
        else:
            return super().now2record()
