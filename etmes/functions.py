import time, threading, sys
from typing import List
import pyvisa as visa
from .instruments.ins import ins, waitFlag

class etmes():
    def __init__(self):
        self.__rm = visa.ResourceManager()
        self.__instruments = []
        self.__t0 = time.time()
        self.__t = time.time()
        self.__start = False
        self.__interval = 0.3
        self.__f = None
        self.__log = open(".log", "a")
        self.__flag = ""
        self.__setpoint = ""
    def addInstrument(self, ins: ins):
        if ins.visa:
            ins.res = self.__rm.open_resource(ins.address)
        else:
            ins.open()
        self.__instruments.append(ins)
        ins.insInit()
    def start(self):
        nameStr = 10*" "+"|"
        fHeader = "time"
        for ins in self.__instruments:
            nameStr += ins.name2str()+"|"
            for var in ins.nowName:
                fHeader += f", {ins.name}_{var}"
        print(f"{nameStr}\n\n\n\n", end='')
        self.__f = open("data"+time.strftime("%Y%m%d_%H%M%S", time.localtime())+".dat", "w")
        self.__f.write(fHeader+"\n")
        self.__f.flush()
        self.__log.write(f"{self.__t:f} {self.__f.name:s}\n")
        self.__start = True
    def stop(self):
        for ins in self.__instruments:
            ins.stop()
            if ins.visa:
                ins.res.close()
            else:
                ins.close()
        self.__rm.close()
        self.__f.close()
        self.__start = False
    def setInterval(self, t: float):
        self.__interval = t
    def setFlag(self, flag: str):
        self.__flag = flag
    def refreshNow(self):
        threads = []
        for ins in self.__instruments:
            th = threading.Thread(target=ins.getNow)
            th.setDaemon(True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()
        self.__t = time.time()
    def refresh(self):
        if not self.__start:
            print("ETMeS is not running!", end="")
            exit()
        flagStr = 6*" "+"FLAG|"
        setpointStr = 2*" "+"SETPOINT|"
        nowStr = 7*" "+"NOW|"
        for ins in self.__instruments:
            flagStr += ins.flag2str()+"|"
            setpointStr += ins.setpoint2str()+"|"
        flagStr += f" {self.__flag:<20s}"
        setpointStr += f" {self.__setpoint:<20s}"
        self.refreshNow()
        for ins in self.__instruments:
            nowStr += ins.now2str()+"|"
        sys.stdout.write("\x1b[3A") # Powershell on Windows 7 does not support ANSI escape codes
        printStr = f"{flagStr}\n{setpointStr}\n{nowStr} {f'{self.__t-self.__t0:>.2f}s':<20s}\n"
        print(printStr, end="")
        for ins in self.__instruments:
            if ins.lognow:
                self.__log.write(f"{self.__t:f} {ins.address:s} {ins.name:s} {ins.log:s}\n")
    def record(self):
        self.__f.write(f"{self.__t:.3f}")
        for ins in self.__instruments:
            self.__f.write(f",{ins.now2record()}")
        self.__f.write("\n")
        self.__f.flush()
    def wait(self, t: float, inss: List[ins], flags: list):
        '''wait(time, [ins1, ins2, ...], [waitFlag1, waitFlag2, ...])'''
        self.__flag = "WAITING "+' '.join([ins.name for ins in inss])
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
                self.__flag = "WAITING "+' '.join([ins.name for ins in inss])
            if t1 - t0 > t:
                break
            time.sleep(self.__interval)
        self.__flag = ""
    def standby(self):
        self.__flag = "STANDBY"
        self.__log.write(f"{self.__t:f} STANDBY\n")
        self.__log.flush()
        while True:
            self.refresh()
            time.sleep(self.__interval)
