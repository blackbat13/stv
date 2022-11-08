from stv.models.synchronous import SimpleVotingModel
import unittest


class SimpleVotingModelTestSuite(unittest.TestCase):
    def testSanity(self):
        model = SimpleVotingModel(number_of_candidates=2, number_of_voters=2)
        model.generate()

    def setUp(self) -> None:
        self.simpleVotingModel = SimpleVotingModel(number_of_candidates=2, number_of_voters=2)
        self.simpleVotingModel.generate()

        self.atliRModel = self.simpleVotingModel.model.to_atl_imperfect()


if __name__ == '__main__':
    unittest.main()
