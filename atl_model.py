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
    numberOfAgents = 0
    agentNames = {}
    numberOfStates = 0
    transitions = []
    reverseTransitions = []
    reverseStates = []
    imperfectInformation = []
    agentsActions = []
    stateNames = []
    stateDescriptions = []
    states = []

    def __init__(self, number_of_agents, number_of_states):
        self.numberOfAgents = number_of_agents
        self.numberOfStates = number_of_states
        self.transitions = [[] for i in itertools.repeat(None, number_of_states)] #create_array_of_size(number_of_states, [])
        # print(self.transitions)
        self.reverseTransitions = [[] for i in itertools.repeat(None, number_of_states)] # create_array_of_size(number_of_states, [])
        self.imperfectInformation = create_array_of_size(number_of_agents, [])
        self.reverseStates = [[] for i in itertools.repeat(None, number_of_states)] #create_array_of_size(number_of_states, [])
        self.agentsActions = [[] for i in itertools.repeat(None, number_of_states)] #create_array_of_size(number_of_agents, [])
        # self.stateNames = create_array_of_size(number_of_states, [])
        # self.stateDescriptions = create_array_of_size(number_of_states, [])
        for i in range(0, 1):#number_of_agents):
            self.imperfectInformation[i] = [set() for i in itertools.repeat(None, number_of_states)] #create_array_of_size(number_of_states, [])
            for j in range(0, number_of_states):
                self.imperfectInformation[i][j].add(j)

    def add_action(self, agent, action):
        self.agentsActions[agent].append(action)

    def add_transition(self, from_state, to_state, actions):
        self.transitions[from_state].append({'nextState': to_state, 'actions': actions})
        self.reverseTransitions[to_state].append({'nextState': from_state, 'actions': actions})
        #if from_state not in self.reverseStates[to_state]:
        self.reverseStates[to_state].append(from_state)
        # for i in range(0, self.numberOfAgents):
        #     if actions[i] not in self.agentsActions[i]:
        #         self.agentsActions[i].append(actions[i])
                # print(self.transitions)
                # print(self.reverseStates)

    def is_same_state(self, agent_number, state_a, state_b):
        return state_b in self.imperfectInformation[agent_number][state_a]

    def set_same_state(self, agent_number, state_a, state_b):
        # if state_b not in self.imperfectInformation[agent_number][state_a]:
        self.imperfectInformation[agent_number][state_a].add(state_b)
        self.imperfectInformation[agent_number][state_b].add(state_a)

    def basic_formula(self, agent_number, winning_state):
        result_states = []
        for state in self.reverseStates[winning_state]:
            ok = True
            for sameState in self.imperfectInformation[agent_number][state]:
                if not self.is_reachable_by_agent(sameState, winning_state, agent_number):
                    ok = False
                    break
            if ok:
                result_states.append(state)
        return result_states

    def is_reachable_by_agent(self, from_state, to_state, agent):
        for action in self.agentsActions[agent]:
            action_ok = False
            for transition in self.transitions[from_state]:
                if transition['actions'][agent] == action:
                    action_ok = True
                    if transition['nextState'] != to_state:
                        action_ok = False
                        break
            if action_ok:
                return True
        return False

    def basic_formula_multiple_agents(self, agents, winning_state):
        result_states = []
        actions = self.create_agents_actions_combinations(agents)
        for state in self.reverseStates[winning_state]:
            ok = True
            same_states = self.get_same_states_for_agents(agents, state)
            for sameState in same_states:
                if not self.is_reachable_by_agents(actions, sameState, [winning_state], agents):
                    ok = False
                    break
            if ok:
                result_states.append(state)
        return result_states

    def get_same_states_for_agents(self, agents, state):
        same_states = []
        for agent in agents:
            for sameState in self.imperfectInformation[agent][state]:
                if sameState not in same_states:
                    same_states.append(sameState)
        return same_states

    def is_reachable_by_agents(self, actions, fromState, toStates, agents):
        for action in actions:
            actionOk = False
            for transition in self.transitions[fromState]:
                if self.is_possible_transition(agents, action, transition):
                    actionOk = True
                    if transition['nextState'] not in toStates:
                        actionOk = False
                        break
            if actionOk:
                return True
        return False

    def is_reachable_by_agent(self, actions, fromState, toStates, agent):
        for action in actions:
            actionOk = False
            for transition in self.transitions[fromState]:
                if transition['actions'][0] == action:
                    actionOk = True
                    if transition['nextState'] not in toStates:
                        actionOk = False
                        break
            if actionOk:
                return True
        return False

    def basic_formula_multiple_agents_and_states(self, agents, winningStates):
        resultStates = set()
        actions = self.create_agents_actions_combinations(agents)
        winning_states_reverse = []
        for winningState in winningStates:
            winning_states_reverse += self.reverseStates[winningState]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            ok = True
            sameStates = self.get_same_states_for_agents(agents, state)
            winning_states_reverse_same = [state]

            for sameState in sameStates:
                if ok and not self.is_reachable_by_agents(actions, sameState, winningStates, agents):
                    ok = False
                if sameState != state and sameState in winning_states_reverse:
                    winning_states_reverse.remove(sameState)
                    winning_states_reverse_same.append(sameState)
            if ok:
                resultStates.update(winning_states_reverse_same)
        return resultStates

    def basic_formula_one_agent_multiple_states(self, agent, current_states, winning_states):
        result_states = set()
        actions = self.agentsActions[agent]
        winning_states_reverse = []
        for winning_state in current_states:
            winning_states_reverse += self.reverseStates[winning_state]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            ok = True
            same_states = self.imperfectInformation[agent][state]
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
        actions = self.agentsActions[agent]
        winning_states_reverse = []
        for winning_state in current_states:
            winning_states_reverse += self.reverseStates[winning_state]

        unique(winning_states_reverse)

        for state in winning_states_reverse:
            if self.is_reachable_by_agent(actions, state, winning_states, agent):
                result_states.add(state)

        return result_states

    def minimum_formula_multiple_agents_and_states(self, agents, winning_states):
        resultStates = set()
        resultStates.update(winning_states)
        resultStatesLength = len(resultStates)
        number_of_iterations = 0
        while True:
            resultStates.update(self.basic_formula_multiple_agents_and_states(agents, winning_states))
            winning_states = list(resultStates)
            if resultStatesLength == len(resultStates):
                break

            resultStatesLength = len(resultStates)
            number_of_iterations += 1


        print('Minimum formula iterations:', number_of_iterations)
        return resultStates

    def minimum_formula_one_agent_multiple_states(self, agent, winningStates):
        resultStates = set()
        resultStates.update(winningStates)
        resultStatesLength = len(resultStates)
        number_of_iterations = 0
        current_states = winningStates[:]
        while True:
            current_states = self.basic_formula_one_agent_multiple_states(agent, current_states, winningStates)
            resultStates.update(current_states)
            winningStates = list(resultStates)
            if resultStatesLength == len(resultStates):
                break

            resultStatesLength = len(resultStates)
            number_of_iterations += 1


        print('Minimum formula iterations:', number_of_iterations)
        return resultStates

    def minimum_formula_one_agent_multiple_states_perfect_information(self, agent, winningStates):
        resultStates = set()
        resultStates.update(winningStates)
        resultStatesLength = len(resultStates)
        number_of_iterations = 0
        current_states = winningStates[:]
        while True:
            current_states = self.basic_formula_one_agent_multiple_states_perfect_information(agent, current_states, winningStates)
            resultStates.update(current_states)
            winningStates = list(resultStates)
            if resultStatesLength == len(resultStates):
                break

            resultStatesLength = len(resultStates)
            number_of_iterations += 1


        print('Minimum formula iterations:', number_of_iterations)
        return resultStates

    def maximum_formula_multiple_agents_and_states(self, agents, winningStates):
        resultStates = set()
        resultStates.update(winningStates)
        resultStatesLength = len(resultStates)
        number_of_iterations = 0
        first_winning_states = list(winningStates)
        while True:
            resultStates = set(and_operator(first_winning_states, self.basic_formula_multiple_agents_and_states(agents, winningStates)))

            winningStates = list(resultStates)
            if resultStatesLength == len(resultStates):
                break

            resultStatesLength = len(resultStates)
            number_of_iterations += 1

        print('Maximum formula iterations:', number_of_iterations)
        return resultStates



    def is_possible_transition(self, agents, action, transition):
        for i, j in zip(agents, range(0, len(agents))):
            if transition['actions'][i] != action[j]:
                return False
        return True

    def create_agents_actions_combinations(self, agents):
        combinations = []
        possibleActions = []
        for a in agents:
            possibleActions.append(self.agentsActions[a])

        for t in itertools.product(*possibleActions):
            combinations.append(t)

        return combinations

    def set_state_name(self, stateNumber, name):
        self.stateNames[stateNumber] = name

    def set_state_descriptions(self, stateNumber, description):
        self.stateDescriptions[stateNumber] = description