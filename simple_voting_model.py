from atl_model import *
import time
import pickle
import gc
# import resource
import random

__author__ = 'blackbat'

class SimpleVotingModel:
    number_of_candidates = 0
    number_of_voters = 0
    model = None
    states = []
    states_dictionary = {}
    epistemic_states_dictionary = {}
    voter_epistemic_states_dictionary = {}

    def __init__(self, number_of_candidates, number_of_voters):
        self.number_of_candidates = number_of_candidates
        self.number_of_voters = number_of_voters

    def generate_asynchronous_voting(self):
        self.model = ATLModel(self.number_of_voters + 1, 1000000)
        self.add_actions()

        beginning_array = []
        for _ in range(0, self.number_of_voters):
            beginning_array.append(-1)

        first_state = {'voted': beginning_array[:], 'voters_action': beginning_array[:], 'coercer_actions': beginning_array[:], 'finish': beginning_array[:]}
        state_number = 0

        self.states.append(first_state)
        state_string = ' '.join(str(first_state[e]) for e in first_state)
        self.states_dictionary[state_string] = state_number
        state_number += 1
        current_state_number = -1

        for state in self.states:
            current_state_number += 1
            voting_product_array = []
            coercer_possible_actions = ['wait']
            for voter_number in range(0, self.number_of_voters):
                if state['voted'][voter_number] == -1:
                    voting_product_array.append(list(range(0, self.number_of_candidates)))
                    voting_product_array[voter_number].append('wait')
                elif state['voters_action'][voter_number] == -1:
                    voting_product_array.append(['give', 'ng', 'wait'])
                elif state['coercer_actions'][voter_number] == -1:
                    coercer_possible_actions.append('np' + str(voter_number+1))
                    coercer_possible_actions.append('pun' + str(voter_number+1))
                    voting_product_array.append(['wait'])
                else:
                    voting_product_array.append(['wait'])

            voting_product_array.append(coercer_possible_actions)

            for possibility in itertools.product(*voting_product_array):
                action = {}
                new_state = {}
                new_state['voted'] = state['voted'][:]
                new_state['voters_action'] = state['voters_action'][:]
                new_state['coercer_actions'] = state['coercer_actions'][:]
                new_state['finish'] = state['finish'][:]
                for voter_number in range(0, self.number_of_voters):
                    action[voter_number+1] = possibility[voter_number]
                    voter_action_string = str(possibility[voter_number])
                    if voter_action_string[0] == 'g' or voter_action_string[0] == 'n':
                        new_state['voters_action'][voter_number] = voter_action_string
                    elif voter_action_string[0] != 'w':
                        new_state['voted'][voter_number] = possibility[voter_number]

                action[0] = possibility[self.number_of_voters]
                if action[0][0:3] == 'pun':
                    pun_voter_number = int(action[0][3:])
                    new_state['coercer_actions'][pun_voter_number-1] = 'pun'
                    new_state['finish'][pun_voter_number - 1] = 1
                elif action[0][0:2] == 'np':
                    np_voter_number = int(action[0][2:])
                    new_state['coercer_actions'][np_voter_number-1] = 'np'
                    new_state['finish'][np_voter_number - 1] = 1

                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                if new_state_str not in self.states_dictionary:
                    self.states_dictionary[new_state_str] = state_number
                    new_state_number = state_number
                    self.states.append(new_state)
                    state_number += 1
                else:
                    new_state_number = self.states_dictionary[new_state_str]

                self.model.add_transition(current_state_number, new_state_number, action)

            self.add_epistemic_state(state, current_state_number)
            self.add_voter_epistemic_state(state, current_state_number)

        self.prepare_epistemic_class()
        self.model.states = self.states

    def generate_simultaneously_voting(self):
        self.model = ATLModel(self.number_of_voters + 1, 1000)
        self.add_actions()

        beginning_array = []
        for _ in range(0, self.number_of_voters):
            beginning_array.append(-1)

        first_state = {'voted': beginning_array[:], 'voters_action': beginning_array[:], 'coercer_actions': beginning_array[:], 'finish': False}
        state_number = 0

        self.states.append(first_state)
        state_string = ' '.join(str(first_state[e]) for e in first_state)
        self.states_dictionary[state_string] = state_number
        state_number += 1
        current_state_number = -1

        voting_product_array = []
        decision_product_array = []
        for _ in range(0, self.number_of_voters):
            voting_product_array.append(range(0, self.number_of_candidates))
            decision_product_array.append(['give', 'ng'])

        for state in self.states:
            current_state_number += 1
            is_finish_state = False
            if state['voted'][0] == -1:
                for voting_product in itertools.product(*voting_product_array):
                    new_state = {}
                    new_state['voted'] = state['voted'][:]
                    new_state['voters_action'] = state['voters_action'][:]
                    new_state['coercer_actions'] = state['coercer_actions'][:]

                    action = {0: 'wait'}
                    for voter_number in range(0, self.number_of_voters):
                        new_state['voted'][voter_number] = voting_product[voter_number]
                        action[voter_number+1] = voting_product[voter_number]

                    new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                    if new_state_str not in self.states_dictionary:
                        self.states_dictionary[new_state_str] = state_number
                        new_state_number = state_number
                        self.states.append(new_state)
                        state_number += 1
                    else:
                        new_state_number = self.states_dictionary[new_state_str]

                    self.model.add_transition(current_state_number, new_state_number, action)
            elif state['voters_action'][0] == -1:
                for decision_product in itertools.product(*decision_product_array):
                    new_state = {}
                    new_state['voted'] = state['voted'][:]
                    new_state['voters_action'] = state['voters_action'][:]
                    new_state['coercer_actions'] = state['coercer_actions'][:]

                    action = {0: 'wait'}

                    for voter_number in range(0, self.number_of_voters):
                        new_state['voters_action'][voter_number] = decision_product[voter_number]
                        action[voter_number+1] = decision_product[voter_number]

                    new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                    if new_state_str not in self.states_dictionary:
                        self.states_dictionary[new_state_str] = state_number
                        new_state_number = state_number
                        self.states.append(new_state)
                        state_number += 1
                    else:
                        new_state_number = self.states_dictionary[new_state_str]

                    self.model.add_transition(current_state_number, new_state_number, action)
            else:
                action = {}
                for voter_number in range(1, self.number_of_voters + 1):
                    action[voter_number] = 'wait'

                is_finish_state = True
                for voter_number in range(1, self.number_of_voters + 1):
                    if state['coercer_actions'][voter_number - 1] == -1:
                        is_finish_state = False

                        new_state = {}
                        new_state['voted'] = state['voted'][:]
                        new_state['voters_action'] = state['voters_action'][:]
                        new_state['coercer_actions'] = state['coercer_actions'][:]
                        new_state['coercer_actions'][voter_number - 1] = 'pun'
                        action[0] = 'pun' + str(voter_number)

                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        if new_state_str not in self.states_dictionary:
                            self.states_dictionary[new_state_str] = state_number
                            new_state_number = state_number
                            self.states.append(new_state)
                            state_number += 1
                        else:
                            new_state_number = self.states_dictionary[new_state_str]

                        self.model.add_transition(current_state_number, new_state_number, action)

                        new_state2 = {}
                        new_state2['voted'] = state['voted'][:]
                        new_state2['voters_action'] = state['voters_action'][:]
                        new_state2['coercer_actions'] = state['coercer_actions'][:]
                        new_state2['coercer_actions'][voter_number - 1] = 'np'
                        action[0] = 'np' + str(voter_number)

                        new_state_str = ' '.join(str(new_state2[e]) for e in new_state2)
                        if new_state_str not in self.states_dictionary:
                            self.states_dictionary[new_state_str] = state_number
                            new_state_number = state_number
                            self.states.append(new_state2)
                            state_number += 1
                        else:
                            new_state_number = self.states_dictionary[new_state_str]

                        self.model.add_transition(current_state_number, new_state_number, action)

            state['finish'] = is_finish_state
            self.add_epistemic_state(state, current_state_number)

        self.prepare_epistemic_class()
        self.model.states = self.states

    def add_actions(self):
        self.model.add_action(0, 'wait')

        for voter_number in range(1, self.number_of_voters + 1):
            self.model.add_action(0, 'np' + str(voter_number))
            self.model.add_action(0, 'pun' + str(voter_number))
            self.model.add_action(voter_number, 'give')
            self.model.add_action(voter_number, 'ng')
            self.model.add_action(voter_number, 'wait')

            for candidate_number in range(0, self.number_of_candidates):
                self.model.add_action(voter_number, candidate_number)

    def add_epistemic_state(self, new_state, new_state_number):
        epistemic_state = {}
        epistemic_state['coercer_actions'] = new_state['coercer_actions'][:]
        epistemic_state['voted'] = new_state['voted'][:]
        epistemic_state['voters_action'] = new_state['voters_action'][:]
        epistemic_state['finish'] = new_state['finish'][:]
        for voter_number in range(0, self.number_of_voters):
            if new_state['voters_action'][voter_number] == -1 and new_state['voted'][voter_number] != -1:
                epistemic_state['voted'][voter_number] = -2
            elif new_state['voters_action'][voter_number] == 'ng':
                epistemic_state['voted'][voter_number] = -1

        epistemic_state_str = ' '.join(str(epistemic_state[e]) for e in epistemic_state)

        if epistemic_state_str not in self.epistemic_states_dictionary:
            self.epistemic_states_dictionary[epistemic_state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionary[epistemic_state_str].add(new_state_number)

    def add_voter_epistemic_state(self, new_state, new_state_number):
        epistemic_state = {}
        epistemic_state['coercer_actions'] = new_state['coercer_actions'][:]
        epistemic_state['voted'] = new_state['voted'][:]
        epistemic_state['voters_action'] = new_state['voters_action'][:]
        epistemic_state['finish'] = new_state['finish'][:]
        for voter_number in range(1, self.number_of_voters):
            epistemic_state['voters_action'][voter_number] = -1
            epistemic_state['voted'][voter_number] = -1
            epistemic_state['coercer_actions'][voter_number] = -1
            # epistemic_state['finish'][voter_number] = -1

        epistemic_state_str = ' '.join(str(epistemic_state[e]) for e in epistemic_state)

        if epistemic_state_str not in self.voter_epistemic_states_dictionary:
            self.voter_epistemic_states_dictionary[epistemic_state_str] = {new_state_number}
        else:
            self.voter_epistemic_states_dictionary[epistemic_state_str].add(new_state_number)

    def prepare_epistemic_class(self):
        for _, epistemic_class in self.epistemic_states_dictionary.items():
            self.model.add_epistemic_class(0, epistemic_class)

        for _, epistemic_class in self.voter_epistemic_states_dictionary.items():
            self.model.add_epistemic_class(1, epistemic_class)

        # for state_number in range(0, len(self.states)):
        #     for voter_number in range(1, self.number_of_voters + 1):
        #         self.model.add_epistemic_class(voter_number, {state_number})

    def print_states(self):
        for state in self.states:
            print(state)

    def print_number_of_epistemic_classes(self):
        print('Number of epistemic classes:', len(self.epistemic_states_dictionary))

    def print_number_of_states(self):
        print('Number of states:', len(self.states))


simple_voting_model = SimpleVotingModel(2, 3)

print('Started generating model')
start = time.clock()
simple_voting_model.generate_asynchronous_voting()
end = time.clock()
print('Generated model in', end-start, 's')

simple_voting_model.print_number_of_states()
simple_voting_model.print_number_of_epistemic_classes()
# simple_voting_model.print_states()
# simple_voting_model.model.walk(0)

voter_number = 0
print()
print("<<c>>F(~pun_i -> vote_{i,1})")
winning_states = []
i = -1
for state in simple_voting_model.states:
    i += 1
    is_winning = True

    if not (state['coercer_actions'][voter_number] != 'pun' and state['voted'][voter_number] != 1):
        winning_states.append(i)

start = time.clock()
result = simple_voting_model.model.minimum_formula_one_agent_multiple_states(0, winning_states)
end = time.clock()

print("Time:", end - start, "s")
print("Number of good states ", len(result))
print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])

