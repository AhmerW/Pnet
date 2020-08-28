import socket
import threading
import tkinter as tk
from tkinter import ttk
from tools.database.cdb import Cdb
from tools.security.gen import randstr
from tools.dialogs import SimpleDialogs, Dialogs
from tools.systemcalls import SystemCalls

class Listener(threading.Thread):
    def __init__(self, db, pnet):
        super(Listener, self).__init__()
        self.listening = True
        self.pnet = pnet
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = self.pnet.entry_ip.get(), self.pnet.entry_port.get()
        if self.port.isdigit():
            self.port = int(self.port)
        else:
            self.port = 9989

        self.db = db
        self.connections_count = 0
        self.attemptBind()

    def attemptBind(self):
        try:
            self.con.bind((self.ip, self.port))
            self.pnet.entry_port.delete(0, tk.END)
            self.pnet.entry_port.insert(0, str(self.port))
        except Exception:
            self.port += 1
            self.attemptBind()

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
    def handlePrivateConnection(self, client):
        pass

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
                elif mode == 'private_connection':
                    threading.Thread(
                        target=self.handlePrivateConnection,
                        args=(obj,)
                    )
                l = tk.Label(
                    self.pnet.status_frame_right,
                    text="New connection from {0}. Mode requested: {1}".format(addr, mode)
                )
                l.pack(side="right", anchor="n")
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



class Connections():
    def __init__(self, pnet):
        self.pnet = pnet
        self.connected = False
        self.bindd = False
        ## objects ##
        self.connection = None # connection to someone object
        self.db = Cdb()
        self.sysc = SystemCalls()
        self.listener = None

    def close(self):
        try:
            self.listener.stop()
        except (OSError, AttributeError):
            return


    def listen(self):
        if self.connected:
            self.connected = False
            self.listener.stop()
            return
        self.connected = True
        self.listener = Listener(self.db, self.pnet)
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
