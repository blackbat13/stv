class Parser:
    str = None
    len = None
    idx = None

    def __init__(self):
        pass

    def setStr(self, str):
        self.str = str
        self.len = len(str)
        self.idx = 0

    def canRead(self):
        return self.idx < self.len

    def readChar(self):
        if not self.canRead():
            raise Exception("Unexpected end of input")
        c = self.str[self.idx]
        self.stepForward()
        if not c.isspace():
            return c
        else:
            return self.readChar()

    def peekChar(self, diff):
        if self.canRead():
            return self.str[self.idx + diff]
        else:
            return None

    def read(self, numNonWhiteSpaceChars):
        str = ""
        while len(str) < numNonWhiteSpaceChars:
            str += self.readChar()
        return str

    def readUntil(self, chars):
        str = ""
        while True:
            c = self.readChar()
            if c in chars:
                self.stepBack()
                return str, c
            else:
                str += c

    def consume(self, text):
        str = self.read(len(text))
        if str != text:
            print(text)
            raise Exception("Consumed string is not equal to the expected string")

    def stepForward(self):
        self.idx = self.idx + 1

    def stepBack(self):
        self.idx = self.idx - 1
