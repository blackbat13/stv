from stv.models.model_generator import ModelGenerator
from typing import List
import random
import math


class RandomModel(ModelGenerator):
    def __init__(self, max_states: int = 20):
        super().__init__(agents_count=2)
        self.__max_states = max_states
        # self.__max_epistemic_classes = random.randint(self.__max_states // 4, self.__max_states // 2)
        self.__max_epistemic_classes = int(self.__max_states // math.log2(self.__max_states))
        self.__max_winning_states = random.randint(1, self.__max_states // 5)
        self.__path_length = random.randint(self.__max_states // 4, 3 * self.__max_states // 4)
        self.__paths_count = random.randint(self.__max_states * 2, self.__max_states * 4)
        self.__max_action = 1
        self.__random_connections_count = random.randint(self.__max_states // 4, self.__max_states * 4)
        # self.state_epistemic_class = [random.randint(0, self.__max_epistemic_classes) for _ in
        #                               range(self.__max_states + 1)]

        self.state_epistemic_class = [i for i in range(self.__max_states + 1)]

        epistemic_classes_count = 0
        for epistemic_class_id in range(self.__max_states + 2, self.__max_states + 2 + self.__max_epistemic_classes):
            # epistemic_class_size = random.randint(int(math.log2(self.__max_states)/2), int(math.log2(self.__max_states)))
            epistemic_class_size = int(math.log2(self.__max_states))
            epistemic_classes_count += 1
            for i in range(0, epistemic_class_size):
                state_id = random.randint(1, self.__max_states)
                cnt = 0
                while cnt < self.__max_states and self.state_epistemic_class[state_id] > self.__max_states + 1:
                    state_id = random.randint(1, self.__max_states)
                    cnt += 1
                if cnt >= self.__max_states:
                    epistemic_classes_count -= 1
                    break
                self.state_epistemic_class[state_id] = epistemic_class_id
        self.state_epistemic_class[0] = 0
        print(f"Max epistemic classes: {self.__max_epistemic_classes}")
        print(epistemic_classes_count)
        print(self.state_epistemic_class)
        self.winning_states = [False for _ in range(self.__max_states + 1)]
        self.__paths: List[List[int]] = []
        self.__graph = [set() for _ in range(self.__max_states + 1)]

    def _generate_initial_states(self):
        self._add_state({'id': 0, 'epistemic_class': self.state_epistemic_class[0]})

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


if __name__ == "__main__":
    model = RandomModel(100)
    model.generate()