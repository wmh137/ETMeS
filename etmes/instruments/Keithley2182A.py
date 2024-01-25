from .ins import ins
import pyvisa as visa

class Keithley2182A(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = [None] # channel 1/2
        self.now = [None] # V
        self.nowName = ["V"]
        self.channel = ["CH1", "CH2"]
    def insInit(self):
        self.res.write_termination = ''
        self.res.read_termination = '\n'
        self.res.write("*RST\n:SENS:FUNC 'VOLT'\n")
    def setChannel(self, flag: int):
        self.res.write(f":SENS:CHAN {flag:d}\n:SENS:VOLT:RANG:AUTO ON\n")
        self.flag[0] = flag
    def getNow(self):
        self.now = [float(self.res.query(":READ?\n"))]
    def flag2str(self) -> str:
        return f"{self.channel[self.flag[0]]:>20s}"
    def now2str(self) -> str:
        if not ((self.now[0] == None) ):
            return f"{self.now[0]:>19.5e}V"
        else:
            return 20*' '
    def now2record(self) -> str:
        if not ((self.now[0] == None)):
            return f"{self.now[0]:>6e}"
        else:
            return super().now2record()
