import time
from atl_model import *

__author__ = 'blackbat'


class CastleModel:
    model = None
    states = []
    states_dictionary = {}
    sizes = []
    lifes = []
    class_a_epistemic = {}
    class_b_epistemic = {}
    class_c_epistemic = {}

    def __init__(self, a_size, b_size, c_size, a_life, b_life, c_life):
        self.model = ATLModel(a_size + b_size + c_size, (4 ** 3) * (2 ** a_size) * (2 ** b_size) * (2 ** c_size))
        self.sizes = [a_size, b_size, c_size]
        self.lifes = [a_life, b_life, c_life]

        defend_a = []
        for _ in range(0, a_size):
            defend_a.append(False)
        defend_b = []
        for _ in range(0, b_size):
            defend_b.append(False)
        defend_c = []
        for _ in range(0, c_size):
            defend_c.append(False)

        first_state = {'lifes': [a_life, b_life, c_life], 'defend': [defend_a[:], defend_b[:], defend_c[:]]}
        self.states_dictionary[''.join(str(first_state[e]) for e in first_state)] = 0
        self.states.append(first_state)
        possible_actions = self.generate_actions()
        state_number = -1
        number_of_states = 1
        self.prepare_epistemic_class(first_state, 0)

        for state in self.states:
            state_number += 1
            if state['lifes'][0] == 0 and state['lifes'][1] == 0 and state['lifes'][2] == 0:
                break

            for action in itertools.product(*possible_actions):
                new_state = {'lifes': state['lifes'][:],
                             'defend': [state['defend'][0][:], state['defend'][1][:], state['defend'][2][:]]}
                lifes_result = [0, 0, 0]
                skip = False
                for i in range(0, self.sizes[0]):
                    if action[i] == 'idle':
                        new_state['defend'][0][i] = False
                    elif action[i] == 'defend' and state['defend'][0][i] == True:
                        skip = True
                        break
                    elif action[i] == 'defend':
                        new_state['defend'][0][i] = True
                        lifes_result[0] += 1
                    elif action[i] == 'attack B':
                        new_state['defend'][0][i] = False
                        lifes_result[1] -= 1
                    elif action[i] == 'attack C':
                        new_state['defend'][0][i] = False
                        lifes_result[2] -= 1

                if skip:
                    continue

                for i in range(0, self.sizes[1]):
                    if action[i + self.sizes[0]] == 'idle':
                        new_state['defend'][1][i] = False
                    elif action[i + self.sizes[0]] == 'defend' and state['defend'][1][i] == True:
                        skip = True
                        break
                    elif action[i + self.sizes[0]] == 'defend':
                        new_state['defend'][1][i] = True
                        lifes_result[1] += 1
                    elif action[i + self.sizes[0]] == 'attack A':
                        new_state['defend'][1][i] = False
                        lifes_result[0] -= 1
                    elif action[i + self.sizes[0]] == 'attack C':
                        new_state['defend'][1][i] = False
                        lifes_result[2] -= 1

                if skip:
                    continue

                for i in range(0, self.sizes[2]):
                    if action[i + self.sizes[0] + self.sizes[1]] == 'idle':
                        new_state['defend'][2][i] = False
                    elif action[i + self.sizes[0] + self.sizes[1]] == 'defend' and state['defend'][2][i] == True:
                        skip = True
                        break
                    elif action[i + self.sizes[0] + self.sizes[1]] == 'defend':
                        new_state['defend'][2][i] = True
                        lifes_result[2] += 1
                    elif action[i + self.sizes[0] + self.sizes[1]] == 'attack A':
                        new_state['defend'][2][i] = False
                        lifes_result[0] -= 1
                    elif action[i + self.sizes[0] + self.sizes[1]] == 'attack B':
                        new_state['defend'][2][i] = False
                        lifes_result[1] -= 1

                if skip:
                    continue

                for i in range(0, 3):
                    if lifes_result[i] < 0:
                        new_state['lifes'][i] += lifes_result[i]
                        if new_state['lifes'][i] < 0:
                            new_state['lifes'][i] = 0

                new_state_string = ''.join(str(new_state[e]) for e in new_state)
                new_state_number = -1
                if new_state_string in self.states_dictionary:

                    new_state_number = self.states_dictionary[new_state_string]
                else:
                    self.states_dictionary[new_state_string] = number_of_states
                    new_state_number = number_of_states
                    number_of_states += 1

                    self.states.append(new_state)
                    self.prepare_epistemic_class(new_state, new_state_number)

                model_actions = {}
                for i in range(0, len(action)):
                    model_actions[i] = action[i]

                self.model.add_transition(state_number, new_state_number, model_actions)

        self.model.states = self.states
        self.add_epistemic_to_model()

    def prepare_epistemic_class(self, state, state_number):
        state_a_epistemic = {'lifes': [state['lifes'][0]], 'defend': [state['defend'][0][:]]}
        state_b_epistemic = {'lifes': [state['lifes'][1]], 'defend': [state['defend'][1][:]]}
        state_c_epistemic = {'lifes': [state['lifes'][2]], 'defend': [state['defend'][2][:]]}
        state_a_epistemic_str = ''.join(str(state_a_epistemic[e]) for e in state_a_epistemic)
        state_b_epistemic_str = ''.join(str(state_b_epistemic[e]) for e in state_b_epistemic)
        state_c_epistemic_str = ''.join(str(state_c_epistemic[e]) for e in state_c_epistemic)
        if state_a_epistemic_str in self.class_a_epistemic:
            self.class_a_epistemic[state_a_epistemic_str].append(state_number)
        else:
            self.class_a_epistemic[state_a_epistemic_str] = [state_number]

        if state_b_epistemic_str in self.class_b_epistemic:
            self.class_b_epistemic[state_b_epistemic_str].append(state_number)
        else:
            self.class_b_epistemic[state_b_epistemic_str] = [state_number]

        if state_c_epistemic_str in self.class_c_epistemic:
            self.class_c_epistemic[state_c_epistemic_str].append(state_number)
        else:
            self.class_c_epistemic[state_c_epistemic_str] = [state_number]

    def add_epistemic_to_model(self):
        for _, epistemic_class in self.class_a_epistemic.items():
            for agent in range(0, self.sizes[0]):
                self.model.add_epistemic_class(agent, epistemic_class)

        for _, epistemic_class in self.class_b_epistemic.items():
            for agent in range(0, self.sizes[1]):
                self.model.add_epistemic_class(agent + self.sizes[0], epistemic_class)

        for _, epistemic_class in self.class_c_epistemic.items():
            for agent in range(0, self.sizes[2]):
                self.model.add_epistemic_class(agent + self.sizes[0] + self.sizes[1], epistemic_class)

    def life_sign(life):
        if life == 0:
            return 0
        else:
            return 1

    def generate_actions(self):
        a_actions = ['idle', 'defend', 'attack B', 'attack C']
        b_actions = ['idle', 'defend', 'attack A', 'attack C']
        c_actions = ['idle', 'defend', 'attack A', 'attack B']
        possible_actions = []

        for i in range(0, self.sizes[0]):
            possible_actions.append(a_actions)
            for action in a_actions:
                self.model.add_action(i, action)
        for i in range(0, self.sizes[1]):
            possible_actions.append(b_actions)
            for action in b_actions:
                self.model.add_action(i + self.sizes[0], action)
        for i in range(0, self.sizes[2]):
            possible_actions.append(c_actions)
            for action in c_actions:
                self.model.add_action(i + self.sizes[0] + self.sizes[1], action)

        return possible_actions


