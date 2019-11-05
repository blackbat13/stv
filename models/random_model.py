from typing import List

from comparing_strats import StrategyComparer
from models.model_generator import ModelGenerator
from enum import Enum
import itertools
import random


class RandomModel(ModelGenerator):
    def __init__(self, max_states: int = 20):
        super().__init__(no_agents=2)
        self.__max_states = max_states
        self.__max_epistemic_classes = random.randint(self.__max_states // 4, self.__max_states // 2)
        self.__max_winning_states = random.randint(1, self.__max_states // 5)
        self.__path_length = random.randint(self.__max_states // 4, 3 * self.__max_states // 4)
        self.__paths_count = random.randint(self.__max_states * 2, self.__max_states * 4)
        self.__max_action = 1
        self.__random_connections_count = random.randint(self.__max_states // 4, self.__max_states * 4)
        self.state_epistemic_class = [random.randint(0, self.__max_epistemic_classes) for _ in
                                      range(self.__max_states + 1)]
        self.state_epistemic_class[0] = -1
        self.winning_states = [False for _ in range(self.__max_states + 1)]
        self.__paths: List[List[int]] = []
        self.__graph = [set() for _ in range(self.__max_states + 1)]

    def _generate_initial_states(self):
        self._add_state({'id': 0, 'epistemic_class': -1})

    def _generate_model(self):
        self._generate_paths()
        self._generate_winning_states()
        self._generate_random_connections()
        self._generate_transitions()

    def _generate_paths(self):
        state_dist = self.__max_states // self.__path_length
        for _ in range(self.__paths_count):
            path = [random.randint(0, state_dist)]
            for _ in range(self.__path_length):
                next_state = random.randint(path[-1] + 1, path[-1] + 1 + state_dist)
                if next_state >= self.__max_states:
                    break
                self.__graph[path[-1]].add(next_state)
                self.__max_action = max(self.__max_action, len(self.__graph[-1]))
                path.append(next_state)
            self.__paths.append(path[:])
        self.__max_action += 30

    def _generate_winning_states(self):
        for _ in range(self.__max_winning_states):
            self.winning_states[self.__paths[random.randint(0, len(self.__paths) - 1)][-1]] = True

    def _generate_random_connections(self):
        for _ in range(self.__random_connections_count):
            path_a = self.__paths[random.randint(0, len(self.__paths) - 1)]
            path_b = self.__paths[random.randint(0, len(self.__paths) - 1)]
            state_a = random.choice(path_a)
            state_b = random.choice(path_b)
            self.__graph[state_a].add(state_b)

    def _generate_transitions(self):
        for state_id in range(len(self.__graph)):
            next_states = list(self.__graph[state_id])
            if len(next_states) == 0:
                continue
            next_states_numbers = []
            state_number = self._add_state({'id': state_id, 'epistemic_class': self.state_epistemic_class[state_id]})
            n_action = 0
            for next_state in next_states:
                next_states_numbers.append(
                    self._add_state({'id': next_state, 'epistemic_class': self.state_epistemic_class[next_state]}))

            # for next_state_number in next_states_numbers:
            #     self.model.add_transition(state_number, next_state_number, [str(n_action)])
            #     n_action += 1

            for action in range(n_action, self.__max_action + 1):
                r_from = random.randint(0, len(next_states_numbers) - 1)
                count = random.randint(1, max(len(next_states_numbers), 2))
                for i in range(r_from, min(r_from + count, len(next_states_numbers))):
                    next_state_number = next_states_numbers[i]
                    self.model.add_transition(state_number, next_state_number, [str(action)])

    def _get_epistemic_state(self, state, agent_no):
        return {'epistemic_class': state['epistemic_class']}

    def _get_props_for_state(self, state: hash) -> List[str]:
        if self.winning_states[state['id']]:
            return ["win"]
        return []

    def get_actions(self) -> List[List[str]]:
        result = [[]]
        for i in range(self.__max_action + 1):
            result[0].append(str(i))
        return result

    def get_props_list(self) -> List[str]:
        return ["win"]

# while True:
#     random_model = RandomModel()
#     random_model.generate()
#     winning_states = random_model.get_winning_states("win")
#     strategy_comparer = StrategyComparer(random_model.model, random_model.get_actions()[0])
#     strategy = strategy_comparer.generate_winning_strategy_perfect_information(0, list(winning_states))
#     defined_in = 0
#     if strategy[0] is None:
#         print("Not winning")
#         continue
#
#     print("Strategy result:", strategy[0] is not None)
#     print(strategy)
#     for index, value in enumerate(strategy):
#         if value is not None:
#             print(f"{index}: {value}")
#             defined_in += 1
#     epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0, strategy)
#     print("Non control states in strategy:", strategy_comparer.count_non_control_states(0, strategy))
#     if strategy_comparer.count_non_control_states(0, strategy) == 0:
#         continue
#     print("Epistemic mismatch for random strategy: ", epistemic_mismatch)
#     print("Random strategy defined in", defined_in, "states")
#     simplified_strategy = strategy_comparer.simplify_strategy_one_agent(0, strategy, None)
#     print(simplified_strategy)
#     print("Different: ", simplified_strategy != strategy)
#     defined_in = 0
#     for index, value in enumerate(simplified_strategy):
#         if value is not None:
#             print(f"{index}: {value}")
#             defined_in += 1
#
#     epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0, simplified_strategy)
#     print("Non control states in strategy:", strategy_comparer.count_non_control_states(0, simplified_strategy))
#     print("Epistemic mismatch for simplified strategy: ", epistemic_mismatch)
#     print("Simpified strategy defined in", defined_in, "states")
#     break
