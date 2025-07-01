from abc import ABC, abstractmethod
from typing import Any
import pyvisa as visa

class insio():
    res: Any
    @abstractmethod
    def write(self, cmd: str):
        pass
    @abstractmethod
    def query(self, cmd: str) -> str:
        return ""
    @abstractmethod
    def close(self):
        pass

class insioNone(insio):
    def write(self, cmd: str):
        pass
    def query(self, cmd: str) -> str:
        return ""
    def close(self):
        pass

class insioVisaMsg(insio):
    res: visa.resources.MessageBasedResource
    def write(self, cmd: str):
        self.res.write(cmd)
    def query(self, cmd: str) -> str:
        return self.res.query(cmd)
    def close(self):
        self.res.close()
