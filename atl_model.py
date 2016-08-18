__author__ = 'blackbat'

import itertools


def create_array_of_size(size, basic_item):
    array = []
    for i in range(0, size):
        array.append(basic_item.copy())
    return array[:]


def unique(l):
    s = set()
    n = 0
    for x in l:
        if x not in s:
            s.add(x)
            l[n] = x
            n += 1
    del l[n:]


def and_operator(a, b):
    c = []
    for item in a:
        if item in b:
            c.append(item)

    return c


def or_operator(a, b):
    c = []
    c += a
    for item in b:
        if item not in c:
            c.append(item)

    return c


def not_operator(a, number_of_states):
    c = []
    for i in range(0, number_of_states):
        if i not in a:
            c.append(i)

    return c


class ATLModel:
    number_of_agents = 0
    agent_names = {}
    number_of_states = 0
    transitions = []
    reverse_transitions = []
    reverse_states = []
    imperfect_information = []
    agents_actions = []
    state_names = []
    state_descriptions = []
    states = []

    def __init__(self, number_of_agents, number_of_states):
        self.number_of_agents = number_of_agents
        self.number_of_states = number_of_states
        self.transitions = [[] for _ in itertools.repeat(None, number_of_states)]
        self.reverse_transitions = [[] for _ in itertools.repeat(None, number_of_states)]
        self.imperfect_information = create_array_of_size(number_of_agents, [])
        self.reverse_states = [set() for _ in itertools.repeat(None, number_of_states)]
        self.agents_actions = [[] for _ in itertools.repeat(None, number_of_states)]
        # self.stateNames = create_array_of_size(number_of_states, [])
        # self.stateDescriptions = create_array_of_size(number_of_states, [])
        for i in range(0, 1):  # number_of_agents):
            self.imperfect_information[i] = [set() for i in itertools.repeat(None, number_of_states)]
            for j in range(0, number_of_states):
                self.imperfect_information[i][j].add(j)

    def add_action(self, agent, action):
        self.agents_actions[agent].append(action)

    def add_transition(self, from_state, to_state, actions):
        self.transitions[from_state].append({'nextState': to_state, 'actions': actions})
        self.reverse_transitions[to_state].append({'nextState': from_state, 'actions': actions})
        self.reverse_states[to_state].add(from_state)
        # for i in range(0, self.numberOfAgents):
        #     if actions[i] not in self.agentsActions[i]:
        #         self.agentsActions[i].append(actions[i])

    def is_same_state(self, agent_number, state_a, state_b):
        return state_b in self.imperfect_information[agent_number][state_a]

    def set_same_state(self, agent_number, state_a, state_b):
        self.imperfect_information[agent_number][state_a].add(state_b)
        self.imperfect_information[agent_number][state_b].add(state_a)

    def basic_formula(self, agent_number, winning_state):
        result_states = []
        for state in self.reverse_states[winning_state]:
            ok = True
            for same_state in self.imperfect_information[agent_number][state]:
                if not self.is_reachable_by_agent(same_state, winning_state, agent_number):
                    ok = False
                    break
            if ok:
                result_states.append(state)
        return result_states

    def basic_formula_multiple_agents(self, agents, winning_state):
        result_states = []
        actions = self.create_agents_actions_combinations(agents)
        for state in self.reverse_states[winning_state]:
            ok = True
            same_states = self.get_same_states_for_agents(agents, state)
            for same_state in same_states:
                if not self.is_reachable_by_agents(actions, same_state, [winning_state], agents):
                    ok = False
                    break
            if ok:
                result_states.append(state)
        return result_states

    def get_same_states_for_agents(self, agents, state):
        same_states = []
        for agent in agents:
            for same_state in self.imperfect_information[agent][state]:
                if same_state not in same_states:
                    same_states.append(same_state)
        return same_states

    def is_reachable_by_agents(self, actions, from_state, to_states, agents):
        for action in actions:
            action_ok = False
            for transition in self.transitions[from_state]:
                if self.is_possible_transition(agents, action, transition):
                    action_ok = True
                    if transition['nextState'] not in to_states:
                        action_ok = False
                        break
            if action_ok:
                return True
        return False

    def is_reachable_by_agent(self, actions, from_state, to_states, agent):
        for action in self.agents_actions[agent]:
            action_ok = False
            for transition in self.transitions[from_state]:
                if transition['actions'][0] == action:
                    action_ok = True
                    if transition['nextState'] not in to_states:
                        action_ok = False
                        break

            if action_ok:
                return True

        return False

    def basic_formula_multiple_agents_and_states(self, agents, winning_states):
        result_states = set()
        actions = self.create_agents_actions_combinations(agents)
        winning_states_reverse = []
        for winning_state in winning_states:
            winning_states_reverse += self.reverse_states[winning_state]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            ok = True
            same_states = self.get_same_states_for_agents(agents, state)
            winning_states_reverse_same = [state]

            for same_state in same_states:
                if ok and not self.is_reachable_by_agents(actions, same_state, winning_states, agents):
                    ok = False
                if same_state != state and same_state in winning_states_reverse:
                    winning_states_reverse.remove(same_state)
                    winning_states_reverse_same.append(same_state)
            if ok:
                result_states.update(winning_states_reverse_same)
        return result_states

    def basic_formula_one_agent_multiple_states(self, agent, current_states, winning_states):
        result_states = set()
        actions = self.agents_actions[agent]
        winning_states_reverse = []
        for winning_state in current_states:
            winning_states_reverse += self.reverse_states[winning_state]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            ok = True
            same_states = self.imperfect_information[agent][state]
            winning_states_reverse_same = [state]
            for same_state in same_states:
                if ok and not self.is_reachable_by_agent(actions, same_state, winning_states, agent):
                    ok = False

                if same_state != state and same_state in winning_states_reverse:
                    winning_states_reverse.remove(same_state)
                    winning_states_reverse_same.append(same_state)
            if ok:
                result_states.update(winning_states_reverse_same)

        return result_states

    def basic_formula_one_agent_multiple_states_perfect_information(self, agent, current_states, winning_states):
        result_states = set()
        actions = self.agents_actions[agent]
        winning_states_reverse = []
        for winning_state in current_states:
            winning_states_reverse += self.reverse_states[winning_state]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            if self.is_reachable_by_agent(actions, state, winning_states, agent):
                result_states.add(state)

        return result_states

    def minimum_formula_multiple_agents_and_states(self, agents, winning_states):
        resultStates = set()
        resultStates.update(winning_states)
        result_states_length = len(resultStates)
        number_of_iterations = 0
        while True:
            resultStates.update(self.basic_formula_multiple_agents_and_states(agents, winning_states))
            winning_states = list(resultStates)
            if result_states_length == len(resultStates):
                break

            result_states_length = len(resultStates)
            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return resultStates

    def minimum_formula_one_agent_multiple_states(self, agent, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        while True:
            current_states = self.basic_formula_one_agent_multiple_states(agent, current_states, winning_states)
            result_states.update(current_states)
            winning_states = list(result_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)
            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def minimum_formula_one_agent_multiple_states_perfect_information(self, agent, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        while True:
            current_states = self.basic_formula_one_agent_multiple_states_perfect_information(agent, current_states,
                                                                                              winning_states)
            result_states.update(current_states)
            winning_states = list(result_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)
            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def maximum_formula_multiple_agents_and_states(self, agents, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        first_winning_states = list(winning_states)
        while True:
            result_states = set(and_operator(first_winning_states,
                                             self.basic_formula_multiple_agents_and_states(agents, winning_states)))

            winning_states = list(result_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)
            number_of_iterations += 1

        print('Maximum formula iterations:', number_of_iterations)
        return result_states

    def is_possible_transition(self, agents, action, transition):
        for i, j in zip(agents, range(0, len(agents))):
            if transition['actions'][i] != action[j]:
                return False
        return True

    def create_agents_actions_combinations(self, agents):
        combinations = []
        possible_actions = []
        for a in agents:
            possible_actions.append(self.agents_actions[a])

        for t in itertools.product(*possible_actions):
            combinations.append(t)

        return combinations

    def set_state_name(self, state_number, name):
        self.state_names[state_number] = name

    def set_state_descriptions(self, state_number, description):
        self.state_descriptions[state_number] = description
