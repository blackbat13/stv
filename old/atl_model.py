# DEPRECATED

import itertools
import copy
from tools.disjoint_set import *

__author__ = 'blackbat'


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


class ATLModel:
    number_of_agents = 0
    number_of_states = 0
    transitions = []
    reverse_transitions = []
    pre_states = []
    imperfect_information = []
    agents_actions = []
    states = []
    epistemic_class_membership = []
    epistemic_class_disjoint = None
    can_go_there = []

    def __init__(self, number_of_agents, number_of_states):
        self.number_of_agents = number_of_agents
        self.number_of_states = number_of_states
        self.init_transitions()
        self.init_states()
        self.init_actions()
        self.init_epistemic_relation()
        self.can_go_there = [[] for _ in itertools.repeat(None, number_of_agents)]

    def init_transitions(self):
        self.transitions = [[] for _ in itertools.repeat(None, self.number_of_states)]
        self.reverse_transitions = [[] for _ in itertools.repeat(None, self.number_of_states)]

    def init_states(self):
        self.pre_states = [set() for _ in itertools.repeat(None, self.number_of_states)]

    def init_actions(self):
        self.agents_actions = [[] for _ in itertools.repeat(None, self.number_of_agents)]

    def init_epistemic_relation(self):
        self.epistemic_class_membership = create_array_of_size(self.number_of_agents, [])
        self.epistemic_class_disjoint = [DisjointSet(self.number_of_states) for _ in
                                         itertools.repeat(None, self.number_of_agents)]
        self.imperfect_information = create_array_of_size(self.number_of_agents, [])
        for i in range(0, self.number_of_agents):
            self.imperfect_information[i] = []
            self.epistemic_class_membership[i] = [-1 for _ in itertools.repeat(None, self.number_of_states)]

    def add_action(self, agent, action):
        self.agents_actions[agent].append(action)

    def enlarge_transitions(self, size):
        if len(self.transitions) <= size:
            to_add = size - len(self.transitions) + 1
            for i in range(0, to_add):
                self.transitions.append([])
                self.reverse_transitions.append([])
                self.pre_states.append(set())

    def max(self, a, b):
        if a > b:
            return a
        else:
            return b

    def add_transition(self, from_state, to_state, actions):
        self.enlarge_transitions(self.max(from_state, to_state))
        if {'nextState': to_state, 'actions': actions} not in self.transitions[from_state]:
            self.transitions[from_state].append({'nextState': to_state, 'actions': actions.copy()})
            self.reverse_transitions[to_state].append({'nextState': from_state, 'actions': actions.copy()})
            self.pre_states[to_state].add(from_state)

    def add_epistemic_class(self, agent_number, epistemic_class):
        self.imperfect_information[agent_number].append(set(epistemic_class))
        epistemic_class_number = len(self.imperfect_information[agent_number]) - 1
        first_state = next(iter(epistemic_class))
        for state in epistemic_class:
            self.epistemic_class_membership[agent_number][state] = epistemic_class_number
            self.epistemic_class_disjoint[agent_number].union(first_state, state)

        self.find_where_can_go(epistemic_class, epistemic_class_number, agent_number)

    def find_where_can_go(self, epistemic_class, epistemic_class_number, agent_number):
        if len(self.can_go_there[agent_number]) == 0:
            self.can_go_there[agent_number] = [{} for _ in itertools.repeat(None, self.number_of_states)]

        for action in self.agents_actions[agent_number]:
            can_go_temp = set()
            is_first = True
            for state in epistemic_class:
                can_go_state_temp = set()
                for transition in self.transitions[state]:
                    if transition['actions'][agent_number] == action:
                        can_go_state_temp.add(transition['nextState'])

                if is_first:
                    is_first = False
                    can_go_temp = set(can_go_state_temp)
                else:
                    can_go_temp |= can_go_state_temp

                if len(can_go_state_temp) == 0:
                    can_go_temp = set()
                    break

            self.can_go_there[agent_number][epistemic_class_number][action] = can_go_temp

    def basic_formula(self, agent_number, winning_state):
        result_states = []
        for state in self.pre_states[winning_state]:
            ok = True
            for same_state in self.imperfect_information[agent_number][state]:
                if not self.is_reachable_by_agent(same_state, winning_state, agent_number):
                    ok = False
                    break
            if ok:
                result_states.append(state)
        return result_states

    def is_reachable_by_agents_in_set(self, action, from_state, winning_states, agents):
        action_ok = False
        for transition in self.transitions[from_state]:
            if self.is_possible_transition(agents, action, transition):
                action_ok = True
                if not (transition['nextState'] in winning_states):
                    return False

        return action_ok

    def is_reachable_by_agent_disjoint(self, action, from_state, agent, first_winning, winning_states_disjoint):
        action_ok = False
        for transition in self.transitions[from_state]:
            if transition['actions'][agent] == action:
                action_ok = True
                if not winning_states_disjoint.is_in_union(first_winning, transition['nextState']):
                    return False

        return action_ok

    def is_reachable_by_agent(self, action, from_state, is_winning_state, agent):
        action_ok = False
        for transition in self.transitions[from_state]:
            if transition['actions'][agent] == action:
                action_ok = True
                if not is_winning_state[transition['nextState']]:
                    return False

        return action_ok

    def is_reachable_by_agent_in_set(self, action, from_state, winning_states, agent):
        action_ok = False
        for transition in self.transitions[from_state]:
            if transition['actions'][agent] == action:
                action_ok = True
                if not (transition['nextState'] in winning_states):
                    return False

        return action_ok

    def get_agents_actions(self, agents):
        actions = []
        for agent in agents:
            actions.append(self.agents_actions[agent])

        return actions

    def basic_formula_one_agent_multiple_states_disjoint(self, agent, current_states, first_winning,
                                                         winning_states_disjoint,
                                                         custom_can_go_there):
        result_states = []
        actions = self.agents_actions[agent]
        preimage = set()
        modified = False
        for winning_state in current_states:
            for pre_state in self.pre_states[winning_state]:
                preimage.add(self.epistemic_class_membership[agent][pre_state])

        first_winning = winning_states_disjoint.find(first_winning)

        for state_epistemic_class in preimage:
            state = next(iter(self.imperfect_information[agent][state_epistemic_class]))
            state = winning_states_disjoint.find(state)
            if state == first_winning:
                continue

            if state_epistemic_class == -1:
                print("ERROR")
                same_states = [state]
            else:
                same_states = self.imperfect_information[agent][state_epistemic_class]

            for action in actions:
                states_can_go = custom_can_go_there[state_epistemic_class][action]

                if len(states_can_go) == 0:
                    continue

                is_ok = True
                new_states_can_go = set()

                for state_can in states_can_go:
                    new_state_can = winning_states_disjoint.find(state_can)

                    if first_winning != new_state_can:
                        is_ok = False

                    new_states_can_go.add(new_state_can)

                custom_can_go_there[state_epistemic_class][action] = new_states_can_go

                if is_ok:
                    result_states.extend(same_states)
                    winning_states_disjoint.union(first_winning, state)
                    first_winning = winning_states_disjoint.find(first_winning)
                    modified = True
                    break

        return {'result': result_states, 'modified': modified}

    def basic_formula_one_agent_multiple_states_disjoint_mcmas_approach(self, agent, current_states, first_winning,
                                                         winning_states_disjoint,
                                                         custom_can_go_there):
        result_states = []
        actions = self.agents_actions[agent]
        preimage = set()
        modified = False
        for winning_state in current_states:
            for pre_state in self.pre_states[winning_state]:
                preimage.add(self.epistemic_class_membership[agent][pre_state])

        first_winning = winning_states_disjoint.find(first_winning)

        for state_epistemic_class in preimage:
            state = next(iter(self.imperfect_information[agent][state_epistemic_class]))
            state = winning_states_disjoint.find(state)
            if state == first_winning:
                continue

            if state_epistemic_class == -1:
                print("ERROR")
                same_states = [state]
            else:
                same_states = self.imperfect_information[agent][state_epistemic_class]

            all_actions = set()
            bad_actions = set()
            for same_state in same_states:
                for transition in self.transitions[same_state]:
                    all_actions.add(transition['actions'][agent])
                    if winning_states_disjoint.find(transition['nextState']) != first_winning:
                        bad_actions.add(transition['actions'][agent])

            all_actions -= bad_actions
            if len(all_actions) > 0:
                result_states.extend(same_states)
                winning_states_disjoint.union(first_winning, state)
                first_winning = winning_states_disjoint.find(first_winning)
                modified = True

        return {'result': result_states, 'modified': modified}

    def basic_formula_one_agent_multiple_states(self, agent, current_states, is_winning_state):
        result_states = set()
        actions = self.agents_actions[agent]
        preimage = []
        for winning_state in current_states:
            preimage += self.pre_states[winning_state]

        unique(preimage)
        for state in preimage:
            state_epistemic_class = self.epistemic_class_membership[agent][state]
            if state_epistemic_class == -1:
                same_states = [state]
            else:
                same_states = self.imperfect_information[agent][state_epistemic_class]

            for action in actions:
                good_states = []
                number_of_good = 0
                should_break = False
                is_good_state = {}

                for same_state in same_states:
                    is_good_state[same_state] = False
                    if self.is_reachable_by_agent(action, same_state, is_winning_state, agent):
                        good_states.append(same_state)
                        is_good_state[same_state] = True
                        number_of_good += 1
                    elif not self.is_reachable_by_agent_in_set(action, same_state, same_states, agent):
                        should_break = True
                        # else: # for standard model
                        #     should_break = True

                if should_break:
                    continue

                modified = True
                while modified:
                    modified = False
                    for same_state in same_states:
                        if is_good_state[same_state]:
                            continue
                        if self.is_reachable_by_agent_in_set(action, same_state, good_states, agent):
                            good_states.append(same_state)
                            is_good_state[same_state] = True
                            number_of_good += 1
                            modified = True

                if number_of_good == len(same_states):
                    result_states.update(same_states)
                    break

            for same_state in same_states:
                if same_state != state and same_state in preimage:
                    preimage.remove(same_state)

        for state_number in result_states:
            is_winning_state[state_number] = True

        return result_states

    def basic_formula_one_agent_multiple_states_mcmas_approach(self, agent, current_states, is_winning_state):
        result_states = set()
        actions = self.agents_actions[agent]
        preimage = []
        for winning_state in current_states:
            preimage += self.pre_states[winning_state]

        unique(preimage)
        for state in preimage:
            state_epistemic_class = self.epistemic_class_membership[agent][state]
            if state_epistemic_class == -1:
                same_states = [state]
            else:
                same_states = self.imperfect_information[agent][state_epistemic_class]

            all_actions = set()
            bad_actions = set()
            for same_state in same_states:
                for transition in self.transitions[same_state]:
                    all_actions.add(transition['actions'][agent])
                    if not is_winning_state[transition['nextState']]:
                        bad_actions.add(transition['actions'][agent])

            all_actions -= bad_actions
            if len(all_actions) > 0:
                result_states.update(same_states)

            for same_state in same_states:
                if same_state != state and same_state in preimage:
                    preimage.remove(same_state)

        for state_number in result_states:
            is_winning_state[state_number] = True

        return result_states

    def basic_formula_multiple_agents_and_states_perfect_information(self, agents, current_states, is_winning_state):
        result_states = set()
        actions = self.get_agents_actions(agents)
        winning_states_reverse = []
        for winning_state in current_states:
            winning_states_reverse += self.pre_states[winning_state]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            for action in itertools.product(*actions):
                if self.is_reachable_by_agents(action, state, is_winning_state, agents):
                    result_states.add(state)

        for state_number in result_states:
            is_winning_state[state_number] = True

        return result_states

    def basic_formula_one_agent_multiple_states_perfect_information(self, agent, current_states, is_winning_state):
        result_states = set()
        actions = self.agents_actions[agent]
        winning_states_reverse = []
        for winning_state in current_states:
            winning_states_reverse += self.pre_states[winning_state]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            for action in actions:
                if self.is_reachable_by_agent(action, state, is_winning_state, agent):
                    result_states.add(state)

        for state_number in result_states:
            is_winning_state[state_number] = True

        return result_states

    def basic_formula_one_agent_multiple_states_perfect_information_mcmas_approach(self, agent, current_states, is_winning_state):
        result_states = set()
        actions = self.agents_actions[agent]
        winning_states_reverse = []
        for winning_state in current_states:
            winning_states_reverse += self.pre_states[winning_state]

        unique(winning_states_reverse)
        for state in winning_states_reverse:
            all_actions = set()
            bad_actions = set()
            for transition in self.transitions[state]:
                all_actions.add(transition['actions'][agent])
                if not is_winning_state[transition['nextState']]:
                    bad_actions.add(transition['actions'][agent])

            all_actions -= bad_actions
            if len(all_actions) > 0:
                result_states.add(state)

        for state_number in result_states:
            is_winning_state[state_number] = True

        return result_states

    def minimum_formula_multiple_agents_and_states(self, agents, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        is_winning_state = [False for _ in itertools.repeat(None, self.number_of_states)]
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_multiple_agents_and_states(agents, current_states, is_winning_state)
            result_states.update(current_states)
            new_results_states_length = len(result_states)
            if result_states_length == new_results_states_length:
                break

            result_states_length = new_results_states_length
            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def minimum_formula_one_agent_multiple_states_disjoint(self, agent, winning_states):
        if len(winning_states) == 0:
            return []

        result_states = set()
        result_states.update(winning_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        winning_states_disjoint = DisjointSet(0)
        winning_states_disjoint.subsets = copy.deepcopy(self.epistemic_class_disjoint[agent].subsets)
        first_winning = winning_states_disjoint.find(winning_states[0])
        epistemic_class_numbers = set()
        for state_number in winning_states:
            epistemic_class_number = self.epistemic_class_membership[agent][state_number]
            epistemic_class_numbers.add(epistemic_class_number)

        for epistemic_class_number in epistemic_class_numbers:
            epistemic_states = self.imperfect_information[agent][epistemic_class_number]
            is_ok = True
            for epistemic_state in epistemic_states:
                state_number = epistemic_state
                if epistemic_state not in winning_states:
                    is_ok = False
                    break
            if is_ok:
                winning_states_disjoint.union(first_winning, state_number)

        custom_can_go_there = self.can_go_there[agent][:]

        while True:
            formula_result = self.basic_formula_one_agent_multiple_states_disjoint(agent, current_states, first_winning,
                                                                                   winning_states_disjoint,
                                                                                   custom_can_go_there)
            current_states = formula_result['result']
            modified = formula_result['modified']
            result_states.update(current_states)
            if not modified:
                break

            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def minimum_formula_one_agent_multiple_states_disjoint_mcmas_approach(self, agent, winning_states):
        if len(winning_states) == 0:
            return []

        result_states = set()
        result_states.update(winning_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        winning_states_disjoint = DisjointSet(0)
        winning_states_disjoint.subsets = copy.deepcopy(self.epistemic_class_disjoint[agent].subsets)
        first_winning = winning_states_disjoint.find(winning_states[0])
        epistemic_class_numbers = set()
        for state_number in winning_states:
            epistemic_class_number = self.epistemic_class_membership[agent][state_number]
            epistemic_class_numbers.add(epistemic_class_number)

        for epistemic_class_number in epistemic_class_numbers:
            epistemic_states = self.imperfect_information[agent][epistemic_class_number]
            is_ok = True
            for epistemic_state in epistemic_states:
                state_number = epistemic_state
                if epistemic_state not in winning_states:
                    is_ok = False
                    break
            if is_ok:
                winning_states_disjoint.union(first_winning, state_number)

        custom_can_go_there = self.can_go_there[agent][:]

        while True:
            formula_result = self.basic_formula_one_agent_multiple_states_disjoint_mcmas_approach(agent, current_states, first_winning,
                                                                                   winning_states_disjoint,
                                                                                   custom_can_go_there)
            current_states = formula_result['result']
            modified = formula_result['modified']
            result_states.update(current_states)
            if not modified:
                break

            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def minimum_formula_one_agent_multiple_states(self, agent, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        is_winning_state = [False for _ in itertools.repeat(None, self.number_of_states)]
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_one_agent_multiple_states(agent, current_states, is_winning_state)
            result_states.update(current_states)
            new_results_states_length = len(result_states)
            if result_states_length == new_results_states_length:
                break

            result_states_length = new_results_states_length
            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def minimum_formula_multiple_agents_and_states_perfect_information(self, agents, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        is_winning_state = [False for _ in itertools.repeat(None, self.number_of_states)]
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_multiple_agents_and_states_perfect_information(agents, current_states,
                                                                                               is_winning_state)
            result_states.update(current_states)
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
        is_winning_state = [False for _ in itertools.repeat(None, self.number_of_states)]
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_one_agent_multiple_states_perfect_information(agent, current_states,
                                                                                              is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)
            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def minimum_formula_one_agent_multiple_states_perfect_information_mcmas_approach(self, agent, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        is_winning_state = [False for _ in itertools.repeat(None, self.number_of_states)]
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_one_agent_multiple_states_perfect_information_mcmas_approach(agent, current_states,
                                                                                              is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)
            number_of_iterations += 1

        print('Minimum formula iterations:', number_of_iterations)
        return result_states

    def maximum_formula_one_agent_multiple_states(self, agent, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        is_winning_state = [False for _ in itertools.repeat(None, self.number_of_states)]
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_one_agent_multiple_states(agent, current_states, is_winning_state)
            result_states = set(and_operator(result_states, current_states))
            if result_states_length == len(result_states):
                break

            for state_number in result_states:
                if state_number not in current_states:
                    is_winning_state[state_number] = False

            result_states_length = len(result_states)
            number_of_iterations += 1

        print('Maximum formula iterations:', number_of_iterations)
        return result_states

    def maximum_formula_one_agent_multiple_states_perfect_information(self, agent, winning_states):
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        number_of_iterations = 0
        current_states = winning_states[:]
        is_winning_state = [False for _ in itertools.repeat(None, self.number_of_states)]
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_one_agent_multiple_states_perfect_information(agent, current_states,
                                                                                              is_winning_state)
            result_states = set(and_operator(result_states, current_states))
            if result_states_length == len(result_states):
                break

            for state_number in result_states:
                if state_number not in current_states:
                    is_winning_state[state_number] = False

            result_states_length = len(result_states)
            number_of_iterations += 1

        print('Maximum formula iterations:', number_of_iterations)
        return result_states

    def create_agents_actions_combinations(self, agents):
        combinations = []
        possible_actions = []
        for a in agents:
            possible_actions.append(self.agents_actions[a])

        for t in itertools.product(*possible_actions):
            combinations.append(t)

        return combinations

    def walk_perfect_information(self, agent_number):
        print("#####################################################")
        print("Simulation")
        current_state = 0
        while True:
            print()
            print("Current state:", self.states[current_state])

            if len(self.transitions[current_state]) == 0:
                print("End")
                return

            print('Transitions:')
            i = 0
            for transition in self.transitions[current_state]:
                print(str(i) + ":", transition)
                i += 1

            choice = int(input("Choose transition="))
            if choice == -1:
                print("End")
                return

            current_state = self.transitions[current_state][choice]['nextState']

    def walk(self, agent_number, print_state):
        print("#####################################################")
        print("Simulation")
        current_state = 0
        while True:
            print()
            print("Current state:")
            print_state(self.states[current_state])
            print("Epistemic states:")
            for state in self.imperfect_information[agent_number][
                self.epistemic_class_membership[agent_number][current_state]]:
                print_state(self.states[state])

            if len(self.transitions[current_state]) == 0:
                print("End")
                return

            print('Transitions:')
            i = 0
            for transition in self.transitions[current_state]:
                print(str(i) + ":", transition)
                i += 1

            choice = int(input("Choose transition="))
            if choice == -1:
                print("End")
                return

            current_state = self.transitions[current_state][choice]['nextState']

    @staticmethod
    def is_possible_transition(agents, action, transition):
        for i, j in zip(agents, range(0, len(agents))):
            if transition['actions'][i] != action[j]:
                return False
        return True