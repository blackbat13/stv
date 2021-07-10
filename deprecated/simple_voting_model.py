# DEPRECATED

from deprecated.atl_model import *
import time

# import resource

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
        if self.number_of_voters == 1:
            self.model = ATLModel(self.number_of_voters + 1, 15)
        elif self.number_of_voters == 2:
            self.model = ATLModel(self.number_of_voters + 1, 225)
        elif self.number_of_voters == 3:
            self.model = ATLModel(self.number_of_voters + 1, 3375)
        elif self.number_of_voters == 4:
            self.model = ATLModel(self.number_of_voters + 1, 50625)
        elif self.number_of_voters == 5:
            self.model = ATLModel(self.number_of_voters + 1, 759375)
        else:
            self.model = ATLModel(self.number_of_voters + 1, 1000000)
        self.add_actions()

        beginning_array = []
        for _ in range(0, self.number_of_voters):
            beginning_array.append('')

        beginning_array_minus_one = []
        for _ in range(0, self.number_of_voters):
            beginning_array_minus_one.append(-1)

        first_state = {'voted': beginning_array_minus_one[:], 'voters_action': beginning_array[:],
                       'coercer_actions': beginning_array[:], 'finish': beginning_array_minus_one[:]}
        state_number = 0

        # self.print_create_for_state(0, first_state)

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
                elif state['voters_action'][voter_number] == '':
                    voting_product_array.append(['give', 'ng', 'wait'])
                elif state['coercer_actions'][voter_number] == '':
                    coercer_possible_actions.append('np' + str(voter_number + 1))
                    coercer_possible_actions.append('pun' + str(voter_number + 1))
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
                voter_not_voted = False

                for voter_number in range(0, self.number_of_voters):
                    action[voter_number + 1] = possibility[voter_number]
                    voter_action_string = str(possibility[voter_number])
                    if voter_action_string[0] == 'g' or voter_action_string[0] == 'n':
                        new_state['voters_action'][voter_number] = voter_action_string
                        voter_not_voted = True
                    elif voter_action_string[0] != 'w':
                        new_state['voted'][voter_number] = possibility[voter_number]
                    # else:
                    #     voter_not_voted = True

                if state['voted'][0] == -1 and new_state['voted'][1] != -1:
                    continue

                coercer_acted = False
                action[0] = possibility[self.number_of_voters]
                if action[0][0:3] == 'pun':
                    pun_voter_number = int(action[0][3:])
                    new_state['coercer_actions'][pun_voter_number - 1] = 'pun'
                    new_state['finish'][pun_voter_number - 1] = 1
                    coercer_acted = True
                elif action[0][0:2] == 'np':
                    np_voter_number = int(action[0][2:])
                    new_state['coercer_actions'][np_voter_number - 1] = 'np'
                    new_state['finish'][np_voter_number - 1] = 1
                    coercer_acted = True

                # print(new_state['voters_action'])
                if not ((action[1] == 'give' or action[1] == 'ng') and (action[2] == 'give' or action[2] == 'ng')):
                    if (state['voted'][0] == -1 or state['voted'][1] == -1) and (coercer_acted or action[1] == 'give' or action[1] == 'ng' or action[2] == 'give' or action[2] == 'ng'):
                        continue

                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                if new_state_str not in self.states_dictionary:
                    self.states_dictionary[new_state_str] = state_number
                    new_state_number = state_number
                    self.states.append(new_state)
                    state_number += 1
                    # self.print_create_for_state(new_state_number, new_state)
                else:
                    new_state_number = self.states_dictionary[new_state_str]

                # self.print_create_transition(current_state_number, new_state_number, action)
                self.model.add_transition(current_state_number, new_state_number, action)

            self.add_epistemic_state(state, current_state_number)
            self.add_voter_epistemic_state(state, current_state_number)

        self.prepare_epistemic_class()
        self.model.states = self.states

    def print_create_for_state(self, state_number, state):
        print("CREATE (S" + str(state_number) + ":State {voted: " + str(state['voted']) + ", voters_action: " + str(
            state['voters_action']) + ", coercer_actions: " + str(state['coercer_actions']) + ", finish: " + str(
            state['finish']) + "})")

    def print_create_transition(self, from_state_number, to_state_number, actions):
        create_str = "CREATE (S" + str(from_state_number) + ")-[:ACTION {"
        for i in range(0, len(actions)):
            create_str += "A" + str(i) + ":['" + str(actions[i]) + "'], "
        create_str = create_str.rstrip(" ,")
        create_str += "}]->(S" + str(to_state_number) + ")"
        print(create_str)

    def generate_simultaneously_voting(self):
        self.model = ATLModel(self.number_of_voters + 1, 1000)
        self.add_actions()

        beginning_array = []
        for _ in range(0, self.number_of_voters):
            beginning_array.append(-1)

        # first_state = {'voted': beginning_array_minus_one[:], 'voters_action': beginning_array[:],
        #                'coercer_actions': beginning_array[:], 'finish': beginning_array_minus_one[:]}

        first_state = {'voted': beginning_array[:], 'voters_action': beginning_array[:],
                       'coercer_actions': beginning_array[:], 'finish': beginning_array[:]}
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
            # is_finish_state = False
            if state['voted'][0] == -1:
                for voting_product in itertools.product(*voting_product_array):
                    new_state = {}
                    new_state['voted'] = state['voted'][:]
                    new_state['voters_action'] = state['voters_action'][:]
                    new_state['coercer_actions'] = state['coercer_actions'][:]
                    new_state['finish'] = state['finish'][:]

                    action = {0: 'wait'}
                    for voter_number in range(0, self.number_of_voters):
                        new_state['voted'][voter_number] = voting_product[voter_number]
                        action[voter_number + 1] = voting_product[voter_number]

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
                    new_state['finish'] = state['finish'][:]

                    action = {0: 'wait'}

                    for voter_number in range(0, self.number_of_voters):
                        new_state['voters_action'][voter_number] = decision_product[voter_number]
                        action[voter_number + 1] = decision_product[voter_number]

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

                # is_finish_state = True
                for voter_number in range(1, self.number_of_voters + 1):
                    if state['coercer_actions'][voter_number - 1] == -1:
                        # is_finish_state = False

                        new_state = {}
                        new_state['voted'] = state['voted'][:]
                        new_state['voters_action'] = state['voters_action'][:]
                        new_state['coercer_actions'] = state['coercer_actions'][:]
                        new_state['coercer_actions'][voter_number - 1] = 'pun'
                        new_state['finish'] = state['finish'][:]
                        new_state['finish'][voter_number - 1] = 1
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
                        new_state2['finish'] = state['finish'][:]
                        new_state2['finish'][voter_number - 1] = 1
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

            # state['finish'] = is_finish_state
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

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def generate_tex(self):
        current_state = 0
        path = "\t\path (0,0) node[initstate] (q0) {$q_{0}$}\n"
        transitions = ""
        level = 0

        visited = []
        for i in range(0, len(self.states)):
            visited.append(0)

        visited[0] = 1
        current_level_states = []
        transitions += "\t\path[->,font=\scriptsize] (q0)"
        for transition in self.model.transitions[current_state]:
            not_wait = 0
            for i in range(1, self.number_of_voters + 1):
                if transition['actions'][i] != 'wait':
                    not_wait += 1

            if transition['actions'][0] != 'wait':
                not_wait += 1

            if visited[transition['nextState']] == 0 and not_wait == 1:
                action = "("
                for i in range(1, self.number_of_voters+1):
                    if transition['actions'][i] != 'wait':
                        action += 'vote' + str(transition['actions'][i] + 1) + ','
                    else:
                        action += "-,"

                action += '-)'
                transitions += "\n"
                transitions += "\t\tedge\n"
                transitions += "\t\t\tnode[midway,sloped]{\onlabel{$"+action+"$}} (q" + str(transition['nextState']) + ")"
                current_level_states.append(transition['nextState'])
                visited[transition['nextState']] = 1

        transitions += ";\n"
        state_num = 1

        level_dictionary = {}
        on_this_level = {}

        for state in self.states:
            level_number = 0
            for i in range(0, len(state['voted'])):
                voted = state['voted'][i]
                if voted != -1:
                    level_number += 1

            for i in range(0, len(state['voters_action'])):
                action = state['voters_action'][i]
                if action != '':
                    level_number += 1

            for i in range(0, len(state['coercer_actions'])):
                action = state['coercer_actions'][i]
                if action != '':
                    level_number += 1

            for i in range(0, len(state['finish'])):
                action = state['finish'][i]
                if action != -1:
                    level_number += 1

            level = -5 * level_number
            if level not in level_dictionary:
                level_dictionary[level] = 0
            else:
                level_dictionary[level] += 1

        while len(current_level_states) > 0:
            level -= 5
            left = -1 * len(current_level_states)
            new_states = []
            for state in current_level_states:
                # print(self.states[state])
                level_number = 0
                for i in range(0, len(self.states[state]['voted'])):
                    voted = self.states[state]['voted'][i]
                    if voted != -1:
                        level_number += 1

                for i in range(0, len(self.states[state]['voters_action'])):
                    action = self.states[state]['voters_action'][i]
                    if action != '':
                        level_number += 1

                for i in range(0, len(self.states[state]['coercer_actions'])):
                    action = self.states[state]['coercer_actions'][i]
                    if action != '':
                        level_number += 1

                for i in range(0, len(self.states[state]['finish'])):
                    action = self.states[state]['finish'][i]
                    if action != -1:
                        level_number += 1

                level = -5 * level_number

                if level not in on_this_level:
                    on_this_level[level] = 0
                else:
                    on_this_level[level] += 1

                left = level_dictionary[level] * -2 + on_this_level[level] * 4

                path += "\t\t(" + str(left) + "," + str(level) + ") node[state]  (q" + str(state) + ") {$q_{" + str(
                    state) + "}$}\n"

                val = -0.5
                for i in range(0, len(self.states[state]['voted'])):
                    voted = self.states[state]['voted'][i]
                    if voted != -1:
                        path += "\t\t\t+(-0.15," + str(val) + ") node[left] {$\prop{vote_{" + str(i + 1) + "," + str(
                            voted + 1) + "}}$}\n"
                        val -= 0.25

                for i in range(0, len(self.states[state]['voters_action'])):
                    action = self.states[state]['voters_action'][i]
                    if action != '':
                        path += "\t\t\t+(-0.15," + str(val) + ") node[left] {$\prop{" + action + "_{" + str(i + 1) + "}}$}\n"
                        val -= 0.25

                for i in range(0, len(self.states[state]['coercer_actions'])):
                    action = self.states[state]['coercer_actions'][i]
                    if action != '':
                        path += "\t\t\t+(-0.15," + str(val) + ") node[left] {$\prop{" + action + "_{" + str(i + 1) + "}}$}\n"
                        val -= 0.25

                for i in range(0, len(self.states[state]['finish'])):
                    action = self.states[state]['finish'][i]
                    if action != -1:
                        path += "\t\t\t+(-0.15," + str(val) + ") node[left] {$\prop{finish_{" + str(i + 1) + "}}$}\n"
                        val -= 0.25

                state_num += 1
                left += 2

                transitions += "\t\path[->,font=\scriptsize] (q"+str(state)+")"
                for transition in self.model.transitions[state]:
                    not_wait = 0
                    for i in range(1, self.number_of_voters + 1):
                        if transition['actions'][i] != 'wait':
                            not_wait += 1

                    if transition['actions'][0] != 'wait':
                        not_wait += 1

                    if state == 99:
                        print(transition)
                    if transition['nextState'] != state and not_wait == 1:
                        action = "("
                        # print(transition)
                        for i in range(1, self.number_of_voters + 1):
                            if transition['actions'][i] != 'wait':
                                if self.is_number(transition['actions'][i]):
                                    action += 'vote' + str(transition['actions'][i] + 1) + ','
                                else:
                                    action += 'vote' + transition['actions'][i] + ','
                            else:
                                action += "-,"

                        if transition['actions'][0] != 'wait':
                            action += transition['actions'][0] + ')'
                        else:
                            action += '-)'
                        transitions += "\n"
                        transitions += "\t\tedge\n"
                        transitions += "\t\t\tnode[midway,sloped]{\onlabel{$" + action + "$}} (q" + str(
                            transition['nextState']) + ")"

                    if visited[transition['nextState']] == 0:


                        new_states.append(transition['nextState'])
                        visited[transition['nextState']] = 1

                transitions += ";\n"
            current_level_states = new_states[:]

        path += ";\n"
        f = open("simple_voting_1_voter.txt", "w")
        f.write(path)
        f.write(transitions)
        f.close()


