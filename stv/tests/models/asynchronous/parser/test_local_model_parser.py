from stv.models.asynchronous.parser import LocalModelParser
import unittest


class LocalModelParserTestSuite(unittest.TestCase):
    def test_sanity(self):
        LocalModelParser()


if __name__ == '__main__':
    unittest.main()
