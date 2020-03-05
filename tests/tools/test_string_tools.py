import unittest
from ..context import tools


class StringToolsTestSuite(unittest.TestCase):
    def test_capitalize_first_letter(self):
        self.assertEqual(tools.StringTools.capitalize_first_letter('ala'), 'Ala')

    def test_is_blank_line(self):
        self.assertEqual(tools.StringTools.is_blank_line("    "), True)

    def test_not_is_blank_line(self):
        self.assertEqual(tools.StringTools.is_blank_line("   a   "), False)


if __name__ == '__main__':
    unittest.main()
