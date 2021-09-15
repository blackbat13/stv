from stv.models.synchronous.drone_model import DroneModel, CracowMap


class DroneModelExperiments:
    def __init__(self, no_drones: int, energies, map):
        self.no_drones = no_drones
        self.energies = energies
        self.map = map
        self.model = None
        self.atl_imperfect_model = None

    def run_experiments(self):
        self.generate_model()
        winning = []

        state_id = -1

        for state in self.model.states:
            state_id += 1
            if len(state['visited'][0]) == len(self.model.graph):
                winning.append(state_id)
                print(state)

        result = self.atl_imperfect_model.minimum_formula_many_agents([0], winning)

        print(result)
        self.model.listify_states()
        print(self.model.model.js_dump_model())

    def generate_model(self):
        self.model = DroneModel(self.no_drones, self.energies, self.map)
        self.model.generate()
        self.atl_imperfect_model = self.model.model.to_atl_imperfect(self.model.get_actions())


if __name__ == "__main__":
    drone_model_experiments = DroneModelExperiments(1, [1], CracowMap())
    drone_model_experiments.run_experiments()
