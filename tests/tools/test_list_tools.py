import unittest
from ..context import tools


class ArrayToolsTestSuite(unittest.TestCase):
    def test_create_integer_array_of_size(self):
        array = tools.ListTools.create_value_list_of_size(10, 1)
        self.assertEqual(len(array), 10)
        self.assertEqual(array[0], 1)

    def test_unique(self):
        array = [1,2,3,1,2,3]
        tools.ListTools.unique(array)
        self.assertEqual(len(array), 3)

    def test_count_not_none(self):
        array = [1,2,None,3,4,None,None]
        count = tools.ListTools.count_not_none(array)
        self.assertEqual(count, 4)


if __name__ == '__main__':
    unittest.main()