from .ins import ins, waitFlag
import pyvisa as visa
import time

class EastChangingP7050(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = {'output': False}
        self.setpoint = {'field': None}
        self.now = {'H(Oe)': None}
        self.defaultWait = waitFlag.stable
        self.error = [1]
    def insInit(self):
        self.res.baud_rate = 9600
        self.res.parity = visa.constants.Parity(1)
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.res.write(":REN\n")
        time.sleep(0.1)
        if self.res.query(":MODE?\n") == "CURR":
            self.res.write(":MODE FIELD\n")
            time.sleep(60)
    def setField(self, field: float):
        '''field in Oe'''
        self.res.write(f":FIELD {field/1e3:+7.4f}\n")
        self.setpoint['field'] = field
        time.sleep(0.1)
    def stop(self):
        self.res.write(":FIELD 0\n")
    def getNow(self):
        self.now['H(Oe)'] = float(self.res.query(":FIELD?\n"))*1e3
    def flag2str(self) -> str:
        return super().flag2str()
    def setpoint2str(self) -> str:
        if not (self.setpoint['field'] == None):
            return f"{self.setpoint['field']:>+18.2f}Oe"
        else:
            return super().setpoint2str()
    def now2str(self) -> str:
        if not (self.now['H(Oe)'] == None):
            return f"{self.now['H(Oe)']:>+18.2f}Oe"
        else:
            return super().now2str()
    def now2record(self) -> str:
        if not (self.now['H(Oe)'] == None):
            return f"{self.now['H(Oe)']:>+7.2f}"
        else:
            return super().now2record()
    def reach(self, flag: waitFlag) -> bool:
        if flag == waitFlag.stable:
            return abs(self.now['H(Oe)'] - self.setpoint['field']) < self.error[0]
        else:
            return (self.setpoint['field'] - self.now['H(Oe)']) * flag < self.error[0]
