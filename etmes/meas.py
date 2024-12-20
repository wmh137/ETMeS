from typing import List, Union, Callable
import time, threading
from etmes import exp, ins, waitFlag

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
    def SMUsrc(self, src: List[float], SMU: ins, delay: float = 0, pulse: bool = True):
        '''
        SMU source in order.

        Attributes
        ----------
        src : List[float]
            list of source
        SMU : ins
            instrument of SMU, SMU.setSrc(src: float) is required
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
    def scanTemp(self, Tstart: float, Tstop: float, Tstep: float, Trate: float, Temp: ins, func: Callable):
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
        Temp : ins
            instrument of temperature controller
            Temp.setTemp(setpoint: float, rate: float) and Temp.setTempTarget(target: Union[float, None]) are required.
        func : function
            a function contains actions at each target with no attribute
            lambda expression is recommanded (e.g.: lambda: meas.SMUsrc([1e-6], k))
        '''
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
            Temp.setTempTarget(Tstart+i*Tstep)
            self.__exp.wait(0, [Temp], [wf])
            func()
        Temp.setTempTarget(None)
        Temp.setTemp(Tstop, Trate)
        self.__exp.wait(0, [Temp], [wf])
        func()
    def scanField(self, Fstart: float, Fstop: float, Fstep: float, Mag: ins, func: Callable):
        '''
        Attributes
        ----------
        Fstart : float
            first field
        Fstop : float
            last field
        Fstep : float
            step of field
        Field : ins
            instrument of magnet controller
            Mag.setField(field: float) is required.
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
        Mag.setField(Fstart)
        self.__exp.wait(10, [Mag], [waitFlag.stable])
        for i in range(n):
            Mag.setField(Fstart+i*Fstep)
            self.__exp.wait(5, [Mag], [waitFlag.stable])
            func()
        Mag.setField(Fstop)
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
