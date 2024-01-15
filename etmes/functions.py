import pyvisa as visa
from .instrument import *
import time, threading
import sys

class em():
    def __init__(self):
        self.__rm = visa.ResourceManager()
        self.__instruments = []
        self.__t0 = time.time()
        self.__start = False
        self.__f = None
        self.__log = open(".log", "w")
    def addInstrument(self, ins: ins):
        ins.res = self.__rm.open_resource(ins.address)
        self.__instruments.append(ins)
        ins.insInit()
    def t(self):
        return time.time()-self.__t0
    def start(self):
        nameStr = ""
        fHeader = "time"
        for ins in self.__instruments:
            nameStr += ins.name2str()
            for var in ins.nowName:
                fHeader += f", {ins.name}_{var}"
        print(f"{nameStr}\n\n\n\n", end='')
        self.__f = open("data"+time.strftime("%Y%m%d_%H%M%S", time.localtime())+".dat", "w")
        self.__f.write(fHeader+"\n")
        self.__start = True
    def stop(self):
        for ins in self.__instruments:
            ins.stop()
        self.__f.close()
        self.__start = False
    def refrashNow(self):
        threads = []
        for ins in self.__instruments:
            th = threading.Thread(target=ins.getNow)
            th.setDaemon(True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()
    def refrash(self):
        if not self.__start:
            print("ETMeS is not running!", end="")
            exit()
        flagStr = ""
        setpointStr = ""
        nowStr = ""
        for ins in self.__instruments:
            flagStr += ins.flag2str()
            setpointStr += ins.setpoint2str()
        self.refrashNow()
        for ins in self.__instruments:
            nowStr += ins.now2str()
        sys.stdout.write("\x1b[3A")
        print(f"{flagStr}\n{setpointStr}\n{nowStr}{self.t():>19.2f}s")
        self.__log.write(f"{nowStr}{self.t():>19.2f}s\n")
    def record(self):
        self.__f.write(f"{self.t():.3f}")
        for ins in self.__instruments:
            self.__f.write(f",{ins.now2record()}")
        self.__f.write("\n")
    def wait(self, inss: list):
        flag = len(inss)*[False]
        while True:
            self.refrash()
            for i in range(len(inss)):
                flag[i] = inss[i].reach()
            if all(flag):
                break
            time.sleep(0.5)
