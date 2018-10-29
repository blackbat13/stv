from simple_models.simple_model import SimpleModel
from typing import List
import itertools


class CastleModel:
    model = None
    castle_sizes: List[int] = []
    castle_lifes: List[int] = []
    states: List[hash] = []
    states_dictionary = {}
    state_number: int = 0
    epistemic_states_dictionaries: List[hash] = []
    no_agents = 0

    def __init__(self, castle_sizes: List[int], castle_lifes: List[int]):
        assert len(castle_sizes) == len(castle_lifes)
        self.castle_sizes = castle_sizes
        self.castle_lifes = castle_lifes
        self.model = SimpleModel(sum(castle_sizes))
        self.no_agents = sum(self.castle_sizes)

        self.prepare_epistemic_dictionaries()
        self.generate_model()
        self.prepare_epistemic_relation()
        self.model.states = self.states

    def prepare_epistemic_dictionaries(self):
        self.epistemic_states_dictionaries.clear()
        for _ in range(0, self.no_agents):
            self.epistemic_states_dictionaries.append({})

    def generate_first_state(self) -> hash:
        defend = []
        for castle_id in range(0, len(self.castle_sizes)):
            defend.append([])
            for i in range(0, self.castle_sizes[castle_id]):
                defend[castle_id].append(False)
        first_state = {'lifes': self.castle_lifes[:], 'defend': defend}
        return first_state

    def add_state(self, state: hash) -> int:
        new_state_number = self.get_state_number(state)
        for i in range(0, self.no_agents):
            epistemic_state = self.get_epistemic_state(state, i)
            self.add_to_epistemic_dictionary(epistemic_state, new_state_number, i)
        return new_state_number

    def get_state_number(self, state: hash) -> int:
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.states_dictionary:
            self.states_dictionary[state_str] = self.state_number
            new_state_number = self.state_number
            self.states.append(state)
            self.state_number += 1
        else:
            new_state_number = self.states_dictionary[state_str]

        return new_state_number

    def get_epistemic_state(self, state: hash, agent_number: int) -> hash:
        castle_id = 0
        agent_no = 0
        size = 0
        for i in range(0, len(self.castle_sizes)):
            prev_size = size
            size += self.castle_sizes[i]
            if agent_number < size:
                castle_id = i
                agent_no = agent_number - prev_size
                break

        life = state['lifes'][castle_id]
        # defend = state['defend'][castle_id][agent_no]
        defend = state['defend'][castle_id]
        epistemic_state = {'life': life, 'defend': defend}

        return epistemic_state

    def add_to_epistemic_dictionary(self, state: hash, new_state_number: int, agent_number: int):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.epistemic_states_dictionaries[agent_number]:
            self.epistemic_states_dictionaries[agent_number][state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionaries[agent_number][state_str].add(new_state_number)

    def generate_model(self):
        first_state = self.generate_first_state()
        self.add_state(first_state)
        current_state_number = -1
        possible_actions = self.generate_actions()

        for state in self.states:
            current_state_number += 1
            if sum(state['lifes']) == 0:
                continue

            for action in itertools.product(*possible_actions):
                defend = []
                for i in range(0, len(self.castle_sizes)):
                    defend.append(state['defend'][i][:])
                new_state = {'lifes': state['lifes'][:],
                             'defend': defend}
                lifes_result = []
                for i in range(0, len(self.castle_sizes)):
                    lifes_result.append(0)
                skip = False

                agent_no = -1
                for castle_id in range(0, len(self.castle_sizes)):
                    for i in range(0, self.castle_sizes[castle_id]):
                        agent_no += 1
                        if action[agent_no] == 'idle':
                            new_state['defend'][castle_id][i] = False
                        elif state['lifes'][castle_id] == 0:
                            skip = True
                            break
                        elif action[agent_no] == 'defend':
                            if state['defend'][castle_id][i]:
                                skip = True
                                break
                            else:
                                new_state['defend'][castle_id][i] = True
                                lifes_result[castle_id] += 1
                        else:
                            castle_no = int(action[agent_no].split()[1])
                            new_state['defend'][castle_id][i] = False
                            lifes_result[castle_no] -= 1

                    if skip:
                        break

                if skip:
                    continue

                for i in range(0, len(self.castle_sizes)):
                    if lifes_result[i] < 0:
                        new_state['lifes'][i] += lifes_result[i]
                        if new_state['lifes'][i] < 0:
                            new_state['lifes'][i] = 0

                new_state_number = self.add_state(new_state)

                actions = []
                for i in range(0, self.no_agents - self.castle_sizes[-1]):
                    actions.append(action[i])

                self.model.add_transition(current_state_number, new_state_number, actions)

    def generate_actions(self):
        actions = []
        for i in range(0, len(self.castle_sizes)):
            actions.append(['idle', 'defend'])
            for j in range(0, len(self.castle_sizes)):
                if i == j:
                    continue
                actions[-1].append('attack ' + str(j))

        possible_actions = []

        for i in range(0, len(self.castle_sizes)):
            for j in range(0, self.castle_sizes[i]):
                possible_actions.append(actions[i])

        return possible_actions

    def prepare_epistemic_relation(self):
        for i in range(0, self.no_agents):
            for state, epistemic_class in self.epistemic_states_dictionaries[i].items():
                self.model.add_epistemic_class(i, epistemic_class)
