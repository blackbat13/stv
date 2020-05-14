from stv.models.asynchronous.parser import LocalTransitionParser
import unittest


class LocalTransitionParserTestSuite(unittest.TestCase):
    def test_sanity(self):
        LocalTransitionParser()


if __name__ == '__main__':
    unittest.main()
