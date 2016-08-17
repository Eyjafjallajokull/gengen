import os
import zerorpc
import pickle
from PIL import Image


class DistributedRenderer(object):
    def render_to_file(self, genome):
        c = zerorpc.Client()
        c.connect("tcp://renderer:4242")
        image_pickle = c.render(genome.serial, genome.data, genome.pngPath)
        image = pickle.loads(image_pickle)
        image.save(genome.pngPath)
        c.close()
        if not os.path.exists(genome.pngPath):
            raise Exception('DistributedRenderer failed to render image %s' % genome.pngPath)
        return True


