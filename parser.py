from __future__ import annotations
from collections import deque
import colorama
import re

class InputError(Exception):"Error in command"

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
    
    class LineRangeArg(Arg):
        def __init__(self,begin:Lexer.LineArg,end:Lexer.LineArg):
            self.begin = begin
            self.end = end
        def __repr__(self):
            return f"LineRangeArg({self.begin},{self.end})"
        
        def eval(self, recentLine:int):

            return (self.begin, self.end)

    class Command:
        def __init__(self):
            self.name:str = ""
            self.args:list[Lexer.Arg] = []
            self.strarg:str = ""
        
        def __repr__(self):
            return f"{self.name} {self.args} {ascii(self.strarg)}"

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
        self.vals = deque(re.findall(r"^[a-zA-Z\-+<]+|\d*[.,]?\d*-\d*[.,]?\d*|\d+[.,]?\d*|\d*[.,]?\d+|[.,]|[a-zA-Z]+", self.primary)) # the last part is mainly to detect input errors
        self.command = ""

    def getCom(self):
        name = self.vals.popleft()
        self.result.name = name

    def getLineRangeArg(self):
        if len(self.vals) == 0:
            raise InputError("Not enough parameters")

        if "-" in self.vals[0]:
            offsets = self.vals.popleft().split("-")
            if offsets[0]:
                val1 = offsets[0]
                try:
                    val1 = self.getLineArgSub(val1)
                except ValueError:
                    raise InputError(f"Expected a number instead of '{val1}'")
            else:
                val1 = Lexer.LineArg(0,True,0)
            if offsets[1]:
                val2 = offsets[1]
                try:
                    val2 = self.getLineArgSub(val2)
                except ValueError:
                    raise InputError(f"Expected a number instead of '{val2}'")
            else:
                val2 = Lexer.LineArg(0,True,0)
            self.result.args.append(self.LineRangeArg(val1,val2))
        else:
            try:
                val = self.getLineArgSub(self.vals.popleft())
                self.result.args.append(self.LineRangeArg(val,val))
            except IndexError:
                raise InputError("Not enough parameters")
            except ValueError:
                raise InputError(f"Expected a number instead of '{val}'")
    
    def getLineArgSub(self, val):
        if "," in val:
            offsets = val.split(",")
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
            return self.LineArg(val2-val1,True,True)
        elif "." in val:
            offsets = val.split(".")
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
            return self.LineArg(val2-val1,True,False)
        else:
            val = val
            try:
                val = int(val)
            except ValueError:
                raise InputError(f"Expected a number instead of '{val}'")
            return self.LineArg(val,False,True)

    def getLineArg(self):

        if len(self.vals) == 0:
            raise InputError("Not enough parameters")

        val = self.vals.popleft()
        self.result.args.append(self.getLineArgSub(val))

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
            self.getLineRangeArg()
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
            self.getLineRangeArg()
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
-N (or -B-E)
N;T

to be implemented[
dN B E
iN B;T
]

s
vB-E
V

w
r

uncertain [
fw;NAME
fr;NAME
]

q
"""


# test
if __name__ == "__main__":
    expect_success = [
        # test for relative lines, absolute lines, ranges, and defaults
        "+0;E",
        "+1.;E",
        "+.;E",
        "+.1;E",
        "-0-1",
        "<.;Replaced current line",
        "v0-2",

        # others
        "V",
        "s",
        "w",
        "q"
    ]
    expect_failure = [
        "+;No Line Number",
        "-A-B",
        "<X;No Number",
        "unknowncmd",
    ]

    for test in expect_success:
        lexer = Lexer(test)
        try:
            result = lexer.main()
            print(f"Input: {test}\n\t{colorama.Fore.GREEN}{result}")
        except InputError as e:
            print(f"Input: {test}\n\t{colorama.Fore.RED}{e}")
        print(colorama.Style.RESET_ALL)
    
    for test in expect_failure:
        lexer = Lexer(test)
        try:
            result = lexer.main()
            print(f"Input: {test}\n\t{colorama.Fore.RED}Expected failure but got: {result}")
        except InputError as e:
            print(f"Input: {test}\n\t{colorama.Fore.GREEN}Correctly failed with: {e}")
        print(colorama.Style.RESET_ALL)
