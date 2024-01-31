from .ins import ins, SM
import pyvisa as visa

class Keithley2400(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = [False, False] # output on/off, 2/4 wire
        self.setpoint = [None, None] # source, V/I
        self.now = [None, None] # V, I
        self.nowName = ["V(V)", "I(A)"]
        self.VI = ["VOLT", "CURR"]
        self.wire = ["2W", "4W"]
    def insInit(self):
        self.res.write_termination = ''
        self.res.read_termination = '\n'
        self.res.write("*RST\n:SENS:FUNC:CONC ON\n:FORM:ELEM VOLT,CURR\n")
    def setRSEN(self, flag: bool):
        self.res.write(f":SYST:RSEN {flag:d}\n")
        self.flag[1] = flag
    def setSMU(self, srcFlag: SM, compliance: float):
        meas = (srcFlag + 1) % 2
        self.res.write(":SOUR:FUNC %s\n:SOUR:%s:MODE FIX\n:SOUR:%s:RANG:AUTO ON\n" % (self.VI[srcFlag], self.VI[srcFlag], self.VI[srcFlag]))
        self.res.write(":SENS:FUNC \"%s\"\n:SENS:%s:RANG:AUTO ON\n:SENS:%s:PROT %f\n" % (self.VI[meas], self.VI[meas], self.VI[meas], compliance))
        self.setpoint[1] = srcFlag
    def setSrc(self, source: float):
        self.res.write(f":SOUR:{self.VI[self.setpoint[1]]}:LEV {source}\n")
        self.setpoint[0] = source
    def setOutput(self, flag: bool):
        self.res.write(f"OUTP {flag:d}\n")
        self.flag[0] = flag
    def stop(self):
        self.res.write("OUTP 0\n")
        self.flag[0] = False
    def getNow(self):
        if self.flag[0]:
            self.now = [float(elem) for elem in self.res.query(":READ?\n").split(",")]
        else:
            self.now = [None, None]
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag[0]]:>10s}{self.wire[self.flag[1]]:>10s}"
    def setpoint2str(self):
        if not ((self.setpoint[0] == None) | (self.setpoint[1] == None)):
            return f"{self.setpoint[0]:>10.3e}{self.VI[self.setpoint[1]]:>10s}"
        else:
            return 20*' '
    def now2str(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f" {self.now[0]:>8.1e}V {self.now[1]:>8.1e}A"
        else:
            return 20*' '
    def now2record(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f"{self.now[0]:>6e},{self.now[1]:>6e}"
        else:
            return super().now2record()
