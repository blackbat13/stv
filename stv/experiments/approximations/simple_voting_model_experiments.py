from stv.models.synchronous.simple_voting_model import SimpleVotingModel


class SimpleVotingModelExperiments:
    def __init__(self, no_candidates: int, no_voters: int):
        self.no_candidates = no_candidates
        self.no_voters = no_voters
        self.model = None

    def run_experiments(self):
        self.generate_model()
        self.model.model.simulate(0)

    def generate_model(self):
        self.model = SimpleVotingModel(self.no_candidates, self.no_voters)
        self.model.generate()


if __name__ == "__main__":
    simple_voting_model_experiments = SimpleVotingModelExperiments(2, 2)
    simple_voting_model_experiments.run_experiments()
