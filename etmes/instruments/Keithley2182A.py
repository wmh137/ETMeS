from .ins import insVisa
from .insBG import insBG
import pyvisa as visa

class Keithley2182A(insVisa, insBG):
    def __init__(self, address: str, name: str = "Keithley2182A"):
        insVisa.__init__(self, address, name)
        insBG.__init__(self)
        self.flag = {'channel': None}
        self.now = {'V(V)': None}
        self.channel = ["CH1", "CH2"]
    # ins method
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.res.write("*RST\n:SENS:FUNC 'VOLT'\n")
        self.flag['channel'] = int(self.res.query(":SENS:CHAN?"))
    def flag2str(self) -> str:
        return f"{self.channel[self.flag['channel']-1]:>20s}"
    def now2str(self) -> str:
        if not ((self.now['V(V)'] == None) ):
            return f"{self.now['V(V)']:>19.5e}V"
        else:
            return 20*" "
    def now2record(self) -> str:
        if not ((self.now['V(V)'] == None)):
            return f"{self.now['V(V)']:>9e}"
        else:
            return super().now2record()
    # insBG method
    def getNow(self):
        self.now['V(V)'] = float(self.res.query(":READ?\n"))
    def setChannel(self, flag: int):
        self.res.write(f":SENS:CHAN {flag:d}\n:SENS:VOLT:RANG:AUTO ON\n")
        self.flag['channel'] = flag
    def setNPLC(self, n: int):
        self.res.write(f":SENS:VOLT:NPLC {n:f}\n")
