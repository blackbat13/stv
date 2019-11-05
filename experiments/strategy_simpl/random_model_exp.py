from models.random_model import *
from comparing_strats.strat_simpl import StrategyComparer
from typing import List
import datetime


class RandomModelExp:
    def __init__(self, model_size: int, exp_count: int, DEBUG: bool = False):
        self.__exp_count = exp_count
        self.__DEBUG = DEBUG
        self.__model_size = model_size

    def run_experiments(self):
        for _ in range(self.__exp_count):
            self._run_experiment()
            print()
            print()

    def _run_experiment(self):
        random_model = RandomModel(self.__model_size)
        random_model.generate()
        print("-------------------PERFECT INFORMATION STRATEGY-------------------")
        strategy = self._generate_perfect_information_strategy(random_model)
        print("-------------------SIMPLIFIED STRATEGY-------------------")
        simplified_strategy = self._generate_simplified_strategy(random_model, strategy)
        print("-------------------DOMINO DFS-------------------")
        self._run_domino_dfs(random_model)

    def _run_domino_dfs(self, model: RandomModel):
        winning_states = model.get_winning_states("win")
        strategy_comparer = StrategyComparer(model.model, model.get_actions()[0])
        (result, strategy) = strategy_comparer.domino_dfs(0, set(winning_states), [0], strategy_comparer.basic_h)
        print(f'Strategy result: {result}')
        print(strategy)
        if self.__DEBUG:
            self._print_strategy(strategy)

    def _print_strategy(self, strategy):
        for index, value in enumerate(strategy):
            if value is not None:
                print(f"{index}: {value}")

    def _generate_perfect_information_strategy(self, model: RandomModel):
        winning_states = model.get_winning_states("win")
        strategy_comparer = StrategyComparer(model.model, model.get_actions()[0])
        strategy = strategy_comparer.generate_winning_strategy_perfect_information(0, list(winning_states))
        defined_in = 0
        # if strategy[0] is None:
        #     print("Not winning")
        #     return

        print("Strategy result:", strategy[0] is not None)
        print(strategy)
        if self.__DEBUG:
            self._print_strategy(strategy)
        for index, value in enumerate(strategy):
            if value is not None:
                defined_in += 1
        epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0, strategy)
        print("Non control states in strategy:", strategy_comparer.count_non_control_states(0, strategy))
        print("Epistemic mismatch for random strategy: ", epistemic_mismatch)
        print("Random strategy defined in", defined_in, "states")
        return strategy

    def _generate_simplified_strategy(self, model: RandomModel, strategy):
        strategy_comparer = StrategyComparer(model.model, model.get_actions()[0])
        simplified_strategy = strategy_comparer.simplify_strategy_one_agent(0, strategy, None)
        print(simplified_strategy)
        if self.__DEBUG:
            self._print_strategy(simplified_strategy)
        print("Different: ", simplified_strategy != strategy)
        defined_in = 0
        for index, value in enumerate(simplified_strategy):
            if value is not None:
                # print(f"{index}: {value}")
                defined_in += 1

        epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0, simplified_strategy)
        print("Non control states in strategy:", strategy_comparer.count_non_control_states(0, simplified_strategy))
        print("Epistemic mismatch for simplified strategy: ", epistemic_mismatch)
        print("Simpified strategy defined in", defined_in, "states")
        return simplified_strategy


random_model_exp = RandomModelExp(model_size=20, exp_count=5)
random_model_exp.run_experiments()
