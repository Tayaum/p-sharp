from error import Error

class Parser:
    def __init__(self, code: str, file):
        #Pass in code
        self.code = code
        self.file = file
        #Parse code
        self.code = self.code.replace(r'\t', '')
        self.code = self.code.replace('    ', '')
        self.code = self.Parse(self.code, self.file)

    def Parse(self, code: str, file) -> str:
        #Parse code into normal python
        code = self.ParseInclude(code)
        code = self.ParseComments(code)
        code = self.ParseKeyWords(code)
        code = self.ParseEOL(code)
        code = self.ParseBraces(code)
        code = self.ParseFunctions(code)
        code = self.CleanCode(code)
        code = self.AddEntryPoint(file, code)

        #Dump code to file
        with open(file.replace('.ps', ''), "w") as f:
            f.write(code)
        return code
     
    def ParseComments(self, code: str) -> str:
        for line in code.splitlines():
            if "//" in line:
                if not self.IsInString("//", line):
                    if list(line)[0] == "/" and list(line)[1] == "/":
                        code = code.replace(line, "")
                    else:
                        newLine = line.partition("//")[0]
                        code = code.replace(line, newLine)                    
        return code

    def ParseInclude(self, code: str) -> str:
        includeName = ""
        for line in code.splitlines():
            words = line.split()
            for wordNo, word in enumerate(words):
                if words[wordNo] == "from" and not self.IsInString(words[wordNo], line):
                    if words[wordNo + 1]== "native":
                        if words[wordNo + 2] == "include":
                            words[wordNo] = f"from {words[wordNo + 3]} import *"
        for line in code.splitlines():
            words = line.split()
            for wordNo, word in enumerate(words):
                if word == "include" and not self.IsInString(word, line):
                    includeName = words[wordNo + 1]
                    code = code.replace(line, "")
                    with open(includeName + ".p", "r") as file:
                        code = file.read() + "\n" + code
        for line in code.splitlines():
            if "from native reference " in line:
                if self.IsInString("from native reference ", line, True):
                    continue
                code = code.replace(line, line.replace("from native reference ", "import "))
                words = line.split()
                newLine = ""
                for wordNo, word in enumerate(words):
                    if words[wordNo] == "from" and not self.IsInString(words[wordNo], line):
                        if words[wordNo + 1] == "native":
                            if words[wordNo + 2] == "reference":
                                words[wordNo] = "import"
                                words[wordNo] = ""
                                words[wordNo + 2] = ""
                                newLine = " ".join(words)
                if newLine != "":
                    code = code.replace(line, newLine)

        return code

    def ParseKeyWords(self, code: str) -> str:
        for line in code.splitlines():
            if "this" in line and not self.IsInString("this", line):
                code = code.replace(line, line.replace("this", "self"))
        for line in code.splitlines():
            if "undefined" in line and not self.IsInString("undefined", line):
                code = code.replace(line, line.replace("undefined", "Undefined"))
        for line in code.splitlines():
            if "$" in line and not self.IsInString("$", line):
                code = code.replace(line, line.replace("$", "Type.as_pointer(") + ')')
        for line in code.splitlines():
            if "true" in line and not self.IsInString("true", line):
                code = code.replace(line, line.replace("true", "True"))
        for line in code.splitlines():
            if "false" in line and not self.IsInString("false", line):
                code = code.replace(line, line.replace("false", "False"))
        for line in code.splitlines():
            if "null" in line and not self.IsInString("null", line):
                code = code.replace(line, line.replace("null", "None"))
        for line in code.splitlines():
            if "else if" in line and not self.IsInString("else if", line):
                code = code.replace(line, line.replace("else if", "elif"))
        return code

    def ParseEOL(self, code: str) -> str:
        code = "".join([s for s in code.splitlines(True) if s.strip("\r\n")])

        for line in code.splitlines():
            skipLine = False
            for token in ("func", "while", "for", "if", "else", "elif", "with", "from"):
                if token in line and not self.IsInString(token, line):
                    skipLine = True
            if ''.join(line.split()).startswith(("{", "}", "\n", "class")):
                skipLine = True
            elif line.strip() == "":
                skipLine = True
            if skipLine:
                continue
            if ";" in line and not self.IsInString(";", line):
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == ";":
                        if stringCount % 2 == 0:
                            lineChars[i] = "\n"
                            break

            elif line.endswith((":")):
                Error(f"Syntax error in: \n{line}")
            else:
                #Error(f"Missing semicolon in: \n{line}")
                pass
            if line.endswith((":")):
                Error(f"Syntax error in: \n{line}")

        return code

    def ParseBraces(self, code: str) -> str:
        leftBracesAmount = 0
        for line in code.splitlines():
            if "then" in line:
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == "then":
                        if stringCount % 2 == 0 and stringCount != 0:
                            leftBracesAmount += 1
                            break
        rightBracesAmount = 0
        for line in code.splitlines():
            if "end" in line:
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == "then":
                        if stringCount % 2 == 0 and stringCount != 0:
                            rightBracesAmount += 1
                            break

        if leftBracesAmount != rightBracesAmount:
            Error(("Braces amount is not equal"))

        newCode = ""
        splitLines = code.splitlines();
        for line in splitLines:
            if ";" in line and not self.IsInString(";", line):
                lineChars = list(line)
                stringCount = 0
                for i in range(len(lineChars)):
                    if lineChars[i] == '"' or lineChars[i] == "'":
                        stringCount += 1
                    if lineChars[i] == ";":
                        if stringCount % 2 == 0:
                            lineChars[i] = "\n"
                            break
                line = "".join(lineChars)
            if "class" in line:
                if not self.IsInString("class", line):
                    line = "\n"+" ".join(line.split())
            if "func" in line:
                if line.partition("func")[0].count("\"") != 0 and line.partition("func")[0].count("\"") % 2 == 0:
                    words = line.split()
                    for wordNo, word in enumerate(words):
                        if word == "func":
                            speechCount = line.partition("func")[2].count("\"")
                            otherCount = line.partition("func")[2].count("'")
                            if speechCount % 2 == 0 and otherCount % 2 == 0:
                                words[wordNo] = "def"
                                break
                    line = " ".join(words)
            leftBraceExpression = ''.join(line.split())
            if not self.IsInString("then", leftBraceExpression):
                if ''.join(line.split()).startswith(("then")):
                    newCode += ":\n"
            if not self.IsInString("end", line):
                    line = line.replace("end", "#endindent")
            if not self.IsInString("end", line):
                line = line.replace("then", "#startindent")
            line += "\n"
            newCode += line
            line += "\n"

        return newCode

    def ParseFunctions(self, code: str) -> str:
        code = code
        for line in code.splitlines():
            if "func" in line and not self.IsInString("func", line):
                code = code.replace(line, line.replace("func", "def"))
        for line in code.splitlines():
            if "def constuctor" in line and not self.IsInString("def constructor", line):
                code = code.replace(line, line.replace("def constructor", "def __init__"))
        for line in code.splitlines():
            if "echo" in line and not self.IsInString("echo", line):
                code = code.replace(line, line.replace("echo", "print"))
        for line in code.splitlines():
            if "def destructor" in line and not self.IsInString("def destuctor", line):
                code = code.replace(line, line.replace("def destuctor", "def __del__"))
        for line in code.splitlines():
            if ") is" in line and not self.IsInString(") is", line):
                code = code.replace(line, line.replace(") is", ") ->"))
        for line in code.splitlines():
            if "def" in line:
                if (line.partition("def")[0].strip() == ""):
                    code = code.replace(line, line.replace("(", "(self,"))
        return code

    def CleanCode(self, code : str) -> str:
        

        splitLines = code.splitlines()
        for lineNo, line in enumerate(splitLines):
            if line.startswith(":"):
                splitLines[lineNo - 1] = splitLines[lineNo - 1] + ":"
                splitLines[lineNo] = ""
        newCode = ""
        for line in splitLines:
            newCode += line + "\n"
        code = newCode

        splitLines = code.splitlines()
        newCode = ""
        for lineNo, line in enumerate(splitLines):
            i = 0
            indentCount = 0
            while i <= lineNo:
                if "#endindent" in splitLines[i]:
                    if not self.IsInString("#endindent", splitLines[i], True):
                        indentCount -= 1
                    
                elif "#startindent" in splitLines[i] and not self.IsInString("#startindent", splitLines[i], True):
                    if not self.IsInString("#startindent", splitLines[i]):
                        indentCount += 1
                i += 1
            newCode += ("    " * indentCount) + line + "\n"
        code = newCode

        
        newCode = ""
        for line in code.splitlines():
            if "#endindent" in line:
                if not self.IsInString("#endindent", line):
                    line = line.replace(line, "")
            if "#startindent" in line:
                if not self.IsInString("#startindent", line):
                    line = line.replace(line, "")
            newCode += line + "\n"
        code = newCode

        
        newCode = ""
        for line in code.splitlines():
            if line.strip("\t\r\n") == "":
                line = line.replace(line, line.strip("\t\r\n"))
                newCode += line
            else:
                newCode += line + "\n"
        code = newCode

        code = "\n".join([ll.rstrip() for ll in code.splitlines() if ll.strip()])

        return code

    def AddEntryPoint(self, file, code: str) -> str:
        code += "\n"
        code += '''
import traceback
import sys
from llvmlite.ir import *
def str_pointer(s):
    try:
       return str(s)[:-1]
    except:
        return 'error'
def int_pointer(i):
    try:
        return int(str(i)[:-1])
    except:
        return 'error'
def float_pointer(f):
    try:
        return float(str(i)[:-1])
    except:
        return 'error'
def bool_pointer(b):
    try:
        return bool(b[:-1])
    except:
        return 
try:
    main = Main()
except NameError:
    sys.exit(0)

try:
    main.main()
except Exception as e:
    a = traceback.format_exc()
    b = sys.argv[0]
    b = b[0]
    b = len(b)
    a = a[(88 + b):]
    print(a)
    sys.exit(1)
        '''

        return code

    def IsInString(self, phrase : str, line : str, returnIfMultiple = False) -> bool:
        if not phrase in line:
            return False
        if line.count(phrase) > 1:
            return returnIfMultiple
        leftSide = line.partition(phrase)[0]
        if leftSide.count("\"") > 0:
            if leftSide.count("\"") % 2 == 0:
                return False
            else:
                return True
        if leftSide.count("\'") > 0:
            if leftSide.count("\'") % 2 == 0:
                return False
            else:
                return True