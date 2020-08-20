import socket
import threading
from tools.database.cdb import Cdb

class Listener(threading.Thread):
    def __init__(self, con, db, pnet):
        super(Listener, self).__init__()
        self.listening = True
        self.pnet = pnet
        self.con = con
        self.db = db
        self.connections_count = 0

    def processClient(self, client):
        pass

    def run(self):
        self.con.listen()
        while self.listening:
            try:
                obj, addr = self.con.accept()
                print(addr)
                self.db.addIp(addr[0], addr[1])
                self.connections_count += 1
                threading.Thread(
                    target=self.processClient,
                    args=(obj,)
                ).start()
                self.pnet.updateStatus(self.connections_count)
            except OSError:
                break

    def stop(self):
        self.listening = False
        return

class Connections():
    def __init__(self, pnet):
        self.pnet = pnet
        self.ip, self.port = 'localhost', 9989
        self.connected = False
        self.bindd = False
        ## objects ##
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.attemptBind()
        self.db = Cdb()
        self.listener = None

    def close(self):
        try:
            self.listener.stop()
            if self.bindd:
                self.connection.close()
        except OSError:
            return
        except AttributeError:
            return

    def attemptBind(self):
        try:
            self.connection.bind((self.ip, self.port))
        except Exception as e:
            print("Connecting failed. Trying again. Exception: ", e)
            self.port += 1
            self.attemptBind()

    def connect(self):
        if self.connected:
            self.connected = False
            self.listener.stop()
            return
        self.connected = True
        self.listener = Listener(self.connection, self.db, self.pnet)
        self.listener.start()
        #print("Listener started on ip {0} and port {1}".format(self.ip, self.port))


    def listen(self):
        pass
