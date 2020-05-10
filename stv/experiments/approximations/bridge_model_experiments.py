from stv.models.bridge_model import BridgeModel


class BridgeModelExperiments:
    def __init__(self, n: int):
        self.n = n
        self.model = None

    def run_experiments(self):
        self.generate_model()
        winning_states = self.model.get_winning_states("ns_win")
        atl_model = self.model.model.to_atl_imperfect(self.model.get_actions())
        result = atl_model.minimum_formula_many_agents([0], winning_states)
        print(result)
        print(atl_model.strategy)

    def generate_model(self):
        self.model = BridgeModel(self.n, self.n, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                                  'hands': BridgeModel.generate_random_hands(self.n, self.n), 'next': 0,
                                                  'history': [],
                                                  'beginning': 0, 'clock': 0, 'suit': -1})
        self.model.generate()


if __name__ == "__main__":
    bridge_model_experiments = BridgeModelExperiments(1)
    bridge_model_experiments.run_experiments()
