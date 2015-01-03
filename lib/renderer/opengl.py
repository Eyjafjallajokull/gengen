from pyglet.gl import *
from PIL import Image
from sys import argv
import pyglet
import pickle
import numpy


def vec(*args):
    return (GLfloat * len(args))(*args)


def setup(visible=False):
    global window
    window = pyglet.window.Window(320, 240, caption='POMPA', resizable=False, visible=visible)
    window.on_resize = on_resize
    window.on_draw = on_draw

    glClearColor(1, 1, 1, 1)
    glColor3f(.5, .5, .5)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_CULL_FACE) # if this is set: vertex direction matters
    glFrontFace(GL_CW)
    glCullFace(GL_BACK)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) # render mesh
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT)

    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, vec(0, 0, 0, 1.0))

    glLightfv(GL_LIGHT0, GL_POSITION, vec(0, .5, .5, 0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, vec(0.5, 0.5, 0.5, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(1, 1, 1, 1))
    # glLightfv(GL_LIGHT0, GL_SPOT_CUTOFF, GLfloat(30.0))
    # glLightfv(GL_LIGHT0, GL_SPOT_EXPONENT, GLfloat(60.0))
    # glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, vec(0, -12, -2))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(1, 1, 1, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, vec(0, 0, 0, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)


def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(35., width / float(height), 0.1, 100.)
    glMatrixMode(GL_MODELVIEW)


def triangle_normal(triangle):
    v = [triangle[1][i] - triangle[0][i] for i in range(3)]
    u = [triangle[2][i] - triangle[0][i] for i in range(3)]
    nx = u[1]*v[2] - u[2]*v[1]
    ny = u[2]*v[0] - u[0]*v[2]
    nz = u[0]*v[1] - u[1]*v[0]
    glNormal3f(nx, ny, nz)

    # if dot_product(normal, ??) > 0: then swap vertices and recalculate normal
    # if sum(p*q for p, q in zip((nx, ny, nz), (0, 0, 1))) > 0:
    #     triangle_normal([triangle[1], triangle[0], triangle[2]])


def triangle_fix_order(triangle):
    maximums = numpy.argmax(triangle, axis=0)
    top = triangle[maximums[1]]
    del triangle[maximums[1]]
    maximums = numpy.argmax(triangle, axis=0)
    right = triangle[maximums[0]]
    del triangle[maximums[0]]
    return [top, right, triangle[0]]


def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -16)

    for triangle in data:
        if len(triangle) < 3:
            continue
        glBegin(GL_TRIANGLES)
        # triangle = triangle_fix_order(triangle)
        triangle_normal(triangle)
        for vertex in triangle:
            glVertex3f(*vertex)
        glEnd()


def save_and_exit(dt):
    print 'saving %s' % target_file
    buffer = (GLubyte * (3 * window.width * window.height))(0)
    glReadPixels(0, 0, window.width, window.height, GL_RGB, GL_UNSIGNED_BYTE, buffer)
    image = Image.frombytes(mode="RGB", size=(window.width, window.height), data=buffer)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(target_file)
    window.close()


def read_data_from_file():
    global target_file, data
    source_file = argv[1]
    target_file = source_file.replace('_data.obj', '.png')
    data = pickle.load(open(source_file, 'r'))
    print 'read %d objects' % len(data)


def render_to_file():
    pyglet.clock.schedule_once(save_and_exit, 0.05)


def render_to_screen():
    def on_key_press(symbol, modifiers):
        save_and_exit(None)
    window.push_handlers(on_key_press)


def render_now(target, genome_data):
    global target_file, data
    target_file = target
    data = genome_data
    setup(visible=True)
    render_to_file()
    pyglet.app.run()



target_file = None
data = None
window = None

if __name__ == '__main__':
    read_data_from_file()
    if argv[2] == 'file':
        setup(visible=True)
        render_to_file()
    else:
        setup(visible=True)
        render_to_screen()
    pyglet.app.run()

