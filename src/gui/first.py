import tkinter as tk
from tkinter import ttk
from ttkthemes import themed_tk as window

class MainWindow(window.ThemedTk):
    def __init__(self, *args, **kwargs):
        ## window objects ##
        window.ThemedTk.__init__(self, *args, **kwargs)
        self.width, self.height = 900, 600
        self.first = True

        ## configure window ## 
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        self.geometry("{0}x{1}".format(self.width, self.height))
        self.title("Pnet")
        self.set_theme("radiance")

        ## data ##
        self.buttons = ['Connect', 'chat', 'file sharing', 'create a connection']
        self.button_objects = []
        self.connected = False


        ## call methods ##
        self.createMenu()
        self.createTab()
        for button in self.buttons: self.createButton(button)

    def onClose(self):
        pass

    def onClick(self, button):
        pass

    def onEnter(self, button):
        pass

    def onLeave(self, button):
        pass

    def createTab(self):
        ## tab widget  ##
        self.tab = ttk.Notebook(self, width=self.width, height=100, name="settings")
        self.tab.pack(side="bottom", anchor="sw", fill="both")


        ## status tab ##
        self.tab_status = ttk.Frame(self.tab, width=self.width, height=1000)
        self.tab_status.pack(fill="both", expand=1, anchor="se")
        self.tab.add(self.tab_status, text="Status")

        self.label_connect = ttk.Label(self.tab_status, text="Disconnected from the network")
        self.label_connect.pack(anchor="w")

        self.label_total = ttk.Label(self.tab_status, text="Total connections established: 0")
        self.label_total.pack(anchor="w")

        ## settings tab ##
        self.tab_settings = ttk.Frame(self.tab, width=self.width, height=100)
        self.tab_settings.pack(fill="both", expand=1, anchor="se")
        self.tab.add(self.tab_settings, text="Settings")



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


    def createMenu(self):
        ## main menu ##
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        ## file menu ##
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_separator()
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        ## [file menu] exit ##
        self.exmenu = tk.Menu(tearoff=0)
        self.filemenu.add_cascade(label="Exit", menu=self.exmenu)

        ## [exit] this application ##
        self.exmenu.add_cascade(label="Exit this program", command=self.quit)

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    MainWindow().show()
