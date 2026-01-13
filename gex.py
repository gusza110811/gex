#!/bin/env python
import re
import sys
from collections import deque

class InputError(Exception):"Error in command"

class Editor:
    def __init__(self):
        self.buffer:list[bytearray] = []
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
        try:
            self.buffer.pop(i)
        except IndexError:
            pass

    def replaceLine(self, i:int, text:str):
        self.padLine(i)
        self.buffer[i] = bytearray(text,encoding="utf-8")
    
    def load(self, data:bytes):
        self.buffer = [bytearray(line) for line in data.split(b"\n")]

class Lexer:

    class Arg:
        def __init__(self,val):
            self.val = val
        def __repr__(self):
            return f"Arg({self.val})"
        def eval(self):
            return self.val
    class LineArg(Arg):
        def __init__(self,line:int,relative:bool,update:bool):
            self.line = line
            self.relative = relative
            self.update = update
        def __repr__(self):
            return f"LineArg({self.line},{self.relative},{self.update})"

        def eval(self, recentLine:int):
            if not self.relative:
                result = self.line - 1
            else:
                result = recentLine + self.line

            return result

    class Command:
        def __init__(self):
            self.name:str = ""
            self.args:list[Lexer.Arg] = []
            self.strarg:str = ""
        
        def __repr__(self):
            return f"{self.name} {self.args} ;{self.strarg}"

    def __init__(self,text:str):
        if not text:
            self.skip = True
            return
        else:
            self.skip = False
        self.result = self.Command()
        if text.startswith(";"):
            text = "+,1" + text
        elif text[0] in list(".,0123456789"):
            text = "<" + text
        self.primary = text.split(";")[0]
        self.secondary = text[len(self.primary)+1:]
        self.vals = deque(re.findall(r"\d+[.,]|[.,]\d+|\d+|[a-zA-Z\-\+\<]", self.primary))
        self.command = ""

    def getCom(self):
        name = self.vals.popleft()
        self.result.name = name

    def getLineArg(self):

        if len(self.vals) == 0:
            raise InputError("Not enough parameters")

        if "," in self.vals[0]:
            offsets = self.vals.popleft().split(",")
            val1, val2 = 0, 0
            if offsets[0]:
                val1 = offsets[0]
                try:
                    val1 = int(val1)
                except ValueError:
                    raise InputError(f"Expected a number instead of '{val1}'")
            if offsets[1]:
                val2 = offsets[1]
                try:
                    val2 = int(val2)
                except ValueError:
                    raise InputError(f"Expected a number instead of '{val2}'")
            self.result.args.append(self.LineArg(val2-val1,True,True))
        elif "." in self.vals[0]:
            offsets = self.vals.popleft().split(".")
            val1, val2 = 0, 0
            if offsets[0]:
                val1 = offsets[0]
                try:
                    val1 = int(val1)
                except ValueError:
                    raise InputError(f"Expected a number instead of '{val1}'")
            if offsets[1]:
                val2 = offsets[1]
                try:
                    val2 = int(val2)
                except ValueError:
                    raise InputError(f"Expected a number instead of '{val2}'")
            self.result.args.append(self.LineArg(val2-val1,True,False))
        else:
            val = self.vals.popleft()
            try:
                val = int(val)
            except ValueError:
                raise InputError(f"Expected a number instead of '{val}'")
            self.result.args.append(self.LineArg(val,False,True))

    def getArg(self):
        try:
            val = self.vals.popleft()
        except IndexError:
            raise InputError("Not enough parameters")
        try:
            val = int(val)
        except ValueError:
            raise InputError(f"Expected a number instead of '{val}'")
        self.result.args.append(self.Arg(val))
    
    def getChrArg(self):
        try:
            char = self.vals.popleft()
        except IndexError:
            raise InputError("Not enough parameters")
        self.result.args.append(self.Arg(char))

    def getStrArg(self):
        self.result.strarg = self.secondary
        self.text = ""

    def main(self):
        if self.skip:
            return None

        self.getCom()
        com = self.result.name
        if com == "+":
            self.getLineArg()
            self.getStrArg()
        elif com == "-":
            self.getLineArg()
        elif com == "<":
            self.getLineArg()
            self.getStrArg()
        elif com == "d":
            self.getLineArg()
            self.getArg()
            self.getArg()
        elif com == "i":
            self.getLineArg()
            self.getArg()
            self.getStrArg()
        elif com == "v":
            self.getLineArg()
            self.getLineArg()
        elif com == "f":
            self.getChrArg()
            self.getStrArg()
        elif com == "s" or com == "V" or com == "w" or com == "r" or com == "q":pass
        else:
            raise InputError(f"Unknown Command: {com}")

        if len(self.vals) > 0:
            raise InputError("Too many parameters")
        
        return self.result

