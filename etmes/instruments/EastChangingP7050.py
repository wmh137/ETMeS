from .insEnum import *
from .ins import MagnetController
import pyvisa as visa
import time

class EastChangingP7050(MagnetController):
    def __data__(self):
        super().__data__()
        self.flag = {'output': False}
        self.error = 1
    def __init__(self, address: str, name: str = None):
        super().__init__(address, name, insType.visa)
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
    def stop(self):
        self.res.write(":FIELD 0\n")
    # get & check
    def getNow(self):
        self.now['H(Oe)'] = float(self.res.query(":FIELD?\n"))*1e3
    def reach(self, flag = waitFlag.stable):
        return super().reach(flag)
    # show & record
    def flag2str(self) -> str:
        return super().flag2str()
    def setpoint2str(self) -> str:
        if not (self.setpoint['setpoint'] == None):
            return f"{self.setpoint['setpoint']:>+18.2f}Oe"
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
    # set
    def setField(self, field: float, rate: float):
        '''field in Oe'''
        self.res.write(f":FIELD {field/1e3:+7.4f}\n")
        self.setpoint['setpoint'] = field
        time.sleep(0.1)
