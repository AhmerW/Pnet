
class Cdb():
    """Connection database"""
    def __init__(self):
        self.connections = {}
    def __del__(self):
        self.saveConnections()

    def saveConnections(self):
        pass

    def addIp(self, ip, uid):
        self.connections[str(ip)] = str(uid)

    def resolveFromIp(self, ip):
        pass
