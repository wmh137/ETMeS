from .ins import ins, SM
import pyvisa as visa

class Keithley2400(ins):
    def __init__(self, address: str, name: str = "Keithley 2400"):
        super().__init__(address, name)
        self.flag = {'output': False, 'rsen': False, 'panel': False, 'senrange': None, 'cmpl': None}
        self.setpoint = {'source': 0.0, 'VI': SM.V}
        self.now = [None, None] # V, I
        self.nowName = ["V(V)", "I(A)"]
        self.wire = ["2W", "4W"]
        self.VI = ["VOLT", "CURR"]
        self.panel = ["FRONT", "REAR"]
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.res.write(":SENS:FUNC:CONC ON\n:FORM:ELEM VOLT,CURR\n")
        self.flag['output'] = bool(int(self.res.query(":OUTP?\n")))
        self.flag['rsen'] = bool(int(self.res.query(":SYST:RSEN?\n")))
        self.flag['panel'] = False if self.res.query(":ROUT:TERM?\n") == "FRON" else True
        sourFunc = self.res.query(":SOUR:FUNC?")
        if sourFunc == "VOLT":
            self.setpoint['VI'] = SM.V
        elif sourFunc == "CURR":
            self.setpoint['VI'] = SM.I
        self.setpoint['source'] = float(self.res.query(f":SOUR:{self.VI[self.setpoint['VI']]}:LEV?\n"))
        self.flag['senrange'] = float(self.res.query(f":SENS:{self.VI[(self.setpoint['VI']+1)%2]}:RANG?\n"))
        self.flag['cmpl'] = float(self.res.query(f":SENS:{self.VI[(self.setpoint['VI']+1)%2]}:PROT?\n"))
    def setRSEN(self, flag: bool):
        self.res.write(f":SYST:RSEN {flag:d}\n")
        self.flag['rsen'] = flag
    def setPanel(self, flag: bool):
        if flag != self.flag['panel']:
            self.res.write(f":ROUT:TERM {self.panel[self.flag['panel']]}\n")
            self.flag['output'] = False
            self.flag['panel'] = flag
    def setSMU(self, srcFlag: SM, cmpl: float):
        meas = (srcFlag + 1) % 2
        self.res.write(f":SOUR:FUNC {self.VI[srcFlag]}\n:SOUR:{self.VI[srcFlag]}:MODE FIX\n:SENS:FUNC \"{self.VI[meas]}\"\n")
        if cmpl < self.flag['senrange']:
            self.res.write(f":SENS:{self.VI[meas]}:RANG {cmpl:f}\n:SENS:{self.VI[meas]}:PROT {cmpl:f}\n")
        else:
            self.res.write(f":SENS:{self.VI[meas]}:PROT {cmpl:f}\n:SENS:{self.VI[meas]}:RANG {cmpl:f}\n")
        self.setpoint['VI'] = srcFlag
        self.flag['senrange'] = float(self.res.query(f":SENS:{self.VI[meas]}:RANG?\n"))
        self.flag['cmpl'] = cmpl
    def setSrc(self, source: float):
        self.res.write(f":SOUR:{self.VI[self.setpoint['VI']]}:RANG {source}\n:SOUR:{self.VI[self.setpoint['VI']]}:LEV {source}\n")
        self.setpoint['source'] = source
    def setOutput(self, flag: bool):
        self.res.write(f"OUTP {flag:d}\n")
        self.flag['output'] = flag
    def stop(self):
        self.res.write("OUTP 0\n")
        self.flag['output'] = False
    def getNow(self):
        if self.flag['output']:
            self.now = [float(elem) for elem in self.res.query(":READ?\n").split(",")]
        else:
            self.now = [None, None]
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag['output']]:>5s}{self.wire[self.flag['rsen']]:>5s}{self.panel[self.flag['panel']]:>10s}"
    def setpoint2str(self):
        if not ((self.setpoint['source'] == None) | (self.setpoint['VI'] == None)):
            return f"{self.setpoint['source']:>10.2e}{self.VI[self.setpoint['VI']]:>10s}"
        else:
            return 20*" "
    def now2str(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f" {self.now[0]:>8.1e}V {self.now[1]:>8.1e}A"
        else:
            return 20*" "
    def now2record(self) -> str:
        if not ((self.now[0] == None) | (self.now[1] == None)):
            return f"{self.now[0]:>9e},{self.now[1]:>9e}"
        else:
            return super().now2record()
