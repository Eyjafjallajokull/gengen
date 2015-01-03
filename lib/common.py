import random
import subprocess
import sys
import copy

def do(cmd, returncode = False, output = False):
    if output:
        print(cmd)
    proc = subprocess.Popen([cmd],
        shell = True,
        stdin = sys.stdin if output else subprocess.PIPE,
        stdout = sys.stdout if output else subprocess.PIPE,
        stderr = sys.stderr if output else subprocess.PIPE)

    if output:
        stdout = ''
        proc.wait()
    else:
        result = proc.communicate()
        stdout = result[0]
        if len(stdout) > 0 and stdout[len(stdout)-1] == '\n':
            stdout = stdout[0:-1]

    if returncode:
        return proc.returncode
    else:
        return stdout

def rand(absMax):
    new = (random.random()-0.5)*absMax*2
    return new

def randNumber(number, absMax, factor):
    new = number
    if abs(number) > absMax:
        number *= 0.9
    while True:
        new = number + (random.random()-0.5)*factor
        if abs(new)<absMax: break
    return new

def randArray(array, select=None):
    tmp = copy.copy(array)
    random.shuffle(tmp)
    if select==None:
        return tmp
    else:
        return tmp[0:select]