simple_voting_model = SimpleVotingModel(2, 2)

print('Started generating model')
start = time.clock()
simple_voting_model.generate_asynchronous_voting()
end = time.clock()
print('Generated model in', end - start, 's')

simple_voting_model.generate_tex()

simple_voting_model.print_number_of_states()
simple_voting_model.print_number_of_epistemic_classes()
# simple_voting_model.print_states()
# simple_voting_model.model.walk(0)

voter_number = 0
# print()
# print("<<c>>F(~pun_i -> vote_{i,1})")
# winning_states = []
# i = -1
# for state in simple_voting_model.states:
#     i += 1
#
#     if not (state['coercer_actions'][voter_number] != 'pun' and state['voted'][voter_number] != 1):
#         winning_states.append(i)
#
# start = time.clock()
# result = simple_voting_model.model.minimum_formula_one_agent_multiple_states(0, winning_states)
# end = time.clock()
#
# print("Time:", end - start, "s")
# print("Number of good states ", len(result))
# print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])

# print()
# print("<<v_i>>G(~pun_i & ~vote_{i,1})")
# winning_states = []
# i = -1
# for state in simple_voting_model.states:
#     i += 1
#
#     if state['coercer_actions'][voter_number] != 'pun' and state['voted'][voter_number] != 1:
#         winning_states.append(i)
#
# start = time.clock()
# result = simple_voting_model.model.maximum_formula_one_agent_multiple_states(1, winning_states)
# end = time.clock()
#
# print("Time:", end - start, "s")
# print("Number of good states ", len(result))
# print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])


