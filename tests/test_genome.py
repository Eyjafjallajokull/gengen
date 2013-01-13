import copy
import os
from tests.test_base import TestBase
from genetics.genome import Genome, MeshGenome

class TestGenome(TestBase):
    def setUp(self):
        self.initConfig('basic')
        self.object = Genome()

    def tearDown(self):
        self.object.remove()

    def test_save(self):
        self.object.save()
        self.assertTrue(os.path.exists(self.object.objPath))

    def test_remove(self):
        self.object.save()
        self.object.remove()
        self.assertFalse(os.path.exists(self.object.objPath))

    def test_create(self):
        self.object.dataModified = False
        self.object.create()
        self.assertTrue(self.object.dataModified)

    def test_createWithCrossover(self):
        with self.assertRaises(ValueError):
            self.object.createWithCrossover(None, None)

    def test_mutate(self):
        self.object.dataModified = False
        self.object.mutate()
        self.assertTrue(self.object.dataModified)

    def test_setFitness(self):
        self.object.dataModified = True
        self.object.setFitness(123)
        self.assertFalse(self.object.dataModified)
        self.assertEqual(self.object.fitness, 123)

class TestMeshGenome(TestBase):
    def setUp(self):
        self.initConfig('basic')
        self.object = MeshGenome()

    def tearDown(self):
        self.object.remove()

    def test_init(self):
        self.assertIsNotNone(self.object.blendPath)
        self.assertIsNotNone(self.object.dataPath)
        self.assertIsNotNone(self.object.pngPath)

    def assert_data(self, data):
        self.assertEqual(len(data), self.cfg['ga']['genomeSize'])
        self.assertEqual(len(data[0]), 3)
        self.assertEqual(len(data[0][0]), 3)
        self.assertNotEqual(self.object.data[0], self.object.data[-1])
        for object in data:
            for point in object:
                for coord in [0,1,2]:
                    self.assertIsInstance(point[coord], float)
                    self.assertTrue(abs(point[coord])<self.object.meshConstraints[coord])

    def test__create(self):
        self.object._create()
        self.assert_data(self.object.data)

    def test__mutate(self):
        self.object.create()
        notMutatedData = copy.deepcopy(self.object.data)
        self.object.mutate()
        mutatedData = self.object.data
        self.assert_data(mutatedData)

        expectedMutatedObjects = self.cfg['ga']['mutationObjectCountMultiplier'] * self.cfg['ga']['genomeSize']
        expectedMutatedPoints = self.cfg['ga']['mutationPointCount']
        expectedMutatedCoordinates = self.cfg['ga']['mutationCoordinateCount']
        mutatedObjects = 0
        mutatedPoints = 0
        mutatedCoordinates = 0

        for i, object in enumerate(self.object.data):
            anyPointMutated = False
            for j, point in enumerate(object):
                anyCoordinateMutated = False
                for k, coordinate in enumerate(point):
                    if coordinate != notMutatedData[i][j][k]:
                        mutatedCoordinates+=1
                        anyCoordinateMutated = True
                if anyCoordinateMutated:
                    mutatedPoints+=1
                    anyPointMutated = True
            if anyPointMutated:
                mutatedObjects+=1

        self.assertEqual(expectedMutatedObjects, mutatedObjects)
        self.assertEqual(expectedMutatedPoints*expectedMutatedObjects, mutatedPoints)
        self.assertEqual(expectedMutatedCoordinates*expectedMutatedPoints*expectedMutatedObjects,
            mutatedCoordinates)