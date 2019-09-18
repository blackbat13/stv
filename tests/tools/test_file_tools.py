import unittest
from tools.file_tools import FileTools


class TestFileTools(unittest.TestCase):
    def test_add_extension(self):
        self.assertEqual(FileTools.add_extension("file", "ext"), "file.ext")
        self.assertEqual(FileTools.add_extension("file.ext", "ext"), "file.ext")


if __name__ == '__main__':
    unittest.main()
