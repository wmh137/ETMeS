import pyvisa as visa
from .instruments.ins import ins, waitFlag
import time, threading, sys

class em():
    def __init__(self):
        self.__rm = visa.ResourceManager()
        self.__instruments = []
        self.__t0 = time.time()
        self.__start = False
        self.__interval = 0.3
        self.__f = None
        self.__log = open(".log", "w")
    def addInstrument(self, ins: ins):
        if ins.visa:
            ins.res = self.__rm.open_resource(ins.address)
        else:
            ins.open()
        self.__instruments.append(ins)
        ins.insInit()
    def t(self):
        return time.time()-self.__t0
    def start(self):
        nameStr = 20*" "+"|"
        fHeader = "time"
        for ins in self.__instruments:
            nameStr += ins.name2str()+"|"
            for var in ins.nowName:
                fHeader += f", {ins.name}_{var}"
        print(f"{nameStr}\n\n\n\n", end='')
        self.__f = open("data"+time.strftime("%Y%m%d_%H%M%S", time.localtime())+".dat", "w")
        self.__f.write(fHeader+"\n")
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
    def refreshNow(self):
        threads = []
        for ins in self.__instruments:
            th = threading.Thread(target=ins.getNow)
            th.setDaemon(True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()
    def refresh(self):
        if not self.__start:
            print("ETMeS is not running!", end="")
            exit()
        flagStr = 16*" "+"FLAG|"
        setpointStr = 12*" "+"SETPOINT|"
        nowStr = 17*" "+"NOW|"
        for ins in self.__instruments:
            flagStr += ins.flag2str()+"|"
            setpointStr += ins.setpoint2str()+"|"
        self.refreshNow()
        for ins in self.__instruments:
            nowStr += ins.now2str()+"|"
        sys.stdout.write("\x1b[3A")
        print(f"{flagStr}\n{setpointStr}\n{nowStr}{self.t():>19.2f}s")
        self.__log.write(f"{nowStr}{self.t():>19.2f}s\n")
    def record(self):
        self.__f.write(f"{self.t():.3f}")
        for ins in self.__instruments:
            self.__f.write(f",{ins.now2record()}")
        self.__f.write("\n")
        self.__f.flush()
    def wait(self, t: float, inss: list, flags: list):
        '''wait(time, [ins1, ins2, ...], [waitFlag1, waitFlag2, ...])'''
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
                else:# not stable
                    reached[i] = reached[i] or inss[i].reach(flags[i])
            if all(reached):
                t1 = time.time()
            else:
                t0 = time.time()
            if t1 - t0 > t:
                break
            time.sleep(self.__interval)
    '''def crossWait(self, inss: list, dir: direction, t: float):
        flag = len(inss)*[False]
        while True:
            self.refresh()
            for i in range(len(inss)):
                flag[i] = inss[i].crossReach(dir)
            if all(flag):
                break
            time.sleep(self.__interval)
        t0 = time.time()
        while time.time() - t0 < t:
            self.refresh()'''
