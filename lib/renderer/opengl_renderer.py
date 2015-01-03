import os
import pickle
from lib.common import do
from lib.renderer.base import BaseRenderer


class OpenglRenderer(BaseRenderer):
    def __init__(self):
        super(OpenglRenderer, self).__init__()

    def renderToFile(self, genome):
        # proces
        pickle.dump(genome.data, open(genome.dataPath, 'wb'))
        do('python lib/renderer/opengl.py %s file 2>&1 >> %s' % (genome.dataPath, genome.logPath))

        # watek
        # opengl.render_now(genome.pngPath, genome.data)

        if not os.path.exists(genome.pngPath):
            raise Exception('Opengl failed to render image %s' % genome.pngPath)

    def renderToMemory(self, genome):
        self.renderToFile(genome)
        return _imageData(Image.open(genome.pngPath))
