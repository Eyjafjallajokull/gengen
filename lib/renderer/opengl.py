import SocketServer
from multiprocessing import Queue
from threading import Thread, Lock
from PIL import Image
from sys import argv
from pyglet.gl import *
import pickle
import numpy
import pyglet


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


def save():
    buffer = (GLubyte * (3 * window.width * window.height))(0)
    glReadPixels(0, 0, window.width, window.height, GL_RGB, GL_UNSIGNED_BYTE, buffer)
    image = Image.frombytes(mode="RGB", size=(window.width, window.height), data=buffer)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(target_file)
    print 'saved', target_file


def save_and_exit(dt):
    save()
    window.close()


def read_data_from_file(source_file):
    global target_file, data
    source_file = '../../'+source_file
    target_file = source_file.replace('_data.obj', '.png')
    data = pickle.load(open(source_file, 'r'))


def render_to_file():
    pyglet.clock.schedule_once(save_and_exit, 0.05)


def render_to_screen():
    def on_key_press(symbol, modifiers):
        save_and_exit(None)
    window.push_handlers(on_key_press)


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.server.lock.acquire()
        data = self.request.recv(1024).strip()
        self.server.input_queue.put(data)

        while True:
            try:
                ndata = self.server.output_queue.get(True, 1)
            except self.server.output_queue.Empty:
                pass
            if ndata:
                break
            # self.server.lock.wait()

        print "response", data, ndata
        self.request.sendall("ok")
        self.server.lock.release()

def start_socket_server():
    HOST, PORT = "localhost", 6007
    print 'starting server at', PORT
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.allow_reuse_address = True
    server.input_queue = Queue()
    server.output_queue = Queue()
    server.lock = Lock()

    def _tmp():
        try:
            server.serve_forever()
        finally:
            server.shutdown()
    server_thread = Thread(target=_tmp)
    server_thread.daemon = True
    server_thread.start()

    return server


target_file = None
data = []
window = None
server = None

if __name__ == '__main__':
    if len(argv)==3:
        read_data_from_file(argv[1])
        if argv[2] == 'file':
            window = pyglet.window.Window(320, 240, caption='POMPA', resizable=False)
            window.on_resize = on_resize
            window.on_draw = on_draw
            setup()
            render_to_file()
        elif argv[2] == 'screen':
            window = pyglet.window.Window(320, 240, caption='POMPA', resizable=False)
            window.on_resize = on_resize
            window.on_draw = on_draw
            setup()
            render_to_screen()
        pyglet.app.run()
    else:
        window = pyglet.window.Window(320, 240, caption='POMPA0', resizable=False)
        window.on_resize = on_resize
        window.on_draw = on_draw

        # THREADS = 1
        #pyglet.app.windows
        # for i in range(1, THREADS):
        #     datas.append([])
        #     window = pyglet.window.Window(320, 240, caption='POMPA%d' % i, resizable=False, context=window.context)
        #     window.on_resize = on_resize
        #     window.on_draw = on_draw_index(i)
        # datas = [data[20:25], data[25:30], [], []]
        setup()
        server = start_socket_server()

        pyglet.clock.tick()
        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        window.flip()

        while True:
            pyglet.clock.tick()

            for window in pyglet.app.windows:
                window.switch_to()
                # server.lock.acquire()
                item = server.input_queue.get()
                read_data_from_file(item)

                window.dispatch_events()
                window.dispatch_event('on_draw')
                window.flip()

                save()
                server.output_queue.put(item)
                # server.lock.notify()
                # server.lock.release()
