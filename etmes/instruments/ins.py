from enum import IntEnum

class SM(IntEnum):
    V  = 0
    I  = 1

class waitFlag(IntEnum):
    none = 0
    stable = 2
    positive = 1
    negative = -1

class ins():
    def __init__(self, address: str, name: str = None, visa: bool = True):
        self.address = address
        self.visa = visa
        if name:
            self.name = name
        else:
            self.name = address
        self.res = None # resource
        self.flag = [] # override
        self.setpoint = [] # override
        self.target = [] # override
        self.now = [] # override
        self.nowName = [] # override [str]
        self.ONOFF = ["OFF", "ON"]
    def write(self, cmd: str):
        if self.visa:
            self.res.write(cmd)
        else:
            raise Exception(f"non-visa {self.address} ins.write() not defined!")
    def query(self, cmd: str) -> str:
        if self.visa:
            return self.res.query(cmd)
        else:
            raise Exception(f"non-visa {self.address} ins.query() not defined!")
    def insInit(self): # override
        pass
    def open(self): # override (only&must for self.visa==False)
        raise Exception(f"non-visa {self.address} ins.open() not defined!")
    def close(self): # override (only&must for self.visa==False)
        raise Exception(f"non-visa {self.address} ins.close() not defined!")
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
    def reach(self, flag: waitFlag) -> bool: # override
        return True
