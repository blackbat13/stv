from stv.models import DroneModel, CracowMap
import unittest


class DroneModelTestSuite(unittest.TestCase):
    def test_sanity(self):
        model = DroneModel(2, [2, 2], CracowMap())
        model.generate()


if __name__ == '__main__':
    unittest.main()
