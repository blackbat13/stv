from simple_models.simple_model import SimpleModel
from enum import Enum
import itertools


class DiningCryptographers:
    model = None
    no_agents = 0
    states_dictionary = {}
    epistemic_states_dictionaries = []
    state_number = 0

    class Coin(Enum):
        NONE = 0
        HEAD = 1
        TAIL = 2

    class NumberOfOdd(Enum):
        NONE = 0
        ODD = 1
        EVEN = 2

    def __init__(self, no_agents):
        self.no_agents = no_agents
        self.create_atl_model()
        self.prepare_variables()
        self.generate_model()
        self.prepare_epistemic_relation()

    def create_atl_model(self):
        self.model = SimpleModel(self.no_agents)

    def prepare_variables(self):
        for _ in range(0, self.no_agents):
            self.epistemic_states_dictionaries.append({})

    def generate_model(self):
        self.create_beginning_states()
        current_state_number = -1
        for state in self.model.states:
            current_state_number += 1
            if state['number_of_odd'] != self.NumberOfOdd.NONE:
                continue

            actions = []
            number = 0
            for agent_no in range(0, self.no_agents):
                if state['coins'][agent_no] == state['coins'][agent_no - 1]:
                    actions.append('say_equal')
                    number += 1
                else:
                    actions.append('say_different')

            if number % 2 == 0:
                number_of_odd = self.NumberOfOdd.EVEN
            else:
                number_of_odd = self.NumberOfOdd.ODD

            new_state = {'number_of_odd': number_of_odd, 'coins': state['coins'], 'paying': state['paying']}
            new_state_number = self.add_state(new_state)
            self.model.add_transition(current_state_number, new_state_number, actions)

    def create_beginning_states(self):
        available_coins = []
        for _ in range(0, self.no_agents):
            available_coins.append([self.Coin.HEAD, self.Coin.TAIL])

        for coins in itertools.product(*available_coins):
            for paying in range(-1, self.no_agents):
                state = {'number_of_odd': self.NumberOfOdd.NONE, 'coins': list(coins), 'paying': paying}
                self.add_state(state)

    def add_state(self, state):
        new_state_number = self.get_state_number(state)
        for agent_no in range(0, self.no_agents):
            epistemic_state = self.get_epistemic_state(state, agent_no)
            self.add_to_epistemic_dictionary(epistemic_state, new_state_number, agent_no)
        return new_state_number

    def get_state_number(self, state):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.states_dictionary:
            self.states_dictionary[state_str] = self.state_number
            new_state_number = self.state_number
            self.model.states.append(state)
            self.state_number += 1
        else:
            new_state_number = self.states_dictionary[state_str]

        return new_state_number

    def add_to_epistemic_dictionary(self, state, new_state_number, agent_no):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.epistemic_states_dictionaries[agent_no]:
            self.epistemic_states_dictionaries[agent_no][state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionaries[agent_no][state_str].add(new_state_number)

    def get_epistemic_state(self, state, agent_no):
        epistemic_coins = state['coins'][:]
        for i in range(0, self.no_agents):
            if i == agent_no or i == agent_no - 1:
                continue

            epistemic_coins[i] = self.Coin.NONE
        epistemic_state = {'number_of_odd': state['number_of_odd'], 'coins': epistemic_coins, 'paying': -2}
        return epistemic_state

    def prepare_epistemic_relation(self):
        for agent_no in range(0, self.no_agents):
            for state, epistemic_class in self.epistemic_states_dictionaries[agent_no].items():
                self.model.add_epistemic_class(agent_no, epistemic_class)
