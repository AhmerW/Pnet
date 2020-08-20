from sys import exit as terminate
from gui.first import MainWindow
from tools.connections import Connections
from tools.events import Events

class pnet(MainWindow):
    connect_texts = {1: 'Connect', 0: 'Disconnect'}
    def updateStatus(self, total=0):
        self.label_total.configure(text="Total connections established: {0}".format(total))

    def onClick(self, button):
        print(button)
        if button == 'file_sharing':
            try:
                self.event.fileWindow()
            except AttributeError as e:
                if not hasattr(self, 'event'):
                    self.event = Events(self)
                    self.onClick(button)
                else:
                    raise e
        elif button == 'Connect':
            try:
                where = self.buttons.index(button)
                self.connected = not self.connected
                print(self.connected)

                text = pnet.connect_texts[int(self.connected)]
                self.button_objects[where].configure(text=text)

                ## create label ##
                text = pnet.connect_texts[int(not self.connected)]
                self.label_connect.configure(text="{0} {1} the network".format(
                    text+"ed",
                    "to" if text[0] == "C" else "from"
                ))
                if not self.first:
                    self.connector.connect()
                else:
                    self.first = False
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
        if hasattr(self.connector, 'listener'):
            del self.connector.listener
            self.connector.connection.close()
        terminate()

if __name__ == "__main__":
    network = pnet()
    network.total = 0
    network.connector = Connections(network)
    network.event = Events(network)
    network.start()
