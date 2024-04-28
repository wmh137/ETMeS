import etmes
from typing import List

class meas():
    def __init__(self, exp: etmes.etmes):
        self.__exp = exp
    def SMUsrc(self, src: List[float], SMU: etmes.ins):
        self.__exp.setFlag("MEAS")
        for i in src:
            SMU.setSrc(i)
            self.__exp.refresh()
            self.__exp.record()
        SMU.setSrc(0)
        self.__exp.setFlag("")
    def scanTemp(self, Tstart: float, Tstop: float, Tstep: float, Trate: float, src: List[float], SMU: etmes.ins, Temp: etmes.ins):
        if Tstop>Tstart:
            waitFlag = etmes.waitFlag.positive
        else:
            waitFlag = etmes.waitFlag.negative
        n = (Tstop-Tstart)/Tstep
        if n < 0:
            Tstep = -Tstep
        n = abs(n)
        if round(n)-n<1e-4:
            n = round(n)
        else:
            n = int(n)+1
        Temp.setTemp(Tstart, Trate)
        self.__exp.wait(10, [Temp], [etmes.waitFlag.stable])
        Temp.setTemp(Tstop, Trate)
        for i in range(n):
            Temp.setTarget(True, Tstart+i*Tstep)
            self.__exp.wait(0, [Temp], [waitFlag])
            self.SMUsrc(src, SMU)
        Temp.setTarget(False)
        Temp.setTemp(Tstop, Trate)
        self.__exp.wait(0, [Temp], [waitFlag])
        self.SMUsrc(src, SMU)
    def scanField(self, Fstart: float, Fstop: float, Fstep: float, src: List[float], SMU: etmes.ins, Field: etmes.ins):
        n = (Fstop-Fstart)/Fstep
        if n < 0:
            Fstep = -Fstep
        n = abs(n)
        if round(n)-n<1e-4:
            n = round(n)
        else:
            n = int(n)+1
        Field.setField(Fstart)
        self.__exp.wait(10, [Field], [etmes.waitFlag.stable])
        for i in range(n):
            Field.setField(Fstart+i*Fstep)
            self.__exp.wait(5, [Field], [etmes.waitFlag.stable])
            self.SMUsrc(src, SMU)
        Field.setField(Fstop)
        self.__exp.wait(5, [Field], [etmes.waitFlag.stable])
        self.SMUsrc(src, SMU)
