from typing import List
from models.model_generator import ModelGenerator
from enum import Enum
import itertools
import random


class RandomModel(ModelGenerator):
    def __init__(self):
        super().__init__(no_agents=2)
        self.max_states = 1000

    def _generate_initial_states(self):
        self._add_state({'id': 0})

    def _generate_model(self):
        num_of_paths = 100
        num_of_connections = 100
        length_of_path = 20

        paths = []
        graph = [[] for _ in range(self.max_states + 1)]
        for _ in range(num_of_paths):
            path = [0]
            for _ in range(length_of_path):
                if (path[-1] + 1) >= self.max_states:
                    break
                next_state = random.randint(path[-1] + 1, self.max_states)
                graph[path[-1]].append(next_state)
                path.append(next_state)

            paths.append(path)
        for _ in range(num_of_connections):
            path_id_1 = random.randint(0, len(paths) - 1)
            path_id_2 = random.randint(0, len(paths) - 1)
            state_id_1 = random.choice(paths[path_id_1])
            state_id_2 = random.choice(paths[path_id_2])
            graph[state_id_1].append(state_id_2)

        for state_id in range(len(graph)):
            next_states = graph[state_id]
            if len(next_states) == 0:
                continue
            action = 1
            state_number = self._add_state({'id': state_id})
            rand_k = random.randint(2, max(len(next_states) // 2, 2))
            for k in range(1, rand_k):
                new_next_states = random.choices(next_states, k=k)
                action2 = 1
                for n_st in new_next_states:
                    next_state_number = self._add_state({'id': n_st})
                    self.model.add_transition(state_number, next_state_number, [str(action), str(action2)])
                    action2 += 1
                action += 1

    def _get_epistemic_state(self, state, agent_no):
        return state

    def _get_props_for_state(self, state: hash) -> List[str]:
        pass

    def get_actions(self):
        pass

    def get_props_list(self) -> List[str]:
        pass

    def get_winning_states(self, prop: str) -> List[int]:
        pass


random_model = RandomModel()
random_model.generate()
random_model.model.simulate(0)
