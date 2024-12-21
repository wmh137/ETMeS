from .insEnum import insType

class ins():
    '''
    The superclass of all instruments classes().

    Attributes
    ----------
        address : str
            address of the instrument
        name : str
            name of the instrument
        type : insType
            type of the instrument
    '''
    def __init__(self, address: str, name: str = None, type: insType = insType.other):
        self.address = address
        if name:
            self.name = name
        else:
            self.name = address
        self.type = type
        self.res = None # resource
        self.ONOFF = ["OFF", "ON"]
        self.log = "" # str
    def write(self, cmd: str): # override (necessary for non-visa instrument)
        raise Exception(f"{self.address} ins.write() not defined!")
    def query(self, cmd: str) -> str: # override (necessary for non-visa instrument)
        raise Exception(f"{self.address} ins.query() not defined!")
    # ins open and close
    def open(self): # override (necessary for non-visa instrument)
        raise Exception(f"{self.address} ins.open() not defined!")
    def close(self): # override (necessary for non-visa instrument)
        raise Exception(f"{self.address} ins.close() not defined!")
    def insInit(self): # override
        pass
    def stop(self): # override
        pass
    # show & record
    def name2str(self) -> str:
        return f"{self.name:>20s}"
    def flag2str(self) -> str: # override
        return 20*" "
    def setpoint2str(self) -> str: # override
        return 20*" "
    def now2str(self) -> str: # override
        return 20*" "
    def now2record(self) -> str: # override
        return (len(self.nowName)-1)*","

class insVisa(ins):
    def __init__(self, address, name = None):
        super().__init__(address, name, insType.visa)
    def write(self, cmd):
        self.res.write(cmd)
    def query(self, cmd):
        return self.res.query(cmd)
