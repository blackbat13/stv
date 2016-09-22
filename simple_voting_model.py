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

    def __init__(self, number_of_candidates, number_of_voters):
        self.number_of_candidates = number_of_candidates
        self.number_of_voters = number_of_voters

    def generate(self):
        self.model = ATLModel(self.number_of_voters, 1000)
        self.add_actions()

        first_state = {'voted': [-1], 'voters_action': [-1], 'coercer_actions': [-1]}
        state_number = 0

        self.states.append(first_state)
        state_string = ' '.join(str(first_state[e]) for e in first_state)
        self.states_dictionary[state_string] = state_number
        state_number += 1
        current_state_number = -1

        for state in self.states:
            current_state_number += 1
            if state['voted'][0] == -1:
                for candidate_number in range(0,self.number_of_candidates):
                    new_state = {}
                    new_state['voted'] = state['voted'][:]
                    new_state['voters_action'] = state['voters_action'][:]
                    new_state['coercer_actions'] = state['coercer_actions'][:]

                    new_state['voted'][0] = candidate_number

                    action = {0: 'wait', 1: candidate_number}
                    new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                    if new_state_str not in self.states_dictionary:
                        self.states_dictionary[new_state_str] = state_number
                        new_state_number = state_number
                        self.states.append(new_state)
                        state_number += 1
                    else:
                        new_state_number = self.states_dictionary[new_state_str]

                    self.add_epistemic_state(new_state, new_state_number)

                    self.model.add_transition(current_state_number, new_state_number, action)
            elif state['voters_action'][0] == -1:
                for voter_action in ['give', 'ng']:
                    new_state = {}
                    new_state['voted'] = state['voted'][:]
                    new_state['voters_action'] = state['voters_action'][:]
                    new_state['coercer_actions'] = state['coercer_actions'][:]

                    new_state['voters_action'][0] = voter_action

                    action = {0: 'wait', 1: voter_action}
                    new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                    if new_state_str not in self.states_dictionary:
                        self.states_dictionary[new_state_str] = state_number
                        new_state_number = state_number
                        self.states.append(new_state)
                        state_number += 1
                    else:
                        new_state_number = self.states_dictionary[new_state_str]

                    self.add_epistemic_state(new_state, new_state_number)

                    self.model.add_transition(current_state_number, new_state_number, action)
            else:
                action = {0: 'np', 1: 'wait'}
                self.model.add_transition(current_state_number, current_state_number, action)

                new_state = {}
                new_state['voted'] = state['voted'][:]
                new_state['voters_action'] = state['voters_action'][:]
                new_state['coercer_actions'] = state['coercer_actions'][:]

                new_state['coercer_actions'][0] = 'pun'

                action = {0: 'pun', 1: 'wait'}
                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                if new_state_str not in self.states_dictionary:
                    self.states_dictionary[new_state_str] = state_number
                    new_state_number = state_number
                    self.states.append(new_state)
                    state_number += 1
                else:
                    new_state_number = self.states_dictionary[new_state_str]

                self.add_epistemic_state(new_state, new_state_number)

                self.model.add_transition(current_state_number, new_state_number, action)

        self.prepare_epistemic_class()

    def add_actions(self):
        self.model.add_action(0, 'wait')
        self.model.add_action(0, 'np')
        self.model.add_action(0, 'pun')

        for voter_number in range(1, self.number_of_voters + 1):
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
        for voter_number in range(0, self.number_of_voters):
            if new_state['voters_action'][voter_number] == -1 or new_state['voters_action'][voter_number] == 'ng':
                epistemic_state['voted'][voter_number] = -1

        epistemic_state_str = ' '.join(str(epistemic_state[e]) for e in epistemic_state)

        if epistemic_state_str not in self.epistemic_states_dictionary:
            self.epistemic_states_dictionary[epistemic_state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionary[epistemic_state_str].add(new_state_number)

    def prepare_epistemic_class(self):
        for _, epistemic_class in self.epistemic_states_dictionary.items():
            self.model.add_epistemic_class(0, epistemic_class)
            print(epistemic_class)

    def print_states(self):
        for state in self.states:
            print(state)

    def print_number_of_epistemic_classes(self):
        print(len(self.epistemic_states_dictionary))


simple_voting_model = SimpleVotingModel(2, 1)
simple_voting_model.generate()
print(len(simple_voting_model.states))
simple_voting_model.print_number_of_epistemic_classes()
simple_voting_model.print_states()


