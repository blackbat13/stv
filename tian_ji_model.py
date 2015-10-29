from atl_model import *
import time

__author__ = 'blackbat'


def generate_all_subsets(number_of_horses):
    product_list = [range(0, 2)] * number_of_horses
    all_subsets = []
    for combination in itertools.product(*product_list):
        subset = []
        for decision, horse in zip(combination, range(0, number_of_horses)):
            if decision == 1:
                subset.append(horse)
        all_subsets.append(subset)

    return all_subsets


states_dictionary = {}
states = []
visited_states = []


def create_array_of_size2(size, basic_item):
    array = []
    for i in range(0, size):
        array.append(basic_item)
    return array[:]


def generate_tian_ji_model2(number_of_horses):
    global states
    global states_dictionary
    global visited_states
    tian_ji_model = ATLModel(2, number_of_horses ** 6)
    states = [{'king_score': 0, 'tian_ji_score': 0, 'king_horses': list(range(0, number_of_horses)),
               'tian_ji_horses': list(range(0, number_of_horses)),
               'results': create_array_of_size2(number_of_horses, 0)}]
    states_dictionary = {' '.join(str(states[0][e]) for e in states[0]): 0}
    tian_ji_model.set_state_name(0, ' '.join(str(states[0][e]) for e in states[0]))
    states_to_process = []
    state_number = 1
    states_to_process.append(states[0])
    while len(states_to_process) != 0:
        state = states_to_process.pop(0)
        state_string = ' '.join(str(state[e]) for e in state)
        current_state_number = states_dictionary[state_string]

        king_horses = state['king_horses']
        tian_ji_horses = state['tian_ji_horses']
        for i in range(0, len(king_horses)):
            for j in range(0, len(tian_ji_horses)):
                king_horse = king_horses[i]
                tian_ji_horse = tian_ji_horses[j]
                new_king_horses = king_horses[:]
                new_tian_ji_horses = tian_ji_horses[:]
                new_king_horses.pop(i)
                new_tian_ji_horses.pop(j)
                king_new_score = state['king_score']
                tian_ji_new_score = state['tian_ji_score']
                new_results = state['results'][:]
                if king_horse >= tian_ji_horse:
                    king_new_score += 1
                    new_results[tian_ji_horse] = -1
                else:
                    tian_ji_new_score += 1
                    new_results[tian_ji_horse] = 1

                new_state = {'king_score': king_new_score, 'tian_ji_score': tian_ji_new_score,
                             'king_horses': new_king_horses, 'tian_ji_horses': new_tian_ji_horses,
                             'results': new_results}

                new_state_string = ' '.join(str(new_state[e]) for e in new_state)

                new_state_number = -1
                if new_state_string in states_dictionary:
                    new_state_number = states_dictionary[new_state_string]
                else:
                    new_state_number = state_number
                    state_number += 1
                    states_dictionary[new_state_string] = new_state_number
                    states_to_process.append(new_state)
                    states.append(new_state)
                    tian_ji_model.set_state_name(new_state_number, new_state_string)

                tian_ji_model.add_transition(current_state_number, new_state_number, {0: king_horse, 1: tian_ji_horse})

    for i in range(0, len(states)):
        state_a_number = states_dictionary[' '.join(str(states[i][e]) for e in states[i])]
        for j in range(i + 1, len(states)):
            state_b_number = states_dictionary[' '.join(str(states[j][e]) for e in states[j])]
            state_a = states[i]
            state_b = states[j]
            if state_a['king_score'] == state_b['king_score'] and state_a['tian_ji_score'] == state_b[
                'tian_ji_score'] and state_a['tian_ji_horses'] == state_b['tian_ji_horses'] and state_a['results'] == \
                    state_b['results']:
                tian_ji_model.set_same_state(1, state_a_number, state_b_number)

    return tian_ji_model


