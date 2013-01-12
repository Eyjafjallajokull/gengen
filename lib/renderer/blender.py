import json
from base import BaseRenderer
from lib.common import do
import os
from lib.image import _imageData
from PIL import Image
import pickle
import lib.config as config

class BlenderRenderer(BaseRenderer):
    def __init__(self):
        self.baseBlendPath = config.config['main']['baseBlendPath']

    def renderToFile(self, genome):
        pickle.dump(genome.data, open(genome.dataPath, 'wb'))
        do('cp %s %s' % (self.baseBlendPath, genome.blendPath))
        tmpPngPath = '/tmp/%s' % genome.serial
        tmpPngFullPath = '/tmp/%s0000.png' % genome.serial
        do('rm -f %s' % tmpPngFullPath)
        blenderReturn = do('params=\'%s\' blender -b "%s" -P lib/renderer/blenderCreateMesh.py -o %s -F PNG -t 6 -f 0 > "%s" 2>&1' %
           (json.dumps({'genomeSerial':genome.serial, 'config':config.config}), genome.blendPath, tmpPngPath, genome.logPath), True)
        if blenderReturn!=0:
            raise Exception('blender failed %s'%genome.logPath)
        if do('grep "Traceback (most recent call last):" %s' % genome.logPath, True)==0 or do('grep "SyntaxError" %s' % genome.logPath, True)==0:
            raise Exception('python error in blender script: %s' % genome.logPath)

        if not os.path.exists(tmpPngFullPath):
            raise Exception('Blender failed to render image %s'%genome.logPath)
        do('cp %s %s' % (tmpPngFullPath, genome.pngPath))


    def renderToMemory(self, genome):
        self.renderToFile(genome)
        return _imageData(Image.open(genome.pngPath))