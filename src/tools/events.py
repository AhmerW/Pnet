import os
import tkinter as tk
from tkinter import ttk
from tools.systemcalls import SystemCalls

class EventWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(*args, **kwargs)


class Events():
    def __init__(self, pnet):
        self.pnet = pnet
        self.other_buttons = ['share a file']
        self.onClick_event = self.onClick
        self.sysc = SystemCalls()

    def onClick(self, button):
        if button == 'file_share':
            path = self.sysc.askPath()
            if not path:
                path = "Failed to get path"
            self.l1.configure(text=path)

    def fileWindow(self):
        top = tk.Toplevel()
        top.geometry("500x500")
        top.resizable(0, 0)
        ypos = 0





        ## share a file buton ##
        b1 = ttk.Button(top, text="share a file", command=lambda : self.onClick_event("file_share"))
        b1.pack(anchor="n", side="top", fill="both")
        b1.place(x=190, y=ypos)

        self.l1 = self.label_status = tk.Label(top, text="status",  fg="black", width=2000)
        self.l1.pack(anchor="center")
        self.l1.place(x=190, y=40)

        ## exit button ##
        ex_st = ttk.Style().configure('exit.TButton',foreground='red')
        button_exit = ttk.Button(top, style='exit.TButton', text="Exit", command=top.quit, width=30)
        button_exit.pack(side="right", anchor="se")


        top.mainloop()
