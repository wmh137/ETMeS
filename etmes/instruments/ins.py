from enum import IntEnum

class SM(IntEnum):
    V  = 0
    I  = 1

class direction(IntEnum):
    positive = 1
    negative = -1

class ins():
    def __init__(self, address: str, name: str = None):
        self.address = address
        if name:
            self.name = name
        else:
            self.name = address
        self.res = None
        self.flag = []
        self.setpoint = []
        self.now = []
        self.nowName = []
        self.error = []
        self.ONOFF = ["OFF", "ON"]
    def write(self, cmd: str):
        self.res.write(cmd)
    def query(self, cmd: str) -> str:
        return self.res.query(cmd)
    def insInit(self): # override
        pass
    def stop(self): # override
        pass
    def getNow(self): # override
        pass
    def name2str(self) -> str:
        return f"{self.name:>20s}"
    def flag2str(self) -> str: # override
        return 20*' '
    def setpoint2str(self) -> str: # override
        return 20*' '
    def now2str(self) -> str: # override
        return 20*' '
    def now2record(self) -> str: # override
        return len(self.now)*','
    def reach(self) -> bool: # override
        return True
    def crossReach(self, dir: direction) -> bool: # override
        return True
