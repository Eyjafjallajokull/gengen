import argparse
from unittest import TestLoader, TextTestRunner
from plugins import accuracy, monitor
from genetics.population import Population
from genetics.genome import *
from lib.config import read_config
from lib.log import init_logger
from lib.renderer import DistributedRenderer
from lib.qualifier import DistributedQualifier
from lib.common import do
from lib import db
from os.path import basename

# from lib import dl
# dl.trace_start("trace.html",interval=5,auto=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', metavar='COMMAND', help='command: init, tests')
    parser.add_argument('-c', '--config', metavar='CONFIG', help='config file')
    args = parser.parse_args()

    if args.command == 'tests':
        suite = TestLoader().discover('tests', pattern='*.py')
        result = TextTestRunner(verbosity=2).run(suite)
        result = 0 if result.wasSuccessful() else 1
        exit(result)

    cfg = read_config(args.config)
    logger = init_logger()

    renderer = DistributedRenderer()
    qualifier = DistributedQualifier()
    base_image_path = cfg['main']['populationPath'] + basename(cfg['main']['baseImage'])
    fitnessMachine = MeshFitnessMachine(base_image_path, renderer, qualifier)
    population = Population(MeshGenome, fitnessMachine)
    population.generation = int(db.get('generation', default=0))

    accuracy.register(population)
    monitor.register(population)

    if args.command == 'reset' or not population.generation:
        population.initialize()
    else:
        population.load()
    do('cp -v %s %s' % (cfg['main']['baseImage'], base_image_path))

    try:
        population.evolve()
    except KeyboardInterrupt as ki:
        pass

    best = population.get_best_genome()
    print(best.serial, best.fitness)

