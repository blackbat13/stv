import time
from atl_model import *

__author__ = 'blackbat'




# controllerClient = ATLModel(2, 2)
# controllerClient.add_transition(0, 0, {0: 'reject', 1: 'set0'})
# controllerClient.add_transition(0, 0, {0: 'reject', 1: 'set1'})
# controllerClient.add_transition(0, 0, {0: 'accept', 1: 'set0'})
# controllerClient.add_transition(0, 1, {0: 'accept', 1: 'set1'})
# controllerClient.add_transition(1, 0, {0: 'accept', 1: 'set0'})
# controllerClient.add_transition(1, 1, {0: 'reject', 1: 'set0'})
# controllerClient.add_transition(1, 1, {0: 'reject', 1: 'set1'})
# controllerClient.add_transition(1, 1, {0: 'accept', 1: 'set1'})


# print(controllerClient.transitions)
# print(controllerClient.transitions[0][0]['actions'][0])
# print(controllerClient.basicFormula(0, 1))
# print(controllerClient.basicFormula(0, 0))
# print(controllerClient.basicFormula(1, 0))
# print(controllerClient.basicFormula(1, 1))
def life_sign(life):
    if life == 0:
        return 0
    else:
        return 1


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


def generate_castle_model(a_size, b_size, c_size, a_life, b_life, c_life):
    castle_model = ATLModel(a_size + b_size + c_size, (4 ** 3) * (2 ** a_size) * (2 ** b_size) * (2 ** c_size))
    states_product = [range(0, a_life + 1), range(0, b_life + 1), range(0, c_life + 1)]
    for i in range(0, a_size + b_size + c_size):
        states_product.append(range(0, 2))

    states = []
    states_dictionary = {}
    start = time.clock()
    for castles, i in zip(itertools.product(*states_product), range(0, 1000000)):
        states.append(castles)
        states_dictionary[''.join(str(e) for e in castles)] = i
    end = time.clock()
    print('Generate Castle Model, create states array executed in', round(end - start, 3))
    print('Number of states', len(states))

    a_actions = ['idle', 'defend', 'attack B', 'attack C']
    b_actions = ['idle', 'defend', 'attack A', 'attack C']
    c_actions = ['idle', 'defend', 'attack A', 'attack B']
    possible_actions = []
    for i in range(0, a_size):
        possible_actions.append(a_actions)
    for i in range(0, b_size):
        possible_actions.append(b_actions)
    for i in range(0, c_size):
        possible_actions.append(c_actions)

    for castles, state in zip(states, range(0, (a_life + 1) * (b_life + 1) * (c_life + 1) * (2 ** a_size) * (
        2 ** b_size) * (2 ** c_size))):
        a = castles[0]
        b = castles[1]
        c = castles[2]
        a_can_defend = list(castles[3:(a_size + 3)])
        b_can_defend = list(castles[(a_size + 3):(a_size + b_size + 3)])
        c_can_defend = list(castles[(a_size + b_size + 3):])

        description = {'A': a, 'B': b, 'C': c}
        for i in range(0, a_size):
            description['a_worker_' + str(i + 1)] = a_can_defend[i]
        for i in range(0, b_size):
            description['b_worker_' + str(i + 1)] = b_can_defend[i]
        for i in range(0, c_size):
            description['c_worker_' + str(i + 1)] = c_can_defend[i]

        castle_model.set_state_descriptions(state, description)
        castle_model.set_state_name(state, "Castle A: " + str(a) + " Castle B: " + str(b) + " Castle C: " + str(c))

        for actions in itertools.product(*possible_actions):
            next = False
            a_new_can_defend = a_can_defend[:]
            b_new_can_defend = b_can_defend[:]
            c_new_can_defend = c_can_defend[:]
            resultA = 0
            resultB = 0
            resultC = 0

            for i in range(0, a_size):
                action = actions[i]
                if a == 0 and action != 'idle':
                    next = True
                    break
                if a_can_defend[i] == 0 and action == 'defend':
                    next = True
                    break
                if action == 'attack B':
                    resultB -= 1
                    a_new_can_defend[i] = 1
                if action == 'attack C':
                    resultC -= 1
                    a_new_can_defend[i] = 1
                if action == 'defend':
                    resultA += 1
                    a_new_can_defend[i] = 0
                if action == 'idle':
                    a_new_can_defend[i] = 1

            for i in range(0, b_size):
                action = actions[a_size + i]
                if b == 0 and action != 'idle':
                    next = True
                    break
                if b_can_defend[i] == 0 and action == 'defend':
                    next = True
                    break
                if action == 'attack A':
                    resultA -= 1
                    b_new_can_defend[i] = 1
                if action == 'attack C':
                    resultC -= 1
                    b_new_can_defend[i] = 1
                if action == 'defend':
                    resultB += 1
                    b_new_can_defend[i] = 0
                if action == 'idle':
                    b_new_can_defend[i] = 1

            for i in range(0, c_size):
                action = actions[a_size + b_size + i]
                if c == 0 and action != 'idle':
                    next = True
                    break
                if c_can_defend[i] == 0 and action == 'defend':
                    next = True
                    break
                if action == 'attack A':
                    resultA -= 1
                    c_new_can_defend[i] = 1
                if action == 'attack B':
                    resultB -= 1
                    c_new_can_defend[i] = 1
                if action == 'defend':
                    resultC += 1
                    c_new_can_defend[i] = 0
                if action == 'idle':
                    c_new_can_defend[i] = 1

            if next:
                continue

            newA = a
            newB = b
            newC = c

            if resultA < 0:
                newA += resultA
            if resultB < 0:
                newB += resultB
            if resultC < 0:
                newC += resultC

            if newA >= 0 and newB >= 0 and newC >= 0:
                new_state = [newA, newB, newC]
                new_state += a_new_can_defend
                new_state += b_new_can_defend
                new_state += c_new_can_defend
                # new_state_number = find_state_index(states, new_state)
                new_state_number = states_dictionary[''.join(str(e) for e in new_state)]
                castle_model.add_transition(state, new_state_number, actions)

    start = time.clock()
    for state_a, state_a_number in zip(states, range(0, len(states))):
        for state_b_number in range(state_a_number + 1, len(states)):
            state_b = states[state_b_number]
            if not (life_sign(state_a[0]) == life_sign((state_b[0])) and life_sign(state_a[1]) == life_sign(
                    (state_b[1])) and life_sign(state_a[2]) == life_sign((state_b[2]))):
                continue

            for agent_a in range(0, a_size):
                if state_a[3 + agent_a] == state_b[3 + agent_a]:
                    castle_model.set_same_state(agent_a, state_a_number, state_b_number)

            for agent_b in range(0, b_size):
                if state_a[3 + a_size + agent_b] == state_b[3 + a_size + agent_b]:
                    castle_model.set_same_state(agent_b, state_a_number, state_b_number)

            for agent_c in range(0, c_size):
                if state_a[3 + a_size + b_size + agent_c] == state_b[3 + a_size + b_size + agent_c]:
                    castle_model.set_same_state(agent_c, state_a_number, state_b_number)

    end = time.clock()
    print('Generate Castle Model, set same states executed in', round(end - start, 3))
    return castle_model


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


