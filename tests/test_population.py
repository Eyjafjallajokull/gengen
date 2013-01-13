from genetics.population import Population
from genetics.genome import TestGenome
from tests.test_base import TestBase

class TestPopulation(TestBase):
    genomeType = TestGenome

    def setUp(self):
        self.initConfig('basic')
        self.initLog()
        self.population = Population(self.genomeType)
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
