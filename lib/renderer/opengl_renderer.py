import os
import pickle
from lib.common import do
from lib.renderer.base import BaseRenderer
import socket


class OpenglRenderer(BaseRenderer):
    def __init__(self):
        super(OpenglRenderer, self).__init__()

    def renderToFile(self, genome):
        # proces
        # pickle.dump(genome.data, open(genome.dataPath, 'wb'))
        # do('python lib/renderer/opengl.py %s file 2>&1 >> %s' % (genome.dataPath, genome.logPath))

        # serwer renderowania
        pickle.dump(genome.data, open(genome.dataPath, 'wb'))
        HOST, PORT = "localhost", 6010
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((HOST, PORT))
            sock.sendall(str(genome.dataPath) + "\n")
            sock.recv(1024)
        finally:
            sock.close()

        if not os.path.exists(genome.pngPath):
            raise Exception('Opengl failed to render image %s' % genome.pngPath)

    def renderToMemory(self, genome):
        self.renderToFile(genome)
        return _imageData(Image.open(genome.pngPath))
