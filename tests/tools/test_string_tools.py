import unittest
from ..context import tools


class StringToolsTestSuite(unittest.TestCase):
    def test_capitalize_first_letter(self):
        self.assertEqual(tools.StringTools.capitalize_first_letter('ala'), 'Ala')


if __name__ == '__main__':
    unittest.main()
