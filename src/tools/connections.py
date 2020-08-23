import socket
import threading
import tkinter as tk
from tkinter import ttk
from tools.database.cdb import Cdb
from tools.security.gen import randstr
from tools.dialogs import SimpleDialogs, Dialogs
from tools.systemcalls import SystemCalls

class Listener(threading.Thread):
    def __init__(self, con, db, pnet):
        super(Listener, self).__init__()
        self.listening = True
        self.pnet = pnet
        self.con = con
        self.db = db
        self.connections_count = 0

    def handleFiletransfer(self, client):
        connected = True
        client.send(self.pnet.uid.encode('utf-8')) # uid
        client.send(str(len(self.pnet.network.paths)).encode('utf-8')) # files
        while connected:
            try:
                command = client.recv(4080).decode('utf-8')
                if ':' in command:
                    name, data = command.split(':')
                    if name == 'download_file':
                        res = self.pnet.network.getPath(data)
                        if not res:
                            client.send('false'.encode('utf-8'))
                            return
                        fdata = self.pnet.network.getData(res)
                        if not fdata:
                            client.send('false'.encode('utf-8'))
                            return
                        amount = len(fdata)
                        client.send('true'.encode('utf-8'))
                        status = client.recv(2080).decode('utf-8')
                        if status == 'continue':
                            client.send(str(amount).encode('utf-8'))
                            for data in fdata:
                                if not isinstance(data, bytes):
                                    data = data.encode('utf-8')
                                client.send(data)


            except ConnectionError:
                connected = False
                self.connections_count -= 1
                self.pnet.updateStatus(self.con)
        return

    def run(self):
        self.con.listen()
        while self.listening:
            try:
                obj, addr = self.con.accept()
                self.connections_count += 1
                mode = obj.recv(2080).decode('utf-8')
                if mode == 'file':
                    threading.Thread(
                        target=self.handleFiletransfer,
                        args=(obj,)
                    ).start()
                self.pnet.updateStatus(self.connections_count)
            except OSError:
                break

    def stop(self):
        self.listening = False
        return

class FileTransfer(threading.Thread):
    def __init__(self, cdb, hostname, port=9989):
        super(FileTransfer, self).__init__()
        self.hostname, self.port = hostname, port
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.db = cdb
        self.connected = True

    def connect(self):
        try:
            self.con.connect((self.hostname, self.port))
            self.connected = True
            return True
        except Exception:
            self.connected = False
            return False

    def run(self):
        if not self.connected:
            return
        self.con.send('file'.encode('utf-8'))
        self.uid = self.con.recv(2080).decode('utf-8')
        self.db.addUid(self.uid, self.hostname)
        self.files = self.con.recv(4080).decode('utf-8')

class Chat():
    _md = {'start': 1, 'join': 0}
    def __init__(self, mode, ip="localhsot"):
        #Super(Chat, self).__init__()
        self.hostname, self.port = ip, 9992
        self.mode = mode # start or join
        self.code = None
        self.running = False

        ## objects ##
        self.window = tk.Tk()
        self.window.deiconify()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ## data ##
        self.username = 'Anonymous'
        self.clients = []
        self.total = 0
        self.max_connections = 1


    def createWindow(self):


        ## text field ##
        self.textf = tk.Text(self.window)
        self.textf.pack(expand=True, fill="both")
        self.textf.configure(state=tk.DISABLED)

        ## message entry ##
        self.messages = tk.StringVar()
        self.inpf = ttk.Entry(self.window, text=self.messages)
        self.inpf.pack(side="bottom", fill="x")
        self.inpf.focus()

        ## scrollbar ##
        self.scrollb = ttk.Scrollbar(self.textf)
        self.scrollb.pack(side="right", fill="y")
        self.scrollb.config(command=self.textf.yview)
        self.textf.configure(yscrollcommand=self.scrollb.set)

        ## frame window ##
        self.frame = ttk.Frame(self.window)
        self.inpf.bind(
            "<Return>", lambda *a : self.addMsg(
                '[{0}] {1}'.format(self.username, self.inpf.get()),
                True
                )
        )
        self.frame.pack()

    def addMsg(self, msg, send=True):
        if ':&:' in msg:
            username = msg.split(':&:')[0]
            if username == '' or username == ' ' or not username:
                username = 'Anonymous'
            msg = '[{0}] {1}'.format(username, msg[len(username)+3:-1])


        ## configure text field ##
        self.textf.configure(state=tk.NORMAL)
        self.textf.insert(tk.INSERT, '{0}\n'.format(msg))

        self.inpf.delete(0, tk.END)
        self.textf.configure(state=tk.DISABLED)
        self.textf.see(tk.END)

        if send:
            self.sendToAll(msg)

    def start(self):
        if not hasattr(self.sock, 'send'):
            return
        self.sock.send(self.code.encode('utf-8'))
        res = self.sock.recv(2080).decode('utf-8')
        if res == 'false':
            self.sock.close()
            return SimpleDialogs().warning(
                "Error",
                "Invalid chat room code '{0}'".format(self.code)
            )

    def sendToAll(self, msg, c = None):
        if not isinstance(msg, bytes):
            msg = msg.encode('utf-8')
        for client in self.clients:
            if client != self.sock and client != c:
                client.send(msg)


    def listen(self):
        try:
            self.sock.listen()
            while self.running:
                if self.max_connections <= self.total:
                    break
                c, addr = self.sock.accept()
                self.clients.append(c)
                self.total += 1
                print(addr)
                threading.Thread(
                    target=self.handleClient,
                    args=(c,)
                ).start()
            return
        except OSError:
            return

    def handleClient(self, con):
        connected = True
        while connected:
            try:
                msg = con.recv(4080).decode('utf-8')
                self.addMsg(msg, send=False)
                self.sendToAll(msg, con)
            except Exception as e:
                print("disconnect ", e)
                if hasattr(con, 'close'):
                    con.close()
                if con in self.clients:
                    self.clients.remove(con)
                connected = False

    def run(self):
        def closed():
            print("Closed")
            self.window.title("Chat room - Code: {0}".format(self.code))
            self.window.mainloop()

        self.running = True
        self.createWindow()
        if Chat._md[self.mode]: # server
            def func(username):
                self.username = username
            Dialogs(onclose=closed).createIputs(
                func,
                "start",
                [
                    {"label": "Enter an username", "entry": " "}
                ],
            )
            self.code = randstr(6)
            self.sock.bind((self.hostname, self.port))
            threading.Thread(target=self.listen).start()
        else: # normal
            def func(ip, port, code, username):
                try:
                    self.username = userame
                    self.code = code
                    port = int(port) if port.isdigit() else self.port
                    self.sock.connect((ip, port))
                    self.start()
                except Exception as e:
                    return SimpleDialogs().warning(
                        "Error",
                        "Could not connect on {0}, {1}.\n\n[Error Code {2}]".format(
                            ip,
                            port,
                            e.__class__.__name__
                        )
                    )
            Dialogs(onclose=closed).createIputs(
                func,
                "Connect",
                [
                    {"label": "Type in the host IP address or User ID", "entry": " "},
                    {"label": "Type in the host PORT. Defaults to 9989", "entry": "9989"},
                    {"label": "Type in the chat room code", "entry": " "},
                    {"label": "Enter an username", "entry": " "}
                ],
            )




