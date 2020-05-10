from stv.models.tian_ji_model import TianJiModel


class TianJiModelExperiments:
    def __init__(self, no_horses: int):
        self.no_horses = no_horses
        self.model = None

    def run_experiments(self):
        self.generate_model()
        atl_model = self.model.model.to_atl_imperfect(self.model.get_actions())

        winning = []

        state_id = -1

        for state in self.model.states:
            state_id += 1
            if state['tian_ji_score'] > state['king_score'] and len(state['tian_ji_horses']) == 0:
                winning.append(state_id)

        result = atl_model.minimum_formula_many_agents([0], winning)

        print(result)

    def generate_model(self):
        self.model = TianJiModel(self.no_horses)
        self.model.generate()


if __name__ == "__main__":
    tian_ji_model_experiments = TianJiModelExperiments(4)
    tian_ji_model_experiments.run_experiments()
