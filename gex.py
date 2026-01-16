#!/bin/env python3
import sys
from editor import Editor
from parser import Lexer, InputError

class UI:
    def __init__(self, editor:Editor):
        self.editor = editor
        self.currentLine = 0
        self.bufferName = None
        self.running = True
    
    def input(self, prompt:str) -> str:
        return input(prompt)

    def main(self):
        editor = self.editor
        while self.running:
            if self.currentLine >= 0:
                print(f"\n\u2552 {self.currentLine+1}\u2502 {editor.getLine(self.currentLine)}")
            else:
                print("\u2552 ...")
            try:
                userin = self.input(f"\u2558\u2550> ")
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

            currentLineNor = self.currentLine

            for arg in argsR:
                if isinstance(arg,Lexer.LineRangeArg):
                    if arg.begin.update:
                        self.currentLine = arg.begin.eval(self.currentLine)
                    arg.begin = arg.begin.eval(self.currentLine)
                    if arg.end.update:
                        self.currentLine = arg.end.eval(self.currentLine)
                    arg.end = arg.end.eval(self.currentLine)
                    args.append((arg.begin,arg.end))
                elif isinstance(arg,Lexer.LineArg):
                    res = arg.eval(self.currentLine)
                    if arg.update:
                        self.currentLine = res
                    args.append(res)
                else:
                    args.append(arg.eval())

            if argsR:
                if isinstance(argsR[0],Lexer.LineArg):
                    line = args[0]
                else:
                    line = None

            def appendMode():
                if editor.getLine(self.currentLine).strip():
                    self.currentLine += 1
                while True:
                    inp = self.input(": ")
                    if inp.rstrip() == ".":
                        break
                    editor.insertLine(self.currentLine, inp)
                    self.currentLine += 1

            if   command == "+": # insert
                editor.insertLine(line,textarg)
            elif command == "a":
                if editor.getLine(line).strip():
                    line += 1
                    self.currentLine += 1

                if textarg:
                    editor.insertLine(line,textarg)
                else:
                    appendMode()
            elif command == "-": # remove
                for line in range(args[0][0],args[0][1]+1):
                    editor.removeLine(line)
                self.currentLine -= 1
            elif command == "<": # replace/move
                if textarg:
                    editor.replaceLine(line,textarg)

            elif command == "V": # view all
                lines = editor.getLines()
                linenummaxlen = len(str(len(lines)))
                for i, line in enumerate(lines):
                    print(f"{format(i+1,f"0{linenummaxlen}")}: {line}")
            elif command == "v": # view
                lines = editor.getLines(args[0][0],args[0][1])
                linenummaxlen = len(str(len(lines)))
                for i, line in enumerate(lines):
                    print(f"{format(args[0][0]+i+1,f"0{linenummaxlen}")}: {line}")

            elif command == "r": # read
                if editor.dirty:
                    confirm = None
                    while confirm not in list("yn"):
                        if confirm is not None:
                            print("Please answer y or n")
                        confirm = self.input("Current buffer is not saved, discard?(Y/n)")[0].lower()
                    if confirm == "n":
                        continue

                name = self.input("File name (Leave blank for blank file)> ")
                if name:
                    try:
                        editor.load(open(name,"rb").read())
                        self.bufferName = name
                        self.currentLine = len(editor.buffer)-1
                    except OSError as e:
                        print(f"Unable to load {name}: {e}")
                else:
                    editor.buffer = []
                    self.bufferName = None
                    self.currentLine = -1
            elif command == "w": # write
                if self.bufferName:
                    name = self.input(f"File name to save as (default: {self.bufferName})> ")
                else:
                    name = self.input("File name to save as> ")
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

                print(f"Editing line {self.currentLine+1 if self.currentLine>=0 else '(none)'}")

            elif command == "q": # quit
                if editor.dirty:
                    confirm = None
                    while confirm not in list("yn"):
                        if confirm is not None:
                            print("Please answer y or n")
                        confirm = self.input("Current buffer is not saved, quit anyway?(Y/n)")[0].lower()
                    if confirm == "n":
                        continue
                print("Exiting...")
                self.running = False

            if not command in list("+a-<r"):
                self.currentLine = currentLineNor


if __name__ == "__main__":
    editor = Editor()
    ui = UI(editor)
    ui.main()