def generate_tian_ji_model(number_of_horses):
    global states
    global states_dictionary
    global visited_states
    horse_subsets = generate_all_subsets(number_of_horses)
    states = []  # [[0, 0, list(range(0, number_of_horses)), list(range(0, number_of_horses))]]
    states_dictionary = {}  # {' '.join(str(e) for e in states[0]): 0}
    state_number = 0
    for state in itertools.product(
            *[range(0, number_of_horses + 1), range(0, number_of_horses + 1), horse_subsets,
              horse_subsets, range(-1, number_of_horses)]):
        # print('before', state)
        if state[0] + state[1] <= number_of_horses and len(state[2]) == len(state[3]) and len(
                state[2]) == number_of_horses - (state[0] + state[1]) and (
                        state[4] in state[2] or state[4] == -1):
            states.append(list(state))
            states_dictionary[' '.join(str(e) for e in state)] = state_number
            state_number += 1
            visited_states.append(False)
            # print(state)
            # print(state)

    tian_ji_model = ATLModel(2, len(states))
    remaining_states = []
    # for state, i in zip(states, range(0, number_of_horses)):
    #     remaining_states.append(state)

    remaining_states.append(states[0])

    while len(remaining_states) != 0:
        state = remaining_states.pop(0)
        state_number = states_dictionary[' '.join(str(e) for e in state)]
        if visited_states[state_number]:
            continue

        tian_ji_model.set_state_name(state_number, ' '.join(str(e) for e in state))
        # tian_ji_model.add_transition(state_number, state_number, {0: '', 1: ''})
        visited_states[state_number] = True
        king_horse = state[4]
        if king_horse == -1:
            for king_horse in state[2]:
                new_state = state[:]
                new_state[4] = king_horse
                new_state_number = states_dictionary[' '.join(str(e) for e in new_state)]
                tian_ji_model.add_transition(state_number, new_state_number, {0: king_horse, 1: ''})
                if not visited_states[new_state_number]:
                    remaining_states.append(new_state[:])
        else:
            for tian_horse in state[3]:
                new_state = state[:]
                if king_horse >= tian_horse:
                    new_state[0] += 1
                else:
                    new_state[1] += 1
                new_state[2] = state[2][:]
                new_state[3] = state[3][:]
                new_state[2].remove(king_horse)
                new_state[3].remove(tian_horse)
                new_state[4] = -1
                new_state_number = states_dictionary[' '.join(str(e) for e in new_state)]
                tian_ji_model.add_transition(state_number, new_state_number, {0: '', 1: tian_horse})
                if not visited_states[new_state_number]:
                    remaining_states.append(new_state[:])

                    # for tian_horse in state[3]:
                    #     new_state = state[:]
                    #     if king_horse >= tian_horse:
                    #         new_state[0] += 1
                    #     else:
                    #         new_state[1] += 1
                    #     new_state[2] = state[2][:]
                    #     new_state[3] = state[3][:]
                    #     new_state[2].remove(king_horse)
                    #     new_state[3].remove(tian_horse)
                    #     for new_king_horse in new_state[2]:
                    #         new_state[4] = new_king_horse
                    #         new_state_number = states_dictionary[' '.join(str(e) for e in new_state)]
                    #         tian_ji_model.add_transition(state_number, new_state_number, {0: king_horse, 1: tian_horse})
                    #         if not visited_states[new_state_number]:
                    #             remaining_states.append(new_state[:])
                    #     if len(new_state[2]) == 0:
                    #         new_state[4] = -1
                    #         new_state_number = states_dictionary[' '.join(str(e) for e in new_state)]
                    #         tian_ji_model.add_transition(state_number, new_state_number, {0: king_horse, 1: tian_horse})
                    #         if not visited_states[new_state_number]:
                    #             remaining_states.append(new_state[:])

    # for state, state_number in zip(states, range(0, len(states))):
    #     tian_ji_model.set_state_descriptions(state_number, ' '.join(str(e) for e in state))
    #     king_horse = state[4]
    #     for tian_horse in state[3]:
    #         new_state = state[:]
    #         if king_horse >= tian_horse:
    #             new_state[0] += 1
    #         else:
    #             new_state[1] += 1
    #         new_state[2] = state[2][:]
    #         new_state[3] = state[3][:]
    #         new_state[2].remove(king_horse)
    #         new_state[3].remove(tian_horse)
    #         for new_king_horse in new_state[2]:
    #             new_state[4] = new_king_horse
    #             new_state_number = states_dictionary[' '.join(str(e) for e in new_state)]
    #             tian_ji_model.add_transition(state_number, new_state_number, {0: king_horse, 1: tian_horse})
    #         if len(new_state[2]) == 0:
    #             new_state[4] = -1
    #             new_state_number = states_dictionary[' '.join(str(e) for e in new_state)]
    #             tian_ji_model.add_transition(state_number, new_state_number, {0: king_horse, 1: tian_horse})

    visited_states_numbers = []
    for state_number in range(0, len(states)):
        if visited_states[state_number]:
            visited_states_numbers.append(state_number)
    for i in range(0, len(visited_states_numbers)):
        state_a_number = visited_states_numbers[i]
        for j in range(i + 1, len(visited_states_numbers)):
            state_b_number = visited_states_numbers[j]
            state_a = states[state_a_number]
            state_b = states[state_b_number]
            if state_a[0] == state_b[0] and state_a[1] == state_b[1] and state_a[3] == state_b[3] and state_a[4] == \
                    state_b[4]:
                tian_ji_model.set_same_state(1, state_a_number, state_b_number)

    return tian_ji_model


