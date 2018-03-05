import unittest
from tools.array_tools import ArrayTools


class TestArrayTools(unittest.TestCase):
    def test_create_array_of_size(self):
        array = ArrayTools.create_array_of_size(10, [])
        self.assertEqual(len(array), 10)
        self.assertEqual(len(array[0]), 0)

    def test_create_integer_array_of_size(self):
        array = ArrayTools.create_value_array_of_size(10, 1)
        self.assertEqual(len(array), 10)
        self.assertEqual(array[0], 1)

    def test_unique(self):
        array = [1,2,3,1,2,3]
        ArrayTools.unique(array)
        self.assertEqual(len(array), 3)


if __name__ == '__main__':
    unittest.main()