from stv.tools import ListTools
import unittest


class ArrayToolsTestSuite(unittest.TestCase):
    def test_unique(self):
        array = [1, 2, 3, 1, 2, 3]
        ListTools.unique(array)
        self.assertEqual(len(array), 3)

    def test_count_not_none(self):
        array = [1, 2, None, 3, 4, None, None]
        count = ListTools.count_not_none(array)
        self.assertEqual(count, 4)


if __name__ == '__main__':
    unittest.main()
