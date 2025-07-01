from typing import List, Union, Literal
from .insEnum import *
from .ins import SMU
from .insio import insioVisaMsg

class Keithley2400(insioVisaMsg, SMU):
    def __data__(self):
        super().__data__()
        self.flag = {'output': False, 'rsen': False, 'panel': False, 'senrange': None, 'cmpl': None}
        self.setpoint = {'source': None, 'VI': None}
        self.now = {'V(V)': None, 'I(A)': None}
        self.wire = ["2W", "4W"]
        self.VI = ["VOLT", "CURR"]
        self.panel = ["FRONT", "REAR"]
    def __init__(self, address: str, name: str = "Keithley 2400"):
        super().__init__(address, name, insType.visa)
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.write(":SENS:FUNC:CONC ON\n:FORM:ELEM VOLT,CURR\n")
        self.__getFlagSetpoint__()
    def stop(self):
        self.write("OUTP 0\n")
        self.flag['output'] = False
    # get & check
    def getNow(self):
        if self.flag['output']:
            v_i = [float(elem) for elem in self.query(":READ?\n").split(",")]
            self.now['V(V)'] = v_i[0]
            self.now['I(A)'] = v_i[1]
        else:
            self.now['V(V)'] = None
            self.now['I(A)'] = None
    def reach(self, flag: waitFlag = waitFlag.stable) -> bool:
        return super().reach(flag)
    # show & record
    def flag2str(self) -> str:
        return f"{self.ONOFF[self.flag['output']]:>5s}{self.wire[self.flag['rsen']]:>5s}{self.panel[self.flag['panel']]:>10s}"
    def setpoint2str(self):
        if not ((self.setpoint['source'] == None) | (self.setpoint['VI'] == None)):
            return f"{self.setpoint['source']:>10.2e}{self.VI[self.setpoint['VI']]:>10s}"
        else:
            return 20*" "
    def now2str(self) -> str:
        if not ((self.now['V(V)'] == None) | (self.now['I(A)'] == None)):
            return f" {self.now['V(V)']:>8.1e}V {self.now['I(A)']:>8.1e}A"
        else:
            return 20*" "
    def now2record(self) -> List[str]:
        if not ((self.now['V(V)'] == None) | (self.now['I(A)'] == None)):
            return [f"{self.now['V(V)']:>.6e}", f"{self.now['I(A)']:>.6e}"]
        else:
            return super().now2record()
    # set
    def setSrc(self, source: float):
        self.write(f":SOUR:{self.VI[self.setpoint['VI']]}:RANG {source}\n:SOUR:{self.VI[self.setpoint['VI']]}:LEV {source}\n")
        self.setpoint['source'] = source
    def setRSEN(self, flag: bool):
        self.write(f":SYST:RSEN {flag:d}\n")
        self.flag['rsen'] = flag
    def setPanel(self, flag: bool):
        if flag != self.flag['panel']:
            self.write(f":ROUT:TERM {self.panel[flag]}\n")
            self.flag['output'] = False
            self.flag['panel'] = flag
    def setSMU(self, srcFlag: Union[SM, Literal["I", "V"]], cmpl: float):
        srcFlag = SM(srcFlag)
        meas = (srcFlag + 1) % 2
        self.write(f":SOUR:FUNC {self.VI[srcFlag]}\n:SOUR:{self.VI[srcFlag]}:MODE FIX\n:SENS:FUNC \"{self.VI[meas]}\"\n")
        self.setpoint['VI'] = srcFlag
        self.flag['output'] = False
        self.flag['senrange'] = float(self.query(f":SENS:{self.VI[(self.setpoint['VI']+1)%2]}:RANG?\n"))
        if cmpl < self.flag['senrange']:
            self.write(f":SENS:{self.VI[meas]}:RANG {cmpl:f}\n:SENS:{self.VI[meas]}:PROT {cmpl:f}\n")
        else:
            self.write(f":SENS:{self.VI[meas]}:PROT {cmpl:f}\n:SENS:{self.VI[meas]}:RANG {cmpl:f}\n")
        self.flag['senrange'] = float(self.query(f":SENS:{self.VI[meas]}:RANG?\n"))
        self.flag['cmpl'] = cmpl
    def setOutput(self, flag: bool):
        self.write(f"OUTP {flag:d}\n")
        self.flag['output'] = flag
    # others
    def __getFlagSetpoint__(self):
        self.flag['output'] = bool(int(self.query(":OUTP?\n")))
        self.flag['rsen'] = bool(int(self.query(":SYST:RSEN?\n")))
        self.flag['panel'] = False if self.query(":ROUT:TERM?\n") == "FRON" else True
        sourFunc = self.query(":SOUR:FUNC?")
        if sourFunc == "VOLT":
            self.setpoint['VI'] = SM.V
        elif sourFunc == "CURR":
            self.setpoint['VI'] = SM.I
        self.setpoint['source'] = float(self.query(f":SOUR:{self.VI[self.setpoint['VI']]}:LEV?\n"))
        self.flag['senrange'] = float(self.query(f":SENS:{self.VI[(self.setpoint['VI']+1)%2]}:RANG?\n"))
        self.flag['cmpl'] = float(self.query(f":SENS:{self.VI[(self.setpoint['VI']+1)%2]}:PROT?\n"))
