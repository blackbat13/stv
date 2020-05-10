from stv.models import CastleModel
import unittest


class CastleModelTestSuite(unittest.TestCase):
    def test_sanity(self):
        castle_model = CastleModel([1, 1, 1], [1, 1, 1])
        castle_model.generate()


if __name__ == '__main__':
    unittest.main()
