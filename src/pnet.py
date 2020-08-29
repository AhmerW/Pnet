from sys import exit as terminate
from tools.events import Events
from gui.first import MainWindow
from tools.connections import Connections

class Pnet(MainWindow):
    connect_texts = {0: 'Connect', 1: 'Disconnect'}
    def updateStatus(self, total=0):
        self.label_total.configure(text="Total connections established: {0}".format(total))

    def onClick(self, button):

        if button == 'File':
            self.event.fileWindow()
        elif button == 'Chat':
            self.event.chatWindow()
        elif button == 'Create_a_connection':
            self.event.privateConnection()
        elif button == 'Connect':
            try:
                where = self.buttons.index(button)
                self.connected = not self.connected

                text = Pnet.connect_texts[int(self.connected)]
                self.button_objects[where].configure(text=text)

                ## create label ##
                text = Pnet.connect_texts[int(not self.connected)]
                self.label_connect.configure(text="{0} {1} the network".format(
                    text+"ed",
                    "to" if text[0] == "C" else "from"
                ))
                self.connector.listen()
                self.updateStatus()
            except ValueError:
                return
            except AttributeError as e:
                if not hasattr(self, 'connector'):
                    self.connector = Connections(self)
                    self.onClick(button)
                else:
                    raise e
    def onClose(self):
        if self.connected:
            self.onClick('connect')
        if hasattr(self.connector.connection, 'con'):
            self.connector.connection.con.close()
        for chat in self.chats:
            if hasattr(chat, 'sock'):
                chat.sock.close()

        terminate()

if __name__ == "__main__":
    network = Pnet()
    network.total = 0
    network.connector = Connections(network)
    network.event = Events(network)
    network.start()
