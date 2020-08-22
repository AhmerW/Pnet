import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tools.systemcalls import SystemCalls
from tools.dialogs import SimpleDialogs



class Events:
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
                return
            res = SimpleDialogs().question(
            "Confirm", "You sure you want to share this file? {0}\nAn unique code will be generated which you can share to others.\nAnyone who knows your ip address and the code can download this file.".format(
            path
            )
            )
            if res == 'no':
                return
            self.pnet.network.addFile(path)
            print(self.pnet.network.paths)
        elif button == 'file_download':
            ## window ##
            win = tk.Tk()
            ## ip ##
            ttk.Label(win, text="Type in the host IP address or User ID").pack()
            e1 = ttk.Entry(win)
            e1.pack(fill="x")
            ## port ##
            ttk.Label(win, text="Type in the host PORT. Defaults to 9989").pack()
            e2 = ttk.Entry(win)
            e2.insert(0, "9989")
            e2.pack(fill="x")

            def func():
                self.pnet.connector.connect(e1.get(), e2.get())
                win.destroy()
            ttk.Button(win, text="Connect", command=func).pack()

    def fileWindow(self):
        top = tk.Toplevel(self.pnet)
        top.geometry("500x500")
        top.resizable(0, 0)
        ypos = 0


        ## share a file buton ##
        b1 = ttk.Button(top, text="share a file", command=lambda : self.onClick_event("file_share"))
        b1.pack(anchor="n", side="top", fill="both")

        self.l1 = ttk.Label(top, text="")
        self.l1.pack(anchor="center")
        self.l1.place(x=190, y=40)

        ## download a file button
        b2 = ttk.Button(top, text="Download a file", command=lambda : self.onClick_event("file_download"))
        b2.pack(anchor="n", side="top", fill="both")


        ## exit button ##
        ex_st = ttk.Style().configure('exit.TButton',foreground='red')
        button_exit = ttk.Button(top, style='exit.TButton', text="Exit", command=top.quit, width=30)
        button_exit.pack(side="right", anchor="se")
        top.mainloop()

    def chatWindow(self):
        top = tk.Toplevel(self.pnet)
        top.geometry("500x500")
        top.resizable(0, 0)


        ## share a file buton ##
        b1 = ttk.Button(top, text="Create a chat", command=lambda : self.onClick_event("chat_create"))
        b1.pack(anchor="n", side="top", fill="both")


        ## download a file button
        b2 = ttk.Button(top, text="Join a chat", command=lambda : self.onClick_event("chat_join"))
        b2.pack(anchor="n", side="top", fill="both")


        ## exit button ##
        ex_st = ttk.Style().configure('exit.TButton',foreground='red')
        button_exit = ttk.Button(top, style='exit.TButton', text="Exit", command=top.quit, width=30)
        button_exit.pack(side="right", anchor="se")
        top.mainloop()
