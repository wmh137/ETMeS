import time, threading, sys, os
from typing import List, Union
import pyvisa as visa
from .instruments.ins import ins, waitFlag

def checkFile(name: str):
    if os.path.exists(name):
        base_name, extension = os.path.splitext(name)
        index = 1
        while True:
            newname = f"{base_name}.{index}{extension}"
            if not os.path.exists(newname):
                return newname
            index += 1
    else:
        return name

class exp():
    '''
    Attributes
    ----------
        instruments : List[ins]
            list of instruments
        dataFile : str
            name of data file without extensition name
    '''
    def __init__(self, instruments: List[ins], dataFile: Union[str, None]=""):
        self.__rm = visa.ResourceManager()
        self.instruments = []
        for ins in instruments:
            self.__addIns(ins)
        self.__t0 = time.time()
        self.__t = time.time()
        self.__interval = 0.3
        self.__log = open(".log", "a")
        if dataFile == None:
            self.f = None
        else:
            if dataFile == "":
                dataFile = "data"+time.strftime("%Y%m%d_%H%M%S", time.localtime())+".dat"
            else:
                dataFile = checkFile(dataFile+".dat")
            self.f = open(dataFile, "w")
        self.__flag = ""
        self.__setpoint = ""
        self.__start()
    def __addIns(self, ins: ins):
        if ins.visa:
            ins.res = self.__rm.open_resource(ins.address)
        else:
            ins.open()
        self.instruments.append(ins)
        ins.insInit()
    def __logWrite(self, log: str):
        self.__log.write(log)
        self.__log.flush()
    def __start(self):
        nameStr = 10*" "+"|"
        fHeader = "time"
        for ins in self.instruments:
            nameStr += ins.name2str()+"|"
            for var in ins.nowName:
                fHeader += f", {ins.name}_{var}"
        print(f"{nameStr}\n\n\n\n", end='')
        self.__logWrite(f"{self.__t:f}")
        if self.f != None:
            self.f.write(fHeader+"\n")
            self.f.flush()
            self.__logWrite(f" {self.f.name}\n")
        else:
            self.__logWrite("\n")
    def stop(self):
        '''stop all instruments'''
        for ins in self.instruments:
            ins.stop()
            if ins.visa:
                ins.res.close()
            else:
                ins.close()
        self.__rm.close()
        self.f.close()
    def setInterval(self, t: float):
        self.__interval = t
    def setFlag(self, flag: str):
        self.__flag = flag
    def __refreshNow(self):
        threads = []
        for ins in self.instruments:
            th = threading.Thread(target=ins.getNow)
            th.setDaemon(True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()
        self.__t = time.time()
    def refresh(self):
        '''refresh the current states of the instruments'''
        flagStr = 6*" "+"FLAG|"
        setpointStr = 2*" "+"SETPOINT|"
        nowStr = 7*" "+"NOW|"
        for ins in self.instruments:
            flagStr += ins.flag2str()+"|"
            setpointStr += ins.setpoint2str()+"|"
        flagStr += f" {self.__flag:<20s}"
        setpointStr += f" {self.__setpoint:<20s}"
        self.__refreshNow()
        for ins in self.instruments:
            nowStr += ins.now2str()+"|"
            if ins.log[0]:
                self.__logWrite(f"{self.__t:f} {ins.address:s} {ins.name:s}: {ins.log[1]:s}\n")
                ins.log[0] = False
        sys.stdout.write("\x1b[3A") # Powershell on Windows 7 does not support ANSI escape codes
        printStr = f"{flagStr}\n{setpointStr}\n{nowStr} {f'{self.__t-self.__t0:>.2f}s':<20s}\n"
        print(printStr, end="")
    def record(self):
        '''record the current states of the instruments'''
        if self.f == None:
            self.__flag = "WARNING: record failed"
            return
        self.f.write(f"{self.__t:.3f}")
        for ins in self.instruments:
            self.f.write(f",{ins.now2record()}")
        self.f.write("\n")
        self.f.flush()
    def wait(self, t: float, inss: List[ins], flags: List[waitFlag]):
        '''wait t (seconds) after all instruments reach their setpoints/targets'''
        self.__flag = "WAIT FOR "+' '.join([ins.name for ins in inss])
        reached = len(inss)*[False]
        t0 = time.time()
        t1 = 0
        while True:
            self.refresh()
            for i in range(len(inss)):
                if flags[i] == waitFlag.none:
                    reached[i] = True
                elif flags[i] == waitFlag.stable:
                    reached[i] = inss[i].reach(flags[i])
                else:
                    reached[i] = reached[i] or inss[i].reach(flags[i])
            if all(reached):
                t1 = time.time()
                self.__flag = f"WAIT {t-t1+t0:.0f}s"
            else:
                t0 = time.time()
                self.__flag = "WAIT FOR "+' '.join([ins.name for ins in inss])
            if t1 - t0 > t:
                break
            time.sleep(self.__interval)
        self.__flag = ""
    def standby(self):
        '''maintain the current states of the instruments'''
        self.__flag = "STANDBY"
        self.__logWrite(f"{self.__t:f} STANDBY\n")
        while True:
            self.refresh()
            time.sleep(self.__interval)
