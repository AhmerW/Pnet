import tkinter as tk
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

    def question(self, title, text):
        self.withdraw()
        res = mb.askquestion(title, text)
        self.destroy()
        return res
