import argparse
from unittest import TestLoader, TextTestRunner
from genetics.accuracy import AccuracyMachine
from genetics.population import Population
from genetics.genome import *
from lib.renderer.blender import BlenderRenderer
from lib.config import readConfig
from lib.log import initLogger
from lib.renderer.opengl_renderer import OpenglRenderer


def initRamDir(basePath, ramPath):
    tmp = ramPath
    if tmp[-1]=='/':
        tmp = tmp[0:-1]
    if do('mount | grep %s'% tmp, True):
        do('mkdir %s' % ramPath)
        do('sudo mount -osize=254m tmpfs %s -t tmpfs' % ramPath, False, True)
        do('cp -r %s/* %s'%(basePath, ramPath))

def closeRamDir(basePath, ramPath):
    do('rm -rf %s/*' % basePath, False)
    do('cp -r %s/* %s'%(ramPath, basePath), False)
from lib import dl
dl.trace_start("trace.html")
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', metavar='COMMAND', help='command: init, evolve, tests')
    parser.add_argument('-c', '--config', metavar='CONFIG', help='config file')
    args = parser.parse_args()

    if args.command == 'tests':
        suite = TestLoader().discover('tests', pattern='*.py')
        result = TextTestRunner(verbosity=2).run(suite)
        result = 0 if result.wasSuccessful() else 1
        exit(result)

    cfg = readConfig(args.config)
    logger = initLogger()
    initRamDir(cfg['main']['populationPath'], cfg['main']['populationRamPath'])

    renderer = OpenglRenderer()
    renderer = BlenderRenderer()
    fitnessMachine = MeshFitnessMachine(cfg['main']['baseImage'], renderer)
    pop = Population(MeshGenome, fitnessMachine)

    accuracyMachine = AccuracyMachine()
    pop.add_event_listener('calculatedFitness', accuracyMachine.onCalculatedFitness)
    pop.add_event_listener('lastGeneration', accuracyMachine.onLastGeneration)

    if args.command == 'init':
        pop.initialize()
    elif args.command == 'evolve':
        pop.load()

    try:
        pop.evolve()
    except KeyboardInterrupt as ki:
        pass

    closeRamDir(cfg['main']['populationPath'], cfg['main']['populationRamPath'])

    best = pop.getBestGenome()
    print(best.serial, best.fitness)