# print()
# print("<<c>>G( (finish_i & ~pun_i) -> vote_{i,1} )")
# winning_states = []
# i = -1
# for state in simple_voting_model.states:
#     i += 1
#
#     if not (state['finish'][voter_number] == 1 and state['coercer_actions'][voter_number] != 'pun' and state['voted'][
#         voter_number] != 1):
#         winning_states.append(i)
#
# start = time.clock()
# result = simple_voting_model.model.maximum_formula_one_agent_multiple_states(0, winning_states)
# end = time.clock()
#
# print("Time:", end - start, "s")
# print("Number of good states ", len(result))
# print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])


print()
print("<<v_i>>F( finish_i & ~pun_i & ~vote_{i,1} )")
winning_states = []
i = -1
for state in simple_voting_model.states:
    i += 1
    if state['finish'][voter_number] == 1 and state['coercer_actions'][voter_number] != 'pun' and state['voted'][
        voter_number] != 1:
        winning_states.append(i)

start = time.clock()
result = simple_voting_model.model.minimum_formula_one_agent_multiple_states(1, winning_states)
end = time.clock()

print("Time:", end - start, "s")
print("Number of good states ", len(result))
print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])

# print()
# print("Perfect <<c>>G( (finish_i & ~pun_i) -> vote_{i,1} )")
# winning_states = []
# i = -1
# for state in simple_voting_model.states:
#     i += 1
#
#     if not (state['finish'][voter_number] == 1 and state['coercer_actions'][voter_number] != 'pun' and state['voted'][
#         voter_number] != 1):
#         winning_states.append(i)
#
# start = time.clock()
# result = simple_voting_model.model.maximum_formula_one_agent_multiple_states_perfect_information(0, winning_states)
# end = time.clock()
#
# print("Time:", end - start, "s")
# print("Number of good states ", len(result))
# print("Formula result:", list(result)[0] == 0)

# for state_number in result:
#     print(state_number, simple_voting_model.states[state_number])


print()
print("Perfect <<v_i>>F( finish_i & ~pun_i & ~vote_{i,1} )")
winning_states = []
i = -1
for state in simple_voting_model.states:
    i += 1
    if state['finish'][voter_number] == 1 and state['coercer_actions'][voter_number] != 'pun' and state['voted'][
        voter_number] != 1:
        winning_states.append(i)

start = time.clock()
result = simple_voting_model.model.minimum_formula_one_agent_multiple_states_perfect_information(1, winning_states)
end = time.clock()

print("Time:", end - start, "s")
print("Number of good states ", len(result))
print("Formula result:", list(result)[0] == 0)
