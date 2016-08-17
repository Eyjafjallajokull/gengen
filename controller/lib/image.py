import os
import pickle
import numpy
# from PIL import Image

cache = None

processPixelStep = 10

def _imageData(img):
    bands = img.getbands()
    if len(bands) == 1:
        return [ numpy.array([i for i in list(img.getdata())]) ]
    else:
        # 3 kanaly (RGB)
        #return [ numpy.array([i[band_index] for i in list(img.getdata())[::processPixelStep]]) for band_index, _ in enumerate(bands) ]

        # suma wartosci z 3 kanalow
        return numpy.array([sum(i) for i in list(img.getdata())])

def _diffImages(m1, m2):
    if len(m1) != len(m2):
        raise Exception('_diffImages failed, arrays of different length %d,%d'%(len(m1),len(m2)))
    if len(m1) == 3 and isinstance(m1[0], list): # 3 kanaly koloru, prawdopodobnie do poprawienie 2 warunek
        if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
            return -1
        s = 0
        for band_index in range(len(m1)):
            s += numpy.sum(numpy.abs(m1[band_index] - m2[band_index]))
    else:
        try:
            s = numpy.sum(numpy.abs(numpy.array(m1[::processPixelStep]) - numpy.array(m2[::processPixelStep])))
        except TypeError as e:
            print('m',m1,m2)
            raise e
    return s

def compare(original, test):
    ''' Im mniejsza liczba tym bardziej obrazy sa podobne do siebie '''
    return 1
    global cache
    if cache==None:
        cacheFile = 'tmp' + os.sep + original.replace('/', '_') + '.cache'
        if os.path.exists(cacheFile):
            cache = pickle.load(open(cacheFile))
        else:
            img = Image.open(original)
            cache = _imageData(img)
            pickle.dump(cache, open(cacheFile, 'w'))
    diff = _diffImages(cache, _imageData(Image.open(test)))
    return diff

#print compare('cmpOriginale.png','cmpOriginale.png')
#print compare('cmpOriginale.png','cmpTest1.png')
#print compare('cmpOriginale.png','cmpTest2.png')
#print compare('cmpOriginale.png','cmpTest3.png')