def find_state_index(states, search_state):
    index = 0
    for state in states:
        is_same = True
        # print(state, search_state)
        for i in range(0, len(search_state)):
            if search_state[i] != state[i]:
                is_same = False
                break

        if is_same:
            return index
        index += 1


a_size = 1
b_size = 1
c_size = 1
start = time.clock()
castle_model = CastleModel(a_size, b_size, c_size, 3, 3, 3)
end = time.clock()
print('Generated castle model in', end - start, 's')
print('Number of states in model:', len(castle_model.states))

castle_3_defeated_states = []
all_castles_defeated_states = []
for i in range(0, len(castle_model.states)):
    state = castle_model.states[i]
    if state['lifes'][2] == 0:
        castle_3_defeated_states.append(i)
    if state['lifes'][0] == 0 and state['lifes'][1] == 0 and state['lifes'][2] == 0:
        all_castles_defeated_states.append(i)
    # print(state)

# castle_model.model.walk(0)

print('Number of winning states', len(castle_3_defeated_states))
print("Castle 3 defeated:")
start = time.clock()
castle_3_defeated_result = castle_model.model.minimum_formula_multiple_agents_and_states([0, 1], castle_3_defeated_states)
end = time.clock()
print('Computed in', end - start, 's')
print('Number of states:', len(castle_3_defeated_result))
formula_result = False
for state in castle_3_defeated_result:
    # print(state, castle_model.states[state])
    if state == 0:
        formula_result = True

print('Formula result:', formula_result)
print()

print("Castle 3 defeated perfect information:")
start = time.clock()
castle_3_defeated_result = castle_model.model.minimum_formula_multiple_agents_and_states_perfect_information([0, 1], castle_3_defeated_states)
end = time.clock()
print('Computed in', end - start, 's')
print('Number of states:', len(castle_3_defeated_result))
formula_result = False
for state in castle_3_defeated_result:
    # print(state, castle_model.states[state])
    if state == 0:
        formula_result = True

print('Formula result:', formula_result)
print()

formula_result = False
print('Number of winning states', len(all_castles_defeated_states))
print("All castles defeated:")
start = time.clock()
all_castles_defeated_result = castle_model.model.minimum_formula_multiple_agents_and_states([0, 1, 2], all_castles_defeated_states)
end = time.clock()
print('Computed in', end - start, 's')
print('Number of states:', len(all_castles_defeated_result))
for state in all_castles_defeated_result:
    # print(state, castle_model.states[state])
    if state == 0:
        formula_result = True

print('Formula result:', formula_result)
print()

formula_result = False
print("All castles defeated perfect information:")
start = time.clock()
all_castles_defeated_result = castle_model.model.minimum_formula_multiple_agents_and_states_perfect_information([0, 1, 2], all_castles_defeated_states)
end = time.clock()
print('Computed in', end - start, 's')
print('Number of states:', len(all_castles_defeated_result))
for state in all_castles_defeated_result:
    # print(state, castle_model.states[state])
    if state == 0:
        formula_result = True

print('Formula result:', formula_result)

