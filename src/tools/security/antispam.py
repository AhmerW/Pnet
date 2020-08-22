import time
import random
from security.gen import randstr

class Antispam():
    def __init__(self):
        self.lts = {}



    def new(self):
        rand = randstr(5)
        self.lts[rand] = time.time()
        return rand