number_of_horses = 2

start = time.clock()
tian_ji_model = generate_tian_ji_model2(number_of_horses)
end = time.clock()

print('Generate Tian Ji model in', end - start, 's')
print('Number of states', len(states))

tian_ji_wins_states = []
for state in states:
    if state['tian_ji_score'] >= state['king_score'] and len(state['king_horses']) == 0 and len(
            state['tian_ji_horses']) == 0:
        tian_ji_wins_states.append(states_dictionary[' '.join(str(state[e]) for e in state)])

        # for tian_ji_score in range(int(number_of_horses / 2 + 1), number_of_horses + 1):
        # king_score = number_of_horses - tian_ji_score
        # state = {'king_score': king_score, 'tian_ji_score': tian_ji_score, 'king_horses': [], 'tian_ji_horses': [], -1]
        # state_number = states_dictionary[' '.join(str(state[e]) for e in state)]
        # if visited_states[state_number]:
        # tian_ji_wins_states.append(state_number)
start = time.clock()
result_states = tian_ji_model.minimum_formula_multiple_agents_and_states([1], tian_ji_wins_states)
end = time.clock()

print('Tian Ji wins compute time', end - start, 's')
print('Number of states', len(result_states))

for i in result_states:
    print(states[i])
# if states[i][0] == 0 and states[i][1] == 0:
#    print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')

tian_ji_won_less_2 = []
for state in states:
    # if not visited_states[state_number]:
    #    continue
    if state['tian_ji_score'] < 2:
        tian_ji_won_less_2.append(states_dictionary[' '.join(str(state[e]) for e in state)])
# for tian_ji_score in range(0, 2):
#     king_score = number_of_horses - tian_ji_score
#     state = [king_score, tian_ji_score, [], [], -1]
#     state_number = states_dictionary[' '.join(str(e) for e in state)]
#     tian_ji_won_less_2.append(state_number)

start = time.clock()
first_result_states = tian_ji_model.basic_formula_multiple_agents_and_states([1], tian_ji_won_less_2)
second_result_states = tian_ji_model.maximum_formula_multiple_agents_and_states([1], first_result_states)
end = time.clock()

print('Tian Ji second formulae compute time', end - start, 's')
print('Number of states', len(second_result_states))
print('Number of states in inner formula', len(first_result_states))

for i in second_result_states:
    print(states[i])
