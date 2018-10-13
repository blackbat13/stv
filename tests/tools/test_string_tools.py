import unittest
from tools.string_tools import StringTools


class TestStringTools(unittest.TestCase):
    def test_capitalize_first_letter(self):
        self.assertEqual(StringTools.capitalize_first_letter('ala'), 'Ala')


if __name__ == '__main__':
    unittest.main()
