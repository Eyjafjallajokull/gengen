from multiprocessing import Queue
from threading import Thread
from PIL import Image
from Queue import Empty
from pyglet.gl import *
import pickle
import numpy
import pyglet
import zerorpc
import time


def vec(*args):
    return (GLfloat * len(args))(*args)


def setup():
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


def on_draw(data_index=0):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -16)

    for triangle in data:
    # for triangle in datas[data_index]:
        if len(triangle) < 3:
            continue
        glBegin(GL_TRIANGLES)
        # triangle = triangle_fix_order(triangle)
        triangle_normal(triangle)
        for vertex in triangle:
            glVertex3f(*vertex)
        glEnd()


def save(png_path):
    get_image().save(png_path)


def get_image():
    window_buffer = (GLubyte * (3 * window.width * window.height))(0)
    glReadPixels(0, 0, window.width, window.height, GL_RGB, GL_UNSIGNED_BYTE, window_buffer)
    image = Image.frombytes(mode="RGB", size=(window.width, window.height), data=window_buffer)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return image


class RPCServer(object):
    def __init__(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue

    def render(self, serial, point_data, png_path):
        print("Received %s" % serial)
        self.input_queue.put((serial, point_data, png_path))
        result = False
        while True:
            try:
                result = self.output_queue.get(True, 1)
                time.sleep(0.2)
            except Empty:
                pass
            if result:
                break
        print "rendered", serial
        return result


def start_rpc_server(input_queue, output_queue):
    s = zerorpc.Server(RPCServer(input_queue, output_queue))
    s.bind("tcp://0.0.0.0:4242")
    print('Waiting for messages.')
    s.run()


def start_rpc_server_thread():
    input_queue = Queue()
    output_queue = Queue()

    server_thread = Thread(target=start_rpc_server, args=(input_queue, output_queue))
    server_thread.daemon = True
    server_thread.start()
    return input_queue, output_queue


target_file = None
data = []
window = None
server = None

if __name__ == '__main__':
    window = pyglet.window.Window(320, 240, caption='POMPA0', resizable=False)
    window.on_resize = on_resize
    window.on_draw = on_draw

    setup()
    input_queue_, output_queue_ = start_rpc_server_thread()

    pyglet.clock.tick()
    window.switch_to()
    window.dispatch_events()
    window.dispatch_event('on_draw')
    window.flip()

    while True:
        pyglet.clock.tick()

        for window in pyglet.app.windows:
            window.switch_to()
            (serial, data, png_path) = input_queue_.get()

            window.dispatch_events()
            window.dispatch_event('on_draw')
            window.flip()

            i = pickle.dumps(get_image())
            output_queue_.put(i)
