from stv.models import BridgeModel
import unittest


class BridgeModelTestSuite(unittest.TestCase):
    def test_sanity(self):
        n = 1
        model = BridgeModel(n, n, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                   'hands': BridgeModel.generate_random_hands(n, n), 'next': 0,
                                   'history': [],
                                   'beginning': 0, 'clock': 0, 'suit': -1})
        model.generate()


if __name__ == '__main__':
    unittest.main()
