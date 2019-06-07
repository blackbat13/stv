from simple_models.simple_voting_model import SimpleVotingModel

simple_voting = SimpleVotingModel(2, 2)
simple_voting.generate()
simple_voting.model.simulate(0)