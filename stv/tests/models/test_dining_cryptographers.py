from stv.models import DiningCryptographers
import unittest


class DiningCryptographersTestSuite(unittest.TestCase):
    def test_sanity(self):
        model = DiningCryptographers(3)
        model.generate()


if __name__ == '__main__':
    unittest.main()
