from stv.tools import DisjointSet
import unittest


class DisjointSetTestSuite(unittest.TestCase):
    def test_sanity(self):
        DisjointSet(5)


if __name__ == '__main__':
    unittest.main()
