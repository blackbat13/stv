import unittest
from tools.list_tools import ListTools


class TestArrayTools(unittest.TestCase):
    def test_create_array_of_size(self):
        array = ListTools.create_array_of_size(10, [])
        self.assertEqual(len(array), 10)
        self.assertEqual(len(array[0]), 0)

    def test_create_integer_array_of_size(self):
        array = ListTools.create_value_array_of_size(10, 1)
        self.assertEqual(len(array), 10)
        self.assertEqual(array[0], 1)

    def test_unique(self):
        array = [1,2,3,1,2,3]
        ListTools.unique(array)
        self.assertEqual(len(array), 3)

    def test_count_not_none(self):
        array = [1,2,None,3,4,None,None]
        count = ListTools.count_not_none(array)
        self.assertEqual(count, 4)


if __name__ == '__main__':
    unittest.main()