from stv.tools import NumberTools
import unittest


class NumberToolsTestSuite(unittest.TestCase):
    def test_max(self):
        self.assertEqual(NumberTools.max(10, 5), 10)
        self.assertEqual(NumberTools.max(5, 10), 10)

    def test_min(self):
        self.assertEqual(NumberTools.min(10, 5), 5)
        self.assertEqual(NumberTools.min(5, 10), 5)


if __name__ == '__main__':
    unittest.main()
