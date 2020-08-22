import typing
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

class SimpleDialogs(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("300x300")

    def success(self, title, text):
        self.withdraw()
        res = mb.showinfo(title, text)
        self.destroy()
        return res

    def warning(self, title, text):
        self.withdraw()
        res = mb.showwarning(title, text)
        self.destroy()
        return res

    def question(self, title : str, text : str) -> str:
        self.withdraw()
        res = mb.askquestion(title, text)
        self.destroy()
        return res

    def getInput(self, title : str, func : typing.Callable, text : str, btext : str = "confirm"):
        ttk.Label(self, text=text).pack(fill="x")
        e = ttk.Entry(self)
        e.pack(fill="x")
        ttk.Button(self, text=btext, command=lambda : func(e.get())).pack(fill="x")
