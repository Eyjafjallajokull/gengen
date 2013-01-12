import argparse
import sys
import logging
from unittest import TestLoader, TextTestRunner
from lib.config import readConfig
from genetics.population import Population
from genetics.genome import *
from lib.renderer.blender import BlenderRenderer

def initLogger():
    #todo: make logging config global
    rawFormatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s %(message)s')
    prettyFormatter = logging.Formatter('%(message)s')
    stdoutHandler = logging.StreamHandler(sys.stdout)
    stdoutHandler.setLevel(logging.INFO)
    stdoutHandler.setFormatter(prettyFormatter)
    fileHandler = logging.FileHandler('log.log')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(rawFormatter)
    logger = logging.getLogger('population')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdoutHandler)
    logger.addHandler(fileHandler)
    return logger

def initRamDir(basePath, ramPath):
    tmp = ramPath
    if tmp[-1]=='/':
        tmp = tmp[0:-1]
    if do('mount | grep %s'% tmp, True):
        do('mkdir %s' % ramPath)
        do('sudo mount -osize=100m tmpfs %s -t tmpfs' % ramPath, False, True)
        do('cp -r %s/* %s'%(basePath, ramPath))

def closeRamDir(basePath, ramPath):
    do('rm -rf %s/*' % basePath, False)
    do('cp -r %s/* %s'%(ramPath, basePath), False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', metavar='COMMAND', help='command: init, evolve, tests')
    parser.add_argument('-c','--config', metavar='CONFIG', default='config.yml', help='load alternative config file')
    #todo: add debug mode
#    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    args = parser.parse_args()

    if args.command=='tests':
        suite = TestLoader().discover('tests', pattern='*.py')
        TextTestRunner(verbosity=2).run(suite)
        exit(0)

    cfg = readConfig(args.config)
    logger = initLogger()
    initRamDir(cfg['main']['populationPath'], cfg['main']['populationRamPath'])

#    g = pickle.load(open('population_ram/1249448_genome.obj'))
#    br = BlenderRenderer(cfg['main']['baseBlendPath'])
#    br.renderToFile(g)
#    ogr = OpenglRenderer()
#    ogr.renderToScreen(g)
#    exit()

    br = BlenderRenderer()
    fm = MeshFitnessMachine(cfg['main']['baseImage'], br)
    p = Population(MeshGenome, logger)
    p.fitnessMachine = fm

    if args.command=='init':
        p.initialize()
    elif args.command=='evolve':
        p.load()

    try:
        p.evolve()
    except KeyboardInterrupt as ki:
        pass

    closeRamDir(cfg['main']['populationPath'], cfg['main']['populationRamPath'])

    best = p.getBestGenome()
    print(best.serial, best.fitness)