a_size = 3
b_size = 1
c_size = 1
start = time.clock()
castleModel = generate_castle_model(a_size, b_size, c_size, 3, 3, 3)
end = time.clock()
print('Generated castle model in', end - start, 's')
# print(castleModel.stateDescriptions[7])
# start = time.clock()
# for i in range(0, 512):
# print(i, castleModel.basicFormulaMultipleAgents([0, 2], i))
# print(i, castleModel.basic_formula_multiple_agents([0, 1], i))
# end = time.clock()
# print('Executed in', end - start, 's')


first_array = [range(0, 4), range(0, 4), range(0, 4)]
second_array = [range(0, 4), range(0, 4), [0]]
third_array = [[0], [0], [0]]

for i in range(0, a_size+b_size+c_size):
    first_array.append(range(0, 2))
    second_array.append(range(0, 2))
    third_array.append(range(0, 2))

castle3defeated = []
all_castles_defeated = []
states = []
for castles in itertools.product(
        *first_array):
    states.append(castles)

for castles in itertools.product(*second_array):
    castle3defeated.append(find_state_index(states, castles))

for castles in itertools.product(*third_array):
    all_castles_defeated.append(find_state_index(states, castles))

print('Number of winning states', len(castle3defeated))
print("Castle 3 defeated:")
start = time.clock()
castle3defeatedResult = castleModel.minimum_formula_multiple_agents_and_states([0, 1, 2, 3],
                                                                             castle3defeated)
end = time.clock()
print('Computed in', end - start, 's')
print('Number of states:', len(castle3defeatedResult))
for state in castle3defeatedResult:
    print(state, castleModel.state_descriptions[state])

print("All castles defeated:")
start = time.clock()
all_castles_defeated_result = castleModel.minimum_formula_multiple_agents_and_states([0, 1],
                                                                             all_castles_defeated)
end = time.clock()
print('Computed in', end - start, 's')
print('Number of states:', len(all_castles_defeated_result))
for state in all_castles_defeated_result:
    print(state, castleModel.state_descriptions[state])

# print(63, castleModel.basicFormulaMultipleAgentsAndStates([0, 1], [63, 62, 61, 56]))

# drinkingManModel = ATLModel(1, 5)
# drinkingManModel.add_transition(0, 1, {0: 'stop drinking'})
# drinkingManModel.add_transition(1, 2, {0: 'go home'})
# drinkingManModel.add_transition(3, 4, {0: 'go home'})
# drinkingManModel.set_same_state(0, 1, 3)

# print(drinkingManModel.basic_formula(0, 2))
