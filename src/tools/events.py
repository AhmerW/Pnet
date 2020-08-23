import os
import tkinter as tk
from tkinter import ttk
from functools import partial
from tkinter.filedialog import askopenfilename
from tools.connections import Chat
from tools.systemcalls import SystemCalls
from tools.dialogs import SimpleDialogs, Dialogs



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
                SimpleDialogs().warning("Error", "Failed to get path")
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
            def func(*args):
                self.pnet.connector.connect(*args)

            Dialogs().createIputs(
                func,
                "Connect",
                [
                    {"label": "Type in the host IP address or User ID", "entry": " "},
                    {"label": "Type in the host PORT. Defaults to 9989", "entry": "9989"}
                ]
            )
        elif button.startswith('chat'):
            c = Chat(button.split('_')[-1], self.pnet.entry_ip.get())
            self.pnet.chats.append(c)
            c.run()


    def mainWindow(self, buttons : dict):
        top = tk.Toplevel(self.pnet)
        top.geometry("500x500")
        top.resizable(0, 0)


        ## create buttons ##
        for name, arg in buttons.items():
            b = ttk.Button(
                top,
                text=name,
                command = partial(self.onClick_event, arg)
            ).pack(anchor="n", side="top", fill="both")



        ## exit button ##
        ex_st = ttk.Style().configure('exit.TButton',foreground='red')
        button_exit = ttk.Button(top, style='exit.TButton', text="Exit", command=top.destroy, width=30)
        button_exit.pack(side="right", anchor="se")
        top.mainloop()

    def fileWindow(self):
        self.mainWindow(
            {
                'Share a file': 'file_share',
                'Download a file': 'file_download'
            }
        )

    def chatWindow(self):
        self.mainWindow(
            {
                'Create a chat room': 'chat_start',
                'Join a chat room': 'chat_join'
            }
        )
