import platform
from tkinter import Tk, Label
from functools import lru_cache
from tkinter.filedialog import askopenfilename, asksaveasfilename

class SystemCalls:
    def __init__(self):
        pass

    @lru_cache
    def getOS(self) -> str:
        return platform.system().lower()

    def askPath(self, *args, **kwargs) -> str:
        root = Tk()
        root.withdraw()
        path = askopenfilename(*args, **kwargs)
        root.destroy()
        if path == None or path == ' ' or path == '':
            return None
        return path

    def askSave(self, *args, **kwargs) -> str:
        root = Tk()
        root.withdraw()
        path = asksaveasfilename(*args, **kwargs)
        root.destroy()
        if path == None or path == ' ' or path == '':
            return None
        return path
