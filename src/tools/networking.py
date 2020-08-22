import os
import json
import string
import secrets

class Network():
    def __init__(self):
        self.paths = {} # {code: path}
        self.strength = 8 # code strength
        self.uppercase, self.lowercase, self.digits = True, True, True


    def generateCode(self):
        choices = self.getChoices()
        if self.strength <= 0:
            return False
        return ''.join(
            secrets.choice(
                choices
            ) for _ in range(0, self.strength, 1)
        )

    def getChoices(self):
        choices = ""
        if self.uppercase:
            choices += string.ascii_uppercase
        if self.lowercase:
            choices += string.ascii_lowercase
        if self.digits:
            choices += str(string.digits)
        return str(choices)

    def getPath(self, code):
        try:
            if not code in self.paths:
                return False
            return self.paths[code]
        except KeyError:
            return False

    def loadFiles(self) -> bool:
        if not os.path.isdir('shared'):
            return False
        if not os.path.isfile(os.path.join('shared', 'paths.json')):
            return False
        try:
            with open(os.path.join('shared', 'paths.json'), 'r') as f:
                if not f.readable():
                    return False
                self.paths = json.load(f)
                return False
        except Exception as e:
            print(e)
            return False

    def savePaths(self):
        pass

    def addFile(self, path):
        self.paths[self.generateCode()] = str(path)


    def getData(self, path):
        try:
            with open(path, 'rb') as f:
                if not f.readable():
                    return False
                content = f.read()
                return [content[i:i+4000] for i in range(0, len(content), 4000)]
        except FileNotFoundError:
            return False
