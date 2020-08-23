import string
import pyperclip
import tkinter as tk
from tkinter import ttk
from ttkthemes import themed_tk as window
from tools.dialogs import SimpleDialogs
from tools.networking import Network
from tools.security.gen import randstr

PATHMENUTEXT = \
"""
Here is a list of all the files you have shared. If you want
to download this file on another computer, then start
with clicking the 'download a file' button under the file menu.
Then type in the ip address or the username (if saved) in the input box.
If that went alright then you can proceed with typing in the code
which belongs to that filename. List of all codes and file paths (locations)
are found below.
"""

class Table:
    def __init__(self, window : tk.Tk, table : list, copy=True):
        for i in range(len(table)):
            for j in range(len(table[0])):
                 if i == 0:
                     e = tk.Entry(window, width=30)
                 else:
                     e = ttk.Entry(window, width=30)
                 e.grid(row=i, column=j)
                 e.insert(tk.END, table[i][j])
                 e.configure(state=tk.DISABLED)
                 if copy and i != 0 and j == 0:
                     e.bind(
                        '<Button-1>', lambda *a, **kw : pyperclip.copy(
                            table[i][j]
                        )
                    )


class MainWindow(window.ThemedTk):
    def __init__(self, *args, **kwargs):
        ## window objects ##
        window.ThemedTk.__init__(self, *args, **kwargs)
        self.network = Network()
        self.width, self.height = 900, 600
        self.first = True
        self.uid_len = 12
        self.uid = randstr(self.uid_len, string.digits) ## option to save later so

        ## configure window ##
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        self.geometry("{0}x{1}".format(self.width, self.height))
        self.title("Pnet")
        self.set_theme("radiance")

        ## data ##
        self.buttons = ['Connect', 'Chat', 'File', 'Create a connection']
        self.button_objects = []
        self.chats = []
        self.connected = False
        self.showl_run = True


        ## call methods ##
        self.createMenu()
        self.createTab()
        self.createOthers()
        for button in self.buttons: self.createButton(button)

        ## uid label ##
        l = ttk.Label(self, text="User ID: {0}".format(self.uid))
        l.pack(anchor="s", side="bottom")
        l.place(y=350)


    def onClose(self):
        pass

    def onClick(self, button):
        pass

    def onEnter(self, button):
        pass

    def onLeave(self, button):
        pass

    def pathMenu(self):
        win = tk.Toplevel(self)
        win.title("Files shared")
        win.geometry("300x300")
        files = [("Code", "File location")]
        #ttk.Label(win, text=PATHMENUTEXT).grid()
        for k, v in self.network.paths.items():
            files.append(
                (k, v)
            )
        Table(win, files)
        win.mainloop()

    def createTab(self):
        ## tab widget  ##
        self.tab = ttk.Notebook(self, width=self.width, height=200, name="settings")
        self.tab.pack(side="bottom", anchor="sw", fill="both")

        #----------------#
        ## status tab ##
        #----------------#

        self.tab_status = ttk.Frame(self.tab, width=self.width, height=1000)
        self.tab_status.pack(fill="both", expand=1, anchor="se")
        self.tab.add(self.tab_status, text="Status")

        ## connect label ##
        self.label_connect = ttk.Label(self.tab_status, text="Disconnected from the network")
        self.label_connect.pack(anchor="w")

        ## total label ##
        self.label_total = ttk.Label(self.tab_status, text="Total connections established: 0")
        self.label_total.pack(anchor="w")

        self.button_shared = ttk.Button(
            self.tab_status,
            text="List of files shared",
            command = lambda : SimpleDialogs().warning("Error", "No files shared at the moment") if not self.network.paths else self.pathMenu()
        )
        self.button_shared.pack(anchor="sw")

        ## progress bar ##
        self.pb = ttk.Progressbar(
            self.tab_status,
            orient=tk.HORIZONTAL,
            mode="determinate",
            length=1000
        )
        self.pb.pack(anchor="se", side="right")

        #----------------#
        ## settings tab ##
        #----------------#
        self.tab_settings = ttk.Frame(self.tab, width=self.width, height=100)
        self.tab_settings.pack(fill="both", expand=1, anchor="se")
        self.tab.add(self.tab_settings, text="Settings")

        ## Frames ##
        ttk.Style().configure("Frame1.TFrame")

        frame_left = ttk.Frame(self.tab_settings, height=600, width=200, style="Frame1.TFrame")
        frame_left.pack(anchor="n", side="left", fill="y")

        frame_right = ttk.Frame(self.tab_settings, height=600, width=200, style="Frame1.TFrame")
        frame_right.pack(anchor="n", side="right", fill="y")

        ## combination button
        self.button_combinations = ttk.Button(
            frame_left,
            text="Code combination settings",
            command=self.network.savePaths
        ).pack(anchor="sw")

        ## save button
        self.buton_path_save = ttk.Button(
            frame_left,
            text="Save files for next time"
        ).pack(anchor="sw")

        ## reset button
        self.button_path_reset = ttk.Button(
            frame_left,
            text="Forget all saved files"
        ).pack(anchor="sw")

        ## save uid checkbox
        self.checkbox_save_uid_state = tk.IntVar()
        self.checkbox_save_uid = ttk.Checkbutton(
            frame_right,
            text="Save user ID for next time",
            variable=self.checkbox_save_uid_state,
            command=lambda : None
        ).pack(anchor="se")

        ## list of saved button
        def _showl():
            setattr(self, 'showl_run', False)
            top = tk.Toplevel()
            def _end():
                setattr(self, 'showl_run', True)
                top.destroy()
            top.protocol("WM_DELETE_WINDOW", _end)
            ttk.Label(
                top,
                text = '\n'.join(self.connector.db.connections.keys())
            ).pack()

        self.button_list = ttk.Button(
            frame_left,
            text="List of user ids saved in cache. (Previous connections)",
            command = lambda : SimpleDialogs().warning("Error", "No user ids saved in cache") \
                    if not self.connector.db.connections else _showl() if self.showl_run else None
        ).pack(anchor="sw")



        ## current listening ip ##
        l1 = ttk.Label(frame_right, text="Listening IP").pack(anchor="ne")

        self.entry_ip = ttk.Entry(frame_right)
        self.entry_ip.pack(anchor="ne")
        self.entry_ip.insert(0, "127.0.0.1")

        ## current listening port ##
        ttk.Label(frame_right, text="Listening port").pack(anchor="ne")
        self.entry_port = ttk.Entry(frame_right)
        self.entry_port.pack(anchor="e")
        self.entry_port.insert(0, "9989")




    def createButton(self, button):
        b = ttk.Button(
            self,
            width=25,
            text=button,
            command=lambda : self.onClick(button.replace(' ', '_').strip())
        )
        b.pack(
            side="right",
            anchor="ne",
            expand=False,
            fill="x"
        )
        self.button_objects.append(b)
        b.bind('<Enter>', lambda args: self.onEnter(b))
        b.bind('<Leave>', lambda args : self.onLeave(b))

    def createOthers(self):
        pass

    def createMenu(self):
        ## main menu ##
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        ## file menu ##
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_separator()
        self.menubar.add_cascade(label="Home", menu=self.filemenu)

        ## [file menu] exit ##
        self.exmenu = tk.Menu(tearoff=0)
        self.filemenu.add_cascade(label="Exit", menu=self.exmenu)

        ## [file menu] launch terminal ##
        self.cmdmenu = tk.Menu(tearoff=0)
        self.filemenu.add_cascade(label="Launch terminal version of pnet", menu=self.cmdmenu)

        ## [exit] this application ##
        self.exmenu.add_cascade(label="Exit this program", command=self.quit)

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    MainWindow().show()
