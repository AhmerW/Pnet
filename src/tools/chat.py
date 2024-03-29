import socket
import threading
import tkinter as tk
from tkinter import ttk
from tools.security.gen import randstr
from tools.dialogs import SimpleDialogs, Dialogs

MD = {'start': 1, 'join': 0}

class Chat(threading.Thread):
    """Chat class for both server & client"""
    def __init__(self, mode, ip="localhsot"):
        super(Chat, self).__init__()
        self.hostname, self.port = ip, 9993
        self.mode = mode # start or join
        self.code = None
        self.running = False

        ## socket object ##
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ## data ##
        self.username = self.default = 'Anonymous'
        self.clients = []
        self.total = 0
        self.max_connections = 1


    def createWindow(self):
        """Creates the chat window"""
        ## text field ##
        self.textf = tk.Text(self.window)
        self.textf.pack(expand=True, fill="both")
        self.textf.configure(state=tk.DISABLED)

        ## message entry ##
        self.messages = tk.StringVar()
        self.inpf = ttk.Entry(self.window, text=self.messages)


        ## scrollbar ##
        self.scrollb = ttk.Scrollbar(self.textf)
        self.scrollb.pack(side="right", fill="y")
        self.scrollb.config(command=self.textf.yview)
        self.textf.configure(yscrollcommand=self.scrollb.set)

        ## frame window ##
        self.frame = ttk.Frame(self.window)
        def func(args):
            data = self.inpf.get()
            if not data.strip():
                return
            msg = '[{0}] {1}'.format(self.username, data)
            if not MD[self.mode]: # not server:
                self.sock.send(msg.encode('utf-8'))
            else: # server
                self.sendToAll(msg.encode('utf-8'))
            self.addMsg(msg)

        self.inpf.bind("<Return>", func)
        self.frame.pack()
        if MD[self.mode]:
            details = lambda : SimpleDialogs().success(
                "Chat information",
                "Listening IP: {0}\nListening Port: {1}\nYour username: {2}\nMaximum allowed connections: {3}\nTotal connected: {4}".format(
                    self.hostname,
                    self.port,
                    self.username,
                    self.max_connections,
                    len(self.clients)
                )
            )
            ttk.Button(self.window, text="Chat details", command=details).pack(side="bottom", fill="x")
        self.inpf.pack(side="bottom", fill="x", ipady=20)

    def addMsg(self, msg):
        """Adds a new message into the text widget"""
        ## get username
        if ':&:' in msg:
            username = msg.split(':&:')[0]
            if not username.strip():
                username = self.default
            msg = '[{0}] {1}'.format(username, msg[len(username)+3:-1])


        ## configure text field ##
        self.textf.configure(state=tk.NORMAL)
        self.textf.insert(tk.INSERT, '{0}\n'.format(msg))

        self.inpf.delete(0, tk.END)
        self.textf.configure(state=tk.DISABLED)
        self.textf.see(tk.END)


    def start(self):
        """Starts the 'connect to server' process (client side)"""
        if not self.sock:
            return
        if not hasattr(self.sock, 'send'):
            return
        ## send information ##
        text = "{0}|{1}".format(self.username, self.code)
        self.sock.send(text.encode('utf-8'))
        res = self.sock.recv(2080).decode('utf-8')

        ## check if code is right ##
        if res == 'false':
            self.sock.close()
            return SimpleDialogs().warning(
                "Error",
                "Invalid chat room code '{0}'".format(self.code)
            )
        ## loop #
        connected = True
        try:
            while connected:
                data = self.sock.recv(4080).decode('utf-8')
                self.addMsg(data)
        except ConnectionError:
            connected = False

    def sendToAll(self, msg, c = None):
        """Sends a message to all clients connected (server)"""
        if not isinstance(msg, bytes):
            msg = msg.encode('utf-8')
        for client in self.clients:
            if client != self.sock and client != c:
                client.send(msg)


    def listen(self):
        """Starts listening for incoming clients (server)"""
        try:
            self.sock.listen()
            while self.running:
                if self.max_connections <= self.total:
                    break
                c, addr = self.sock.accept()
                self.clients.append(c)
                self.total += 1
                threading.Thread(
                    target=self.handleClient,
                    args=(c,)
                ).start()
            return
        except OSError:
            return

    def handleClient(self, con):
        """Handles a new connected client, this function runs in its own thread."""
        ## get data ##
        connected = True
        username, code = con.recv(2080).decode('utf-8').split('|')

        ## validate code ##
        if not code.strip() == self.code.strip():
            con.send('false'.encode('utf-8'))
            return con.close()
        con.send('true'.encode('utf-8'))
        msg = "'{0}' has connected to this chat!".format(username)
        self.addMsg(msg)
        self.sendToAll(msg)

        ## main loop ##
        while connected:
            try:
                msg = con.recv(4080).decode('utf-8')
                self.addMsg(msg)
                self.sendToAll(msg, con)
            except Exception:
                if hasattr(con, 'close'):
                    con.close()
                if con in self.clients:
                    self.clients.remove(con)
                connected = False

    def run(self, autocon : bool = False, *args):
        def closed():
            ## create the window ##
            self.window = tk.Toplevel()
            self.window.geometry("500x500")
            self.createWindow()
            self.window.title("Pnet chat room - Code: {0} | Your username: {1}".format(self.code, self.username))
            self.window.mainloop()
            return
        def processUsername(username):
            if len(username) >= 20:
                username = username[0:19]
            if not username.strip():
                username = self.default
            return username


        self.running = True
        def func(maxc, username):
            self.max_connections = int(maxc) if maxc.isdigit() else 1
            self.username = processUsername(username)
        if MD[self.mode]:
            if autocon:
                closed()
                func(*args)
            else:
                Dialogs(onclose=closed).createIputs(
                    func,
                    "start",
                    [
                        {"label": "Maximum amount of people allowed in this chat", "entry": str(self.max_connections)},
                        {"label": "Chose a username", "entry": " "}
                    ],
                )
            self.code = randstr(6) # new code
            try:
                self.sock.bind((self.hostname, self.port)) # bind server
            except Exception as e:
                print("Exception ", e)
                self.port += 1
                self.run(True, self.max_connections, self.username)
            threading.Thread(target=self.listen).start() # start listening

            return
        else:
            def func(ip, port, code, username):
                try:
                    self.username = processUsername(username)
                    self.code = code
                    port = int(port) if port.isdigit() else self.port

                    self.sock.connect((ip, port))
                    threading.Thread(target=self.start).start()

                except Exception as e:
                    SimpleDialogs().warning(
                        "Error",
                        "Could not connect on {0}, {1}.\n\n[Error Code {2}]".format(
                            ip,
                            port,
                            e.__class__.__name__
                        )

                    )

            if autocon:
                closed()
                func(*args)
            else:
                Dialogs(onclose=closed).createIputs(
                    func,
                    "Connect",
                    [
                        {"label": "Type in the host IP address or Host user-ID", "entry": " "},
                        {"label": "Type in the host PORT. Defaults to 9989", "entry": "9993"},
                        {"label": "Type in the chat room code", "entry": " "},
                        {"label": "Chose a username", "entry": " "}
                    ],
                )
            return