print()
print("<<v_i>>G(~pun_i & ~vote_{i,1})")
winning_states = []
i = -1
for state in simple_voting_model.states:
    i += 1

    if state['coercer_actions'][voter_number] != 'pun' and state['voted'][voter_number] != 1:
        winning_states.append(i)

start = time.clock()
result = simple_voting_model.model.maximum_formula_one_agent_multiple_states(1, winning_states)
end = time.clock()

print("Time:", end - start, "s")
print("Number of good states ", len(result))
print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])


print()
print("<<c>>G( (finish_i & ~pun_i) -> vote_{i,1} )")
winning_states = []
i = -1
for state in simple_voting_model.states:
    i += 1

    if not (state['finish'][voter_number]==1 and state['coercer_actions'][voter_number] != 'pun' and state['voted'][voter_number] != 1):
        winning_states.append(i)

start = time.clock()
result = simple_voting_model.model.maximum_formula_one_agent_multiple_states(0, winning_states)
end = time.clock()

print("Time:", end - start, "s")
print("Number of good states ", len(result))
print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])


print()
print("<<v_i>>F( finish_i & ~pun_i & ~vote_{i,1} )")
winning_states = []
i = -1
for state in simple_voting_model.states:
    i += 1
    if state['finish'][voter_number]==1 and state['coercer_actions'][voter_number] != 'pun' and state['voted'][voter_number] != 1:
        winning_states.append(i)

start = time.clock()
result = simple_voting_model.model.maximum_formula_one_agent_multiple_states(1, winning_states)
end = time.clock()

print("Time:", end - start, "s")
print("Number of good states ", len(result))
print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])
