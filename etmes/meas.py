from typing import List
from etmes import etmes, ins, waitFlag

class meas():
    def __init__(self, exp: etmes):
        self.__exp = exp
    def SMUsrc(self, src: List[float], SMU: ins):
        self.__exp.setFlag("MEAS")
        for i in src:
            SMU.setSrc(i)
            self.__exp.refresh()
            self.__exp.record()
        SMU.setSrc(0)
        self.__exp.setFlag("")
    def scanTemp(self, Tstart: float, Tstop: float, Tstep: float, Trate: float, src: List[float], SMU: ins, Temp: ins):
        if Tstop>Tstart:
            wf = waitFlag.positive
        else:
            wf = waitFlag.negative
        n = (Tstop-Tstart)/Tstep
        if n < 0:
            Tstep = -Tstep
        n = abs(n)
        if round(n)-n<1e-4:
            n = round(n)
        else:
            n = int(n)+1
        Temp.setTemp(Tstart, Trate)
        self.__exp.wait(10, [Temp], [waitFlag.stable])
        Temp.setTemp(Tstop, Trate)
        for i in range(n):
            Temp.setTarget(True, Tstart+i*Tstep)
            self.__exp.wait(0, [Temp], [wf])
            self.SMUsrc(src, SMU)
        Temp.setTarget(False)
        Temp.setTemp(Tstop, Trate)
        self.__exp.wait(0, [Temp], [wf])
        self.SMUsrc(src, SMU)
    def scanField(self, Fstart: float, Fstop: float, Fstep: float, src: List[float], SMU: ins, Field: ins):
        n = (Fstop-Fstart)/Fstep
        if n < 0:
            Fstep = -Fstep
        n = abs(n)
        if round(n)-n<1e-4:
            n = round(n)
        else:
            n = int(n)+1
        Field.setField(Fstart)
        self.__exp.wait(10, [Field], [waitFlag.stable])
        for i in range(n):
            Field.setField(Fstart+i*Fstep)
            self.__exp.wait(5, [Field], [waitFlag.stable])
            self.SMUsrc(src, SMU)
        Field.setField(Fstop)
        self.__exp.wait(5, [Field], [waitFlag.stable])
        self.SMUsrc(src, SMU)
