from stv.models.asynchronous.parser import GlobalModelParser
import unittest


class GlobalModelParserTestSuite(unittest.TestCase):
    def test_sanity(self):
        GlobalModelParser()


if __name__ == '__main__':
    unittest.main()