"""
Commands
+N;T
-N
N;T

dN B E
iN B;T

s
vB E
V

w
r
fw;NAME
fr;NAME

q
"""

class UI:
    def __init__(self, editor:Editor):
        self.editor = editor
        self.recentLine = -1
        self.bufferName = None

    def main(self):
        editor = self.editor
        while 1:
            if self.recentLine >= 0:
                print(f"\n\u2552 {self.recentLine+1}\u2502 {editor.getLine(self.recentLine)}")
            else:
                print("\u2552 ...")
            try:
                userin = input(f"\u2558\u2550> ")
            except KeyboardInterrupt:
                print("Please use q to exit")
                continue
            except EOFError:
                print("Warning: forceful exit (edit buffer lost)")
                sys.exit(1)
            lexer = Lexer(userin)
            try:
                result = lexer.main()
            except InputError as e:
                print(e)
                continue

            if not result:
                continue

            command = result.name
            argsR = result.args
            textarg = result.strarg

            args = []

            recentLineNor = self.recentLine

            for arg in argsR:
                if isinstance(arg,Lexer.LineArg):
                    res = arg.eval(self.recentLine)
                    if arg.update:
                        self.recentLine = res
                    args.append(res)
                else:
                    args.append(arg.eval())

            update = None

            if argsR:
                if isinstance(argsR[0],Lexer.LineArg):
                    line = args[0]
                else:
                    line = None

            def insertionMode():
                while True:
                    inp = input(";")
                    if inp == "":
                        break
                    editor.insertLine(self.recentLine, inp)

            if   command == "+": # insert
                editor.insertLine(line,textarg)
                insertionMode()
            elif command == "-": # remove
                editor.removeLine(line)
                self.recentLine -= 1
            elif command == "<": # replace
                editor.replaceLine(line,textarg)

            elif command == "V": # view all
                lines = editor.getLines()
                linenummaxlen = len(str(len(lines)))
                for i, line in enumerate(lines):
                    print(f"{format(i+1,f"0{linenummaxlen}")}: {line}")
            elif command == "v": # view
                lines = editor.getLines(args[0],args[1])
                linenummaxlen = len(str(len(lines)))
                for i, line in enumerate(lines):
                    print(f"{format(args[0]+i+1,f"0{linenummaxlen}")}: {line}")

            elif command == "r": # read
                if editor.dirty:
                    confirm = None
                    while confirm not in list("yn"):
                        if confirm is not None:
                            print("Please answer y or n")
                        confirm = input("Current buffer is not saved, discard?(Y/n)")[0].lower()
                    if confirm == "n":
                        continue

                name = input("File name (Leave blank for blank file)> ")
                if name:
                    try:
                        editor.load(open(name,"rb").read())
                        self.bufferName = name
                        self.recentLine = len(editor.buffer)-1
                    except OSError as e:
                        print(f"Unable to load {name}: {e}")
                else:
                    editor.buffer = []
                    self.bufferName = None
                    self.recentLine = -1
            elif command == "w": # write
                if self.bufferName:
                    name = input(f"File name to save as (default: {self.bufferName})> ")
                else:
                    name = input("File name to save as> ")
                    if not name:
                        print("Save aborted")
                        continue
                if not name:
                    name = self.bufferName
                else:
                    self.bufferName = name
                try:
                    with open(self.bufferName,"wb") as f:
                        f.write(b"\n".join(editor.buffer))
                    editor.dirty = False
                    print(f"Saved to {self.bufferName}")
                except OSError as e:
                    print(f"Unable to save to {self.bufferName}: {e}")
            
            elif command == "s": # status
                if self.bufferName:
                    print(f"Editing {self.bufferName}",end=" ")
                else:
                    print("Editing (unnamed)",end=" ")
                print(f"{'[Modified]' if editor.dirty else ''}")

                print(f"{len(editor.buffer)} lines")

                print(f"Recent line: {self.recentLine+1 if self.recentLine>=0 else '(none)'}")

            elif command == "q": # quit
                if editor.dirty:
                    confirm = None
                    while confirm not in list("yn"):
                        if confirm is not None:
                            print("Please answer y or n")
                        confirm = input("Current buffer is not saved, quit anyway?(Y/n)")[0].lower()
                    if confirm == "n":
                        continue
                print("Exiting...")
                sys.exit(0)

            if not command in list("+-<r"):
                self.recentLine = recentLineNor


if __name__ == "__main__":
    editor = Editor()
    ui = UI(editor)
    ui.main()