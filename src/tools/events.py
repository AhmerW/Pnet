import os
import tkinter as tk
from tkinter import ttk
from functools import partial
from tkinter.filedialog import askopenfilename
from tools.chat import Chat
from tools.pcn import PriateConnection
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
            code = self.pnet.network.addFile(path)
            SimpleDialogs().success("Success", "Your file has been shared.\nOthers can now download the file if you're connected to the network.\n\nFile Code: {0}".format(code))
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
    def privateConnection(self):
        Dialogs(title="Connection details").createIputs(
            lambda ip, port : PriateConnection(ip, port).start(),
            "Connect",
            [
                {"label": "Enter ip address", "entry": " "},
                {"label": "Port", "entry": "9989"}
            ]
        )
