from stv.tools import FileTools
import unittest


class FileToolsTestSuite(unittest.TestCase):
    def test_add_extension(self):
        self.assertEqual(FileTools.add_extension("file", "ext"), "file.ext")
        self.assertEqual(FileTools.add_extension("file.ext", "ext"), "file.ext")


if __name__ == '__main__':
    unittest.main()
