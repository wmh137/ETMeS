from typing import Dict, List, Union, Literal
from .insEnum import *
from .ins import ins
from .insio import insioVisaMsg

class cardType(Enum):
    none = "none"
    relay = "relay"
    matrix = "matrix"

class card():
    def __init__(self, cardName: str = "NONE"):
        self.name = cardName
        if cardName == "NONE":
            self.size = [0, 0]
            self.type = cardType.none
        elif cardName == "7012":
            self.size = [4, 10]
            self.type = cardType.matrix
        self.chinit()
    def chinit(self):
        self.channel = [[False for _ in range(self.size[1])] for _ in range(self.size[0])]
    def flag2str(self):
        return f" {self.size[0]:>1d}x{self.size[1]:>2d}{self.name:>5s}"
    def now2str(self, flag: Literal[0, 1]):
        if flag == 0:
            row = [i for i in range(int(self.size[0]/2+0.6))]
        elif flag == 1:
            row = [i for i in range(int(self.size[0]/2+0.6), self.size[0])]
        s = ""
        for i in range(self.size[1]):
            col = [self.channel[r][i] for r in row]
            s += self.__col2str__(col)
        return s+" "*(10-len(s))
    def now2record(self):
        result = 0
        for bit in [bit for row in self.channel for bit in row]:
            result = (result << 1) | bit
        return f"0x{result:x}"
    def ch2str(self, c: List[int]):
        if len(c) == 2:
            return f"{c[0]}{c[1]:02d}"
        else:
            return f"{c[0]}!{c[1]}!{c[2]}"
    def __col2str__(self, col: List[bool]) -> str:
        if col == [False, False] or col ==[False]:
            return " "
        elif col == [True, False]:
            return "▘"
        elif col == [False, True]:
            return "▖"
        elif col == [True, True] or col == [True]:
            return "▌"
        else:
            raise ValueError("Invalid channel state in card")

class Keithley7001(insioVisaMsg, ins):
    now: Dict[str, card]
    def __data__(self):
        super().__data__()
        self.now = {'card1': card(), 'card2': card()}
    def __init__(self, address, name = "Keithley 7001"):
        super().__init__(address, name, insType.visa)
        self.state = ""
    def insInit(self):
        self.res.write_termination = ""
        self.res.read_termination = "\n"
        self.now['card1'] = card(self.query(":CONF:SLOT:CTYP?\n")[1:])
        self.now['card2'] = card(self.query(":CONF:SLOT2:CTYP?\n")[1:])
        self.getNow()
    def stop(self):
        return super().stop()
    # get & check
    def getNow(self):
        for i in range(2):
            self.now[f'card{i+1}'].chinit()
        stateStr = self.query("CLOS:STAT?\n")[2:-1]
        self.state = stateStr
        if stateStr == "":
            return
        for chStr in [s for s in stateStr.split(",")]:
            ch = [[int(n) for n in l]for l in [s.split('!') for s in chStr.split(":")]]
            if len(ch) > 1:
                for c in range(ch[0][2]-1, ch[1][2]):
                    self.now[f'card{ch[0][0]}'].channel[ch[0][1]-1][c] = True
            else:
                self.now[f'card{ch[0][0]}'].channel[ch[0][1]-1][ch[0][2]-1] = True
    def reach(self, flag = waitFlag.stable):
        return super().reach(flag)
    # show & record
    def flag2str(self):
        return f"{self.now['card1'].flag2str()}{self.now['card2'].flag2str()}"
    def setpoint2str(self):
        return f"{self.now['card1'].now2str(0)}{self.now['card2'].now2str(0)}"
    def now2str(self):
        return f"{self.now['card1'].now2str(1)}{self.now['card2'].now2str(1)}"
    def now2record(self):
        return [self.now['card1'].now2record(), self.now['card2'].now2record()]
    # set
    def openChannel(self, channel: Union[List[List[int]], str]):
        if type(channel) == list:
            channel = self.__ch2str__(channel)
        elif type(channel) == str:
            pass
        else:
            raise TypeError("Channel must be a list of lists or a string")
        self.write(":OPEN "+channel+"\n")
    def closeChannel(self, channel: Union[List[List[int]], str]):
        if type(channel) == list:
            channel = self.__ch2str__(channel)
        elif type(channel) == str:
            pass
        else:
            raise TypeError("Channel must be a list of lists or a string")
        self.write(":CLOS "+channel+"\n")
    def setChannel(self, channel: Union[List[List[int]], str]):
        self.openChannel("all")
        self.closeChannel(channel)
    # others
    def __ch2str__(self, channel: List[List[int]]) -> str:
        chStr = ""
        chStr += ",".join([self.now[f'card{c[0]+1}'].ch2str(c) for c in channel])
        return "(@"+chStr+")"
