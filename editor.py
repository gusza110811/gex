class Editor:
    def __init__(self):
        self.buffer:list[bytearray] = [bytearray()]
        self.dirty = False
    
    def padLine(self, target:int):
        self.dirty = True
        target += 1
        self.dirty = True
        if target < len(self.buffer):
            return
        add = target - len(self.buffer)
        self.buffer.extend(bytearray() for _ in range(add))
        return add
    
    def getLine(self, line:int):
        try:
            return self.buffer[line].decode()
        except IndexError:
            return ""
    
    # end is inclusive unlike regular python slice
    def getLines(self, begin=0, end=-1):
        if len(self.buffer) == 0:
            return [""]
        
        if end == -1:
            end = len(self.buffer)-1
        
        selected = [item.decode() for item in self.buffer[begin:end+1]]

        return selected

    def insertLine(self, i:int, text:str):
        self.padLine(i)
        self.buffer.insert(i, bytearray(text,encoding="utf-8"))
    
    def removeLine(self, i:int):
        self.dirty = True
        try:
            self.buffer.pop(i)
        except IndexError:
            pass

    def replaceLine(self, i:int, text:str):
        self.padLine(i)
        self.buffer[i] = bytearray(text,encoding="utf-8")
    
    def load(self, data:bytes):
        self.buffer = [bytearray(line) for line in data.split(b"\n")]