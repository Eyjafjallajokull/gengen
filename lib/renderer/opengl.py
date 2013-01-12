#!/usr/bin/env python
from Image import FLIP_LEFT_RIGHT
import pickle

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
from base import BaseRenderer
from PIL import Image
from math import sqrt
from lib.common import do

ESCAPE = '\033'

# Number of the glut window.
window = 0
meshData = []
LightAmbientColor = ( .5, .5, .5, 1 )
LightDiffuseColor = ( .9, .9, .9, 1 )
LightPosition = ( 0.0, 4.0, -2.0, 1)

dineAndDash = False
dine = None
size = None
# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height):                # We call this right after our OpenGL window is created.
    glClearColor(1.0, 1.0, 1.0, 0.0)    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LEQUAL)                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    glShadeModel(GL_FLAT)                # Enables Smooth Color Shading

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()                    # Reset The Projection Matrix
    # Calculate The Aspect Ratio Of The Window
    gluPerspective(45.0, float(Width) / float(Height), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)

    glLightfv(GL_LIGHT0, GL_DIFFUSE, LightDiffuseColor)        # Setup The Diffuse Light
    glLightfv(GL_LIGHT0, GL_AMBIENT, LightAmbientColor)        # Setup The Ambient Light
    glLightfv(GL_LIGHT0, GL_POSITION, LightPosition)    # Position The Light
    #glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, (0,0,0))    # Position The Light
    #glLightfv(GL_LIGHT0, GL_SPOT_EXPONENT, 128)    # Position The Light
    #glLightfv(GL_LIGHT0, GL_SPOT_CUTOFF, 90)    # Position The Light


    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    #glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (.5,.5,.5,1));

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width) / float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

# The main drawing function. 
def DrawGLScene():
    # Clear The Screen And The Depth Buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()                    # Reset The View
    glFrontFace(GL_CW);
    # Move Left 1.5 units and into the screen 6.0 units.
    glTranslatef(0, 0.0, -12.0)

    for objectData in meshData:
        drawTriangle(objectData)

    # Move Right 3.0 units.
    glTranslatef(0.0, 0.0, 0.0)

    #  since this is double buffered, swap the buffers to display what just got drawn.
    glutSwapBuffers()

    if dineAndDash:
        global dine
        dine = glReadPixels(0, 0, size[0], size[1], GL_RGB, GL_FLOAT).reshape((size[0] * size[1], -1))
        glutLeaveMainLoop()



def createNormal(o):
    a = [0,0,0]
    b = [0,0,0]
    c = [0,0,0]
    a[0] = o[0][0] - o[1][0]
    a[1] = o[0][1] - o[1][1]
    a[2] = o[0][2] - o[1][2]
    b[0] = o[1][0] - o[2][0]
    b[1] = o[1][1] - o[2][1]
    b[2] = o[1][2] - o[2][2]
    c[0] = (a[1] * b[2]) - (a[2] * b[1])
    c[1] = (a[2] * b[0]) - (a[0] * b[2])
    c[2] = (a[0] * b[1]) - (a[1] * b[0])
    return normalize(c)

def normalize(v):
    len = sqrt((v[0] * v[0]) + (v[1] * v[1]) + (v[2] * v[2]))
    if len == 0:
        len = 1.0
    v[0] /= len
    v[1] /= len
    v[2] /= len
    return v


def drawTriangle(objectData):
    glBegin(GL_POLYGON)                 # Start drawing a polygon
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (.5,.5,.5,1))
    normal = createNormal(objectData)
    normal[2] = -normal[2]
    glNormal3fv(normal)
    for v in objectData:
        glVertex3f(v[0], v[1], v[2])
    glEnd()


# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
# If escape is pressed, kill everything.
    if args[0] == ESCAPE:
        glutDestroyWindow(window)
        sys.exit()

def draw(size):
    global window
    glutInit(())
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)
    glutInitWindowSize(size[0], size[1])
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("POMPA")
    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glutReshapeFunc(ReSizeGLScene)
    glutKeyboardFunc(keyPressed)
    InitGL(size[0], size[1])


def main(size):
    draw(size)
    # Start Event Processing Engine
    glutMainLoop()

def getPixelData(sizeIn, meshDataIn):
    global meshData, dineAndDash, size
    meshData = meshDataIn
    dineAndDash =True
    size = sizeIn
    main(size)
    return dine

class OpenglRenderer(BaseRenderer):
    size = (320,240)

    def _renderToFile(self, genome):
        pixels = getPixelData(self.size, genome.data) *255
        pixels.astype(int)
        pixels = [ tuple(pixel) for pixel in pixels ]
        pixels.reverse()
        i = Image.new('RGB', self.size)
        i.putdata(pixels) # putdata oczekuje [ (255,255,0), ... ]
        i.transpose(FLIP_LEFT_RIGHT).save(genome.pngPath)
        #i.save(genome.pngPath)
    def renderToFile(self, genome):
        do('python lib/renderer/opengl.py '+genome.serial)

    def renderToScreen(self, genome):
        global meshData
        meshData = genome.data
        main(self.size)



def renderToMemory(self, genome):
        return getPixelData(size, genome.data)

if __name__ == '__main__':
    renderer = OpenglRenderer()
    sys.path.append('.')
    renderer._renderToFile(pickle.load(open('population_ram/'+sys.argv[1]+'_genome.obj')))