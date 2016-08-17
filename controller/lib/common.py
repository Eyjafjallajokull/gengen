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
        stderr = sys.stderr if output else subprocess.PIPE, close_fds=True)

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
    while abs(number) > absMax:
        number *= 0.95
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


# determinant of matrix a
def det(a):
    return a[0][0]*a[1][1]*a[2][2] + a[0][1]*a[1][2]*a[2][0] + a[0][2]*a[1][0]*a[2][1] - a[0][2]*a[1][1]*a[2][0] - a[0][1]*a[1][0]*a[2][2] - a[0][0]*a[1][2]*a[2][1]


# unit normal vector of plane defined by points a, b, and c
def unit_normal(a, b, c):
    x = det([[1,a[1],a[2]],
             [1,b[1],b[2]],
             [1,c[1],c[2]]])
    y = det([[a[0],1,a[2]],
             [b[0],1,b[2]],
             [c[0],1,c[2]]])
    z = det([[a[0],a[1],1],
             [b[0],b[1],1],
             [c[0],c[1],1]])
    magnitude = (x**2 + y**2 + z**2)**.5
    return (x/magnitude, y/magnitude, z/magnitude)


# dot product of vectors a and b
def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


# cross product of vectors a and b
def cross(a, b):
    x = a[1] * b[2] - a[2] * b[1]
    y = a[2] * b[0] - a[0] * b[2]
    z = a[0] * b[1] - a[1] * b[0]
    return (x, y, z)


# area of polygon poly
def triangle_area(poly):
    if len(poly) < 3: # not a plane - no area
        return 0

    total = [0, 0, 0]
    for i in range(len(poly)):
        vi1 = poly[i]
        if i is len(poly)-1:
            vi2 = poly[0]
        else:
            vi2 = poly[i+1]
        prod = cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = dot(total, unit_normal(poly[0], poly[1], poly[2]))
    return abs(result/2)