from .instruments.ins import *
from typing import List, Callable
import time, threading
from etmes import exp
from .instruments.insEnum import waitFlag
from .etmesEnum import scanFlag

class meas():
    '''
    Some measurement functions.

    Attributes
    ----------
        exp : etmes.exp
    '''
    def __init__(self, exp: exp):
        self.__exp = exp
        self.__action = None
        self.__actionFlag = False
    def __actionRepeat(self, interval: float, func: Callable):
        while True:
            if not self.__actionFlag:
                break
            func()
            time.sleep(interval)
    def SMUsrc(self, src: List[float], SMU: SMU, delay: float = 0, pulse: bool = True):
        '''
        SMU source in order.

        Attributes
        ----------
        src : List[float]
            list of source
        SMU : SMU
            instrument of SMU
        delay : float
            source ---wait delay seconds---> refresh&record
        '''
        self.__exp.setFlag("MEAS")
        for i in src:
            SMU.setSrc(i)
            time.sleep(delay)
            self.__exp.refresh()
            self.__exp.record()
        if pulse:
            SMU.setSrc(0)
        self.__exp.setFlag("")
    def scanTemp(self, Tstart: float, Tstop: float, Tstep: float, Trate: float, Temp: TempController, func: Callable, sf: scanFlag = scanFlag.sweep):
        '''
        Attributes
        ----------
        Tstart : float
            first temperature
        Tstop : float
            last temperature
        Tstep : float
            step of temperature
        Trate : float
            rate of warming/cooling
        Temp : TempController
            instrument of temperature controller
        func : function
            a function contains actions at each target with no attribute
            lambda expression is recommanded (e.g.: lambda: meas.SMUsrc([1e-6], k))
        '''
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
        if sf == scanFlag.settle:
            for i in range(n):
                Temp.setTemp(Tstart+i*Tstep, Trate)
                self.__exp.wait(10, [Temp], [wf])
                func()
            Temp.setTemp(Tstop, Trate)
            self.__exp.wait(10, [Temp], [wf])
            func()
        elif sf == scanFlag.sweep:
            if Tstop>Tstart:
                wf = waitFlag.positive
            else:
                wf = waitFlag.negative
            Temp.setTemp(Tstop, Trate)
            for i in range(n):
                Temp.setTempTarget(Tstart+i*Tstep)
                self.__exp.wait(0, [Temp], [wf])
                func()
            Temp.setTempTarget(None)
            Temp.setTemp(Tstop, Trate)
            self.__exp.wait(0, [Temp], [wf])
            func()
    def scanField(self, Fstart: float, Fstop: float, Fstep: float, Frate: float, Mag: MagnetController, func: Callable):
        '''
        Attributes
        ----------
        Fstart : float
            first field
        Fstop : float
            last field
        Fstep : float
            step of field
        Mag : MagnetController
            instrument of magnet controller
        func : function
            a function contains actions at each target with no attribute
            lambda expression is recommanded (e.g.: lambda: meas.SMUsrc([1e-6], k))
        '''
        n = (Fstop-Fstart)/Fstep
        if n < 0:
            Fstep = -Fstep
        n = abs(n)
        if round(n)-n<1e-4:
            n = round(n)
        else:
            n = int(n)+1
        Mag.setField(Fstart, Frate)
        self.__exp.wait(10, [Mag], [waitFlag.stable])
        for i in range(n):
            Mag.setField(Fstart+i*Fstep, Frate)
            self.__exp.wait(5, [Mag], [waitFlag.stable])
            func()
        Mag.setField(Fstop, Frate)
        self.__exp.wait(5, [Mag], [waitFlag.stable])
        func()
    def scanTime(self, t: float, interval: float, func: Callable):
        '''
        Attributes
        ----------
        time : float
            total time
        interval : float
            interval of time
        func : function
            a function contains actions at each target with no attribute
            lambda expression is recommanded (e.g.: lambda: meas.SMUsrc([1e-6], k))
        '''
        func()
        t0 = time.time()
        while time.time()-t0<t:
            func()
            self.__exp.wait(interval, [], [])
    def startAction(self, interval: float, func: Callable):
        '''
        execute **func** per **interval** seconds

        Attributes
        ----------
        interval : float
            interval of time
        func : function
            a function contains actions at each target with no attribute
            lambda expression is recommanded (e.g.: lambda: meas.SMUsrc([1e-6], k))
        '''
        self.__action = threading.Thread(target = lambda: self.__actionRepeat(interval, func), daemon=True)
        self.__actionFlag = True
        self.__action.start()
    def stopAction(self):
        self.__actionFlag = False
        self.__action.join()
        self.__action = None
