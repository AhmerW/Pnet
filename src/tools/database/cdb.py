
class Cdb():
    """Connection database"""
    def __init__(self):
        self.connections = {}
    def __del__(self):
        self.saveConnections()

    def saveConnections(self):
        pass

    def addUid(self, uid, ip):
        self.connections[str(uid)] = str(ip)

    def resolveFromUid(self, uid):
        if uid in self.connections:
            return self.connections[uid]
        return False
