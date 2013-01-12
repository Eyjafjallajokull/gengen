import logging
import unittest
from genetics.population import Population
from genetics.genome import TestGenome
from lib.config import readConfig


class TestPopulation(unittest.TestCase):
    genomeType = TestGenome

    def setUp(self):
        self.cfg = readConfig('tests/fixtures/config/basic.yml')
        logger = logging.getLogger('population')
        logger.addHandler(logging.NullHandler())
        self.population = Population(self.genomeType, logger)
        self.population.pool._processes = 1

    def test_load_init(self):
        self.assertEqual(len(self.population.genomes), 0)
        self.population.initialize()
        self.assertEqual(len(self.population.genomes), self.cfg['ga']['populationSize'])
        self.assertNotEqual(self.population.genomes[0], self.population.genomes[1])

    def test_selection(self):
        self.population.initialize()
        selected = self.population.selection()
        self.assertLess(len(selected), len(self.population.genomes))
        self.assertTrue(self.population.getBestGenome() in selected)
