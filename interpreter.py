import os.path
import subprocess
import sys
import shutil

#PyPy
pyInstallerInstalled = True

try:
    import PyInstaller.__main__ as PyInstaller
except ImportError:
    pyInstallerInstalled = False

#Custom
from parse import Parser
from error import Error

version = "0.0.1"

class Compiler:
    def compile(self, code :str, file) -> None:
        subprocess.call(["python3", file.replace(".ps", "")])
        os.remove(file.replace(".ps", ""))
def GetCode(filePath) -> str:
    if os.path.isfile(filePath):
        with open(filePath, 'r') as file:
            return file.read()
    else:
        Error("Input file not found")

def HandleArgs() -> None:
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        Error('''
        Command line arguments:
        --help -h: Prints this message
        --version -b: Prints the version of the interpreter
        --run -r [file]: Runs the interpreter on the file specified
        --transpile -t [file] [address]: Converts the file specified into python code and saves it to the address specified
            ''')
    elif sys.argv[1] == "--run" or sys.argv[1] == "-r":
        if len(sys.argv) < 3:
            Error("Invalid number of arguments")
        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(GetCode((sys.argv[2])), sys.argv[2])
                compiler = Compiler()
                compiler.compile(parser.code, sys.argv[2])
            else:
                Error("File not found")
    elif os.path.isfile(sys.argv[1]):
        parser = Parser(GetCode(sys.argv[1]))
        compiler = compiler()
        compiler.compile(parser.code)
    elif sys.argv[1] == "--transpile" or sys.argv[1] == "-t":
        if len(sys.argv) < 4:
            Error("Invalid number of arguments")
        else:
            if os.path.isfile(sys.argv[2]):
                parser = Parser(GetCode((sys.argv[2])))
                with open(sys.argv[3], "w") as f:
                    f.write(parser.code)
            else:
                Error("Input file not found")
    else:
        Error("Invalid argument")

    if (os.path.isfile(sys.argv[1])):
        os.remove(sys.argv[1])

def CheckArgs() -> str:
    if len(sys.argv) < 2:
        Error("Invalid number of arguments")
    HandleArgs()
    
if __name__ == "__main__":
    CheckArgs()