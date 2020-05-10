from stv.models.drone_model import *
from stv.comparing_strats.strategy_comparer import StrategyComparer
from typing import List
import datetime


class DroneStrExp:
    def __init__(self, no_drones: int, energies: List[int], DEBUG: bool = False):
        self.no_drones = no_drones
        self.energies = energies
        self.DEBUG = DEBUG

    def run_experiments(self):
        print(datetime.datetime.now())
        print(self.no_drones, self.energies)
        drone_model = DroneModel(no_drones=self.no_drones, energies=self.energies, map=CracowMap(), is_random=False)
        drone_model.generate()
        no_states = len(drone_model.states)
        print(f"Model have {no_states} states")

        winning_states = []
        max_visited = 0

        for i, state in enumerate(drone_model.states):
            if self.DEBUG:
                print(state)
            visited = set()
            for vis in state['visited']:
                visited.update(vis)
            if len(visited) > max_visited:
                max_visited = len(visited)

        for i, state in enumerate(drone_model.states):
            visited = set()
            for vis in state['visited']:
                visited.update(vis)
            if len(visited) >= max_visited:
                if self.DEBUG:
                    print(f'Winning state: {state}')
                winning_states.append(i)

        if self.DEBUG:
            print(f'Max visited: {max_visited}')
            print(f'Number of winning states: {len(winning_states)}')

        strategy_comparer = StrategyComparer(drone_model.model, ['N', 'S', 'W', 'E', 'Wait'])
        strategy = strategy_comparer.generate_winning_strategy_perfect_information(0, winning_states)
        # (result, strategy) = strategy_comparer.domino_dfs(0, set(winning_states), [0], strategy_comparer.basic_h)
        # print(f'Strategy result: {result}')
        defined_in = 0
        print(strategy)
        for index, value in enumerate(strategy):
            if value is not None:
                print(f"{index}: {value}")
                defined_in += 1

        epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0, strategy)
        print("Epistemic mismatch for random strategy: ", epistemic_mismatch)
        print("Random strategy defined in", defined_in, "states")

        simplified_strategy = strategy_comparer.simplify_strategy_one_agent(0, strategy, strategy_comparer.basic_h)
        print(simplified_strategy)
        defined_in = 0
        for index, value in enumerate(simplified_strategy):
            if value is not None:
                print(f"{index}: {value}")
                defined_in += 1

        epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0, simplified_strategy)
        print("Epistemic mismatch for simplified strategy: ", epistemic_mismatch)
        print("Simpified strategy defined in", defined_in, "states")


if __name__ == "__main__":
    drone_str_exp = DroneStrExp(no_drones=1, energies=[3], DEBUG=True)
    drone_str_exp.run_experiments()
