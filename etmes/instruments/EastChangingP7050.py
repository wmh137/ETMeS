from .ins import ins, direction
import pyvisa as visa
import time

class EastChangingP7050(ins):
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name)
        self.flag = [False] # output on/off
        self.setpoint = [None] # target field
        self.now = [None] # field
        self.nowName = ["H(Oe)"]
        self.error = [1]
    def insInit(self):
        self.res.baud_rate = 9600
        self.res.parity = visa.constants.Parity(1)
        self.res.write_termination = ''
        self.res.read_termination = '\n'
        self.res.write(":REN\n")
        time.sleep(0.1)
        if self.res.query(":MODE?\n") == "CURR":
            self.res.write(":MODE FIELD\n")
            time.sleep(60)
    def setField(self, field: float):
        '''field in Oe'''
        self.res.write(f":FIELD {field/1e3:+7.4f}\n")
        self.setpoint[0] = field
        time.sleep(0.1)
    def stop(self):
        self.res.write(":FIELD 0\n")
    def getNow(self):
        self.now[0] = float(self.res.query(":FIELD?\n"))*1e3
    def flag2str(self) -> str:
        return super().flag2str()
    def setpoint2str(self) -> str:
        if not (self.setpoint[0] == None):
            return f"{self.setpoint[0]:>+18.2f}Oe"
        else:
            return super().setpoint2str()
    def now2str(self) -> str:
        if not (self.now[0] == None):
            return f"{self.now[0]:>+18.2f}Oe"
        else:
            return super().now2str()
    def now2record(self) -> str:
        if not (self.now[0] == None):
            return f"{self.now[0]:>+7.2f}"
        else:
            return super().now2record()
    def reach(self) -> bool:
        return abs(self.now[0] - self.setpoint[0]) < self.error[0]
    def crossReach(self, dir: direction) -> bool:
        return (self.setpoint[0] - self.now[0]) * dir < self.error[0]