class Connections():
    def __init__(self, pnet):
        self.pnet = pnet
        self.ip, self.port = self.pnet.entry_ip.get(), 9989
        self.connected = False
        self.bindd = False
        ## objects ##
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener connection
        self.connection = None # connection to someone object
        self.attemptBind()
        self.db = Cdb()
        self.sysc = SystemCalls()
        self.listener = None

    def close(self):
        try:
            self.listener.stop()
            if self.bindd:
                self.con.close()
        except (OSError, AttributeError):
            return

    def attemptBind(self):
        try:
            self.con.bind((self.ip, self.port))
            self.pnet.entry_port.delete(0, tk.END)
            self.pnet.entry_port.insert(0, str(self.port))
        except Exception:
            self.port += 1
            self.attemptBind()

    def listen(self):
        if self.connected:
            self.connected = False
            self.listener.stop()
            return
        self.connected = True
        self.listener = Listener(self.con, self.db, self.pnet)
        self.listener.start()
        #print("Listener started on ip {0} and port {1}".format(self.ip, self.port))

    def connect(self, hostname, port):
        if hostname.isdigit(): # assuming user id was typed, since ip contains dots (not digit)
            res = self.db.resolveFromUid(hostname)
            print(self.db.connections)
            if not res:
                text = "Cant resolve IP from user ID.\nYou can't connect via User ID before connecting through the IP address at least once"
                return SimpleDialogs().warning("Error", text)
            hostname = res
        if port.isdigit():
            port = int(port)
        else:
            SimpleDialogs().warning("Error", "You failed to enter a valid port.\nChoosing port {0} instead".format(self.port))
            port = self.port
        self.connection = FileTransfer(self.db, hostname, port)
        if not self.connection.connect():
            return SimpleDialogs().warning("Error", "Could not connect to {0}, {1}".format(hostname, port))
        self.connection.start()
        ## download a file main window ##
        def startdw(code):
            self.connection.con.send(
                bytes(
                    'download_file:{0}'.format(code),
                    "utf-8"
                )
            )
            status = self.connection.con.recv(2080).decode('utf-8')
            if status == 'false':
                return SimpleDialogs().warning("Error", "Could not download file with the code {0}".format(code))
            path = self.sysc.askSave()
            try:
                with open(path, 'wb+') as f:
                    self.connection.con.send('continue'.encode('utf-8'))
                    amount = self.connection.con.recv(2080).decode('utf-8')
                    amount = int(amount) if amount.isdigit() else 1
                    pbl = int(amount/100)
                    for i in range(amount):
                        f.write(
                            self.connection.con.recv(4080)
                        )
                        self.pnet.pb["value"] += pbl
                        self.pnet.update_idletasks()
                self.pnet.pb["value"] = 100
                SimpleDialogs().success("Success", "The file has been download and saved at\n{0}".format(path))
                self.pnet.pb["value"] = 0
            except FileNotFoundError:
                self.connection.con.send('abort')

        SimpleDialogs().getInput(
            "Download menu",
            startdw,
            "Enter the code of the file you wish to download.",
            "Download file"
        )
