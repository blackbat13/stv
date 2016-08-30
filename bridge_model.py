from atl_model import *
import time
import pickle
import gc
# import resource
import random

__author__ = 'blackbat'


def read_bridge_model(no_cards_available):
    bridge_model = ATLModel(3, 1294938)
    cards_available = []
    card_number = 14
    for i in range(0, no_cards_available):
        for c in range(1, 5):
            cards_available.append(card_number * 10 + (5 - c))
            bridge_model.add_action(1, card_number * 10 + (5 - c))
            bridge_model.add_action(2, card_number * 10 + (5 - c))
        card_number -= 1
    pr = []
    pr.append(cards_available[:])
    pr.append(cards_available[:])
    for cards in itertools.product(*pr):
        if cards[0] != cards[1]:
            bridge_model.add_action(0, [cards[0], cards[1]])

    print("Reading states")
    start = time.clock()
    with open('state_array_3_2.pkl', 'rb') as input:
        bridge_model.states = pickle.load(input)
    stop = time.clock()
    print("Read states in", stop - start, "s")

    # print("Reading states dictionary")
    # start = time.clock()
    # with open('state_dictionary_3_2.pkl', 'rb') as input:
    #     bridge_model.states_dictionary = pickle.load(input)
    # stop = time.clock()

    # print("Read states dictionary in", stop - start, "s")

    print("Reading transitions")
    start = time.clock()
    with open('transitions_array_3_2.pkl', 'rb') as input:
        transitions = pickle.load(input)
    stop = time.clock()
    print("Read transitions in", stop - start, "s")

    print("Adding transitions")
    start = time.clock()
    for i in range(0, len(transitions)):
        bridge_model.add_transition(transitions[i]['from_state'], transitions[i]['to_state'], transitions[i]['action'])
    stop = time.clock()
    print("Added transitions in", stop - start, "s")
    return bridge_model


def generate_bridge_model(no_cards_available, no_end_cards):
    # with open('atl_3_1294940.pkl', 'rb') as input:
    #     bridge_model = pickle.load(input)
    # 1294936 dla (3,2)
    # bridge_model = ATLModel(3, 3445920)
    bridge_model = ATLModel(4, 1000000)
    print(bridge_model.number_of_agents)
    print(bridge_model.number_of_states)
    cards_available = []
    card_number = 14
    for i in range(0, no_cards_available):
        for c in range(1, 5):
            cards_available.append(card_number * 10 + (5 - c))
            bridge_model.add_action(1, card_number * 10 + (5 - c))
            bridge_model.add_action(2, card_number * 10 + (5 - c))
        card_number -= 1
    pr = []
    pr.append(cards_available[:])
    pr.append(cards_available[:])
    for card in cards_available:
        bridge_model.add_action(0, card)
    bridge_model.add_action(0, -1)
    states = []
    states_dictionary = {}
    state_number = 0
    print("Start creating beginning states of model")
    # gc.disable()
    start = time.clock()
    for combination in itertools.combinations(cards_available, no_end_cards * 4):
        history = list(cards_available)
        for i in combination:
            history.remove(i)
        for player1 in itertools.combinations(combination, no_end_cards):
            combination2 = list(combination)
            for i in player1:
                combination2.remove(i)
            for player2 in itertools.combinations(combination2, no_end_cards):
                combination3 = combination2[:]
                for i in player2:
                    combination3.remove(i)
                for player3 in itertools.combinations(combination3, no_end_cards):
                    player4 = combination3[:]
                    for i in player3:
                        player4.remove(i)
                    hands = [list(player1), list(player2), list(player3), list(player4)]
                    state = {'hands': hands, 'lefts': [0, 0, 0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                             'beginning': 0, 'history': history}
                    print(state)
                    states.append(state)
                    state_str = ' '.join(str(state[e]) for e in state)
                    states_dictionary[state_str] = state_number
                    state_number += 1
    end = time.clock()
    # gc.enable()
    # gc.collect()
    print("Created beginning states of model in", end - start, "s")
    print("Number of beginning states of model:", len(states))

    print("Start creating rest of model")
    # gc.disable()
    # transitions = []
    trans = 0
    start = time.clock()
    current_state_number = -1
    for state in states:
        current_state_number += 1
        if state['next'] == state['beginning']:
            if len(state['hands'][state['next']]) == 0:
                break
            for card in state['hands'][state['next']]:
                new_board = state['board'][:]
                new_board[state['next']] = card
                new_next = (state['next'] + 1) % 4
                new_hands = [[], [], [], []]
                new_hands[0] = state['hands'][0][:]
                new_hands[1] = state['hands'][1][:]
                new_hands[2] = state['hands'][2][:]
                new_hands[3] = state['hands'][3][:]
                new_hands[state['next']].remove(card)
                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': state['history']}
                agent_number = state['next']
                if agent_number == 2:
                    agent_number = 0
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                action[agent_number] = card
                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                new_state_number = 0
                if new_state_str not in states_dictionary:
                    states_dictionary[new_state_str] = state_number
                    new_state_number = state_number
                    states.append(new_state)
                    state_number += 1
                else:
                    new_state_number = states_dictionary[new_state_str]
                bridge_model.add_transition(current_state_number, new_state_number, action)
        elif state['next'] == -1:
            new_history = state['history'][:]
            for i in state['board']:
                new_history.append(i)
            beginning = state['beginning']
            board = state['board']
            card1 = board[beginning]
            card2 = board[(beginning + 1) % 4]
            card3 = board[(beginning + 2) % 4]
            card4 = board[(beginning + 3) % 4]
            winner = beginning
            winning_card = card1
            color = card1 % 10
            if card2 % 10 == color and card2 > winning_card:
                winning_card = card2
                winner = (beginning + 1) % 4
            if card3 % 10 == color and card3 > winning_card:
                winning_card = card3
                winner = (beginning + 2) % 4
            if card4 % 10 == color and card4 > winning_card:
                winning_card = card4
                winner = (beginning + 3) % 4

            new_lefts = state['lefts'][:]
            new_lefts[winner] += 1
            new_next = winner
            new_beginning = winner
            action = {0: -1, 1: -1, 2: -1, 3: -1}
            new_state = {'hands': state['hands'], 'lefts': new_lefts, 'next': new_next, 'board': [-1, -1, -1, -1],
                         'beginning': new_beginning, 'history': new_history}
            new_state_str = ' '.join(str(new_state[e]) for e in new_state)
            new_state_number = 0
            if new_state_str not in states_dictionary:
                states_dictionary[new_state_str] = state_number
                new_state_number = state_number
                states.append(new_state)
                state_number += 1
            else:
                new_state_number = states_dictionary[new_state_str]
            bridge_model.add_transition(current_state_number, new_state_number, action)

        else:
            color = state['board'][state['beginning']] % 10
            have_color = False
            for card in state['hands'][state['next']]:
                if (card % 10) == color:
                    have_color = True
                    break
            for card in state['hands'][state['next']]:
                if not ((not have_color) or (card % 10) == color):
                    continue
                new_board = state['board'][:]
                new_board[state['next']] = card
                new_next = (state['next'] + 1) % 4
                new_hands = [[], [], [], []]
                new_hands[0] = state['hands'][0][:]
                new_hands[1] = state['hands'][1][:]
                new_hands[2] = state['hands'][2][:]
                new_hands[3] = state['hands'][3][:]
                new_hands[state['next']].remove(card)
                if new_next == state['beginning']:
                    new_next = -1

                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': state['history']}
                agent_number = state['next']
                if agent_number == 2:
                    agent_number = 0
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                action[agent_number] = card
                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                new_state_number = 0
                if new_state_str not in states_dictionary:
                    states_dictionary[new_state_str] = state_number
                    new_state_number = state_number
                    states.append(new_state)
                    state_number += 1
                else:
                    new_state_number = states_dictionary[new_state_str]
                bridge_model.add_transition(current_state_number, new_state_number, action)

    end = time.clock()
    # gc.enable()
    print("Created rest of model in", end - start, "s")

    print("Created model have", len(states), "states")
    # print("Created model have", trans, "transitions")

    # with open('state_array_3_2.pkl', 'wb') as output:
    #     pickle.dump(states, output, pickle.HIGHEST_PROTOCOL)
    #
    # with open('state_dictionary_3_2.pkl', 'wb') as output:
    #     pickle.dump(states_dictionary, output, pickle.HIGHEST_PROTOCOL)

    # with open('transitions_array_3_2.pkl', 'wb') as output:
    #     pickle.dump(transitions, output, pickle.HIGHEST_PROTOCOL)

    print("Begin defining indistuiginshable relation")
    gc.disable()
    start = time.clock()
    bridge_model.states = states
    # same_relation = [[] for i in itertools.repeat(None, len(states))]
    for i in range(0, len(states)):
        for j in range(i + 1, len(states)):
            state_a = states[i]
            state_b = states[j]
            if len(state_a['hands'][0]) != len(state_b['hands'][0]):
                break
            if state_a['hands'][0] == state_b['hands'][0] and state_a['hands'][2] == state_b['hands'][2] and state_a[
                'lefts'] == state_b['lefts'] and state_a['board'] == state_b['board'] and state_a['beginning'] == \
                    state_b['beginning'] and state_a['next'] == state_b['next'] and state_a['history'] == state_b[
                'history']:
                bridge_model.set_same_state(0, i, j)
                # same_relation[i].append(j)
                # same_relation[j].append(i)
    end = time.clock()
    gc.enable()
    print("Created indistuiginshable relation in", end - start, "s")
    # with open('same_array_3_2.pkl', 'wb') as output:
    #     pickle.dump(same_relation, output, pickle.HIGHEST_PROTOCOL)

    return bridge_model


number_of_beginning_states = 0


def generate_bridge_model_for_epistemic(no_cards_available, no_end_cards, first_state):
    # with open('atl_3_1294940.pkl', 'rb') as input:
    #     bridge_model = pickle.load(input)
    global number_of_beginning_states

    if no_cards_available == 1:
        bridge_model = ATLModel(3, 100)
    elif no_cards_available == 2:
        bridge_model = ATLModel(3, 1000)
    elif no_cards_available == 3:
        bridge_model = ATLModel(3, 50000)
    elif no_cards_available == 4:
        bridge_model = ATLModel(3, 1000000)
    else:
        bridge_model = ATLModel(3, 8000000)

    full_time = 0
    cards_available = []
    card_number = 14
    for i in range(0, no_cards_available):
        for c in range(1, 5):
            cards_available.append(card_number * 10 + (5 - c))
            bridge_model.add_action(1, card_number * 10 + (5 - c))
            bridge_model.add_action(2, card_number * 10 + (5 - c))
        card_number -= 1
    pr = []
    pr.append(cards_available[:])
    pr.append(cards_available[:])
    for card in cards_available:
        bridge_model.add_action(0, card)
    bridge_model.add_action(0, -1)
    states = []
    states_dictionary = {}
    alternative_states_dictionary = {}
    state_number = 0
    print("Start creating beginning epistemic class states of model")
    enemy_hands = first_state['hands'][1][:] + first_state['hands'][3][:]
    start = time.clock()
    for player2 in itertools.combinations(enemy_hands, no_end_cards):
        player4 = enemy_hands[:]
        for i in player2:
            player4.remove(i)
        new_hands = first_state['hands'][:]
        new_hands[1] = sorted(list(player2))
        new_hands[3] = sorted(list(player4))
        state = {'hands': new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                 'beginning': 0, 'history': first_state['history'], 'clock': 0, 'suit': -1}
        states.append(state)
        state_str = ' '.join(str(state[e]) for e in state)
        states_dictionary[state_str] = state_number
        alternative_states_dictionary[state_str] = {state_number}
        state_number += 1

    end = time.clock()
    full_time += end - start
    print("Created beginning states of model in", end - start, "s")
    print("Number of beginning states of model:", len(states))
    number_of_beginning_states = len(states)
    print("Start creating rest of model")
    start = time.clock()
    current_state_number = -1
    for state in states:
        current_state_number += 1
        if state['next'] == state['beginning'] and state['clock'] == 0:
            remaining_cards_count = 0
            for card in state['hands'][state['next']]:
                if card != -1:
                    remaining_cards_count += 1

            if remaining_cards_count == 0:
                break

            for card_index, card in enumerate(state['hands'][state['next']]):
                if card == -1:
                    continue

                new_board = state['board'][:]
                new_board[state['next']] = card

                new_history = state['history'][:]
                new_history.append(card)
                new_history = sorted(new_history)

                new_next = (state['next'] + 1) % 4
                new_clock = state['clock'] + 1
                new_hands = [[], [], [], []]
                for i in range(0, 4):
                    new_hands[i] = state['hands'][i][:]

                new_hands[state['next']][card_index] = -1

                alternative_new_hands = [[], [], [], []]
                alternative_new_hands[0] = new_hands[0][:]
                alternative_new_hands[1] = remove_values_from_list(new_hands[1], -1)
                alternative_new_hands[2] = new_hands[2][:]
                alternative_new_hands[3] = remove_values_from_list(new_hands[3], -1)

                # print(alternative_new_hands)

                new_suit = card % 10
                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                             'suit': new_suit}
                alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'], 'next': new_next,
                                         'board': new_board,
                                         'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                         'suit': new_suit}
                agent_number = state['next']
                if agent_number == 2:
                    agent_number = 0
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                action[agent_number] = card
                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                alternative_new_state_str = ' '.join(str(alternative_new_state[e]) for e in alternative_new_state)
                if new_state_str not in states_dictionary:
                    states_dictionary[new_state_str] = state_number
                    new_state_number = state_number
                    states.append(new_state)
                    state_number += 1
                else:
                    new_state_number = states_dictionary[new_state_str]

                if alternative_new_state_str not in alternative_states_dictionary:
                    alternative_states_dictionary[alternative_new_state_str] = {new_state_number}
                else:
                    alternative_states_dictionary[alternative_new_state_str].add(new_state_number)

                bridge_model.add_transition(current_state_number, new_state_number, action)
        elif state['clock'] == 4:
            new_history = state['history'][:]
            beginning = state['beginning']
            board = state['board']
            card1 = board[beginning]
            card2 = board[(beginning + 1) % 4]
            card3 = board[(beginning + 2) % 4]
            card4 = board[(beginning + 3) % 4]
            winner = beginning
            winning_card = card1
            color = card1 % 10
            if card2 % 10 == color and card2 > winning_card:
                winning_card = card2
                winner = (beginning + 1) % 4
            if card3 % 10 == color and card3 > winning_card:
                winning_card = card3
                winner = (beginning + 2) % 4
            if card4 % 10 == color and card4 > winning_card:
                winning_card = card4
                winner = (beginning + 3) % 4

            new_lefts = state['lefts'][:]
            new_lefts[winner % 2] += 1
            new_next = winner
            new_clock = 0
            new_beginning = winner
            new_suit = -1
            action = {0: -1, 1: -1, 2: -1, 3: -1}

            alternative_new_hands = [[], [], [], []]
            alternative_new_hands[0] = state['hands'][0][:]
            alternative_new_hands[1] = remove_values_from_list(state['hands'][1], -1)
            alternative_new_hands[2] = state['hands'][2][:]
            alternative_new_hands[3] = remove_values_from_list(state['hands'][3], -1)

            new_state = {'hands': state['hands'], 'lefts': new_lefts, 'next': new_next, 'board': [-1, -1, -1, -1],
                         'beginning': new_beginning, 'history': new_history, 'clock': new_clock, 'suit': new_suit}
            alternative_new_state = {'hands': alternative_new_hands, 'lefts': new_lefts, 'next': new_next,
                                     'board': [-1, -1, -1, -1],
                                     'beginning': new_beginning, 'history': new_history, 'clock': new_clock,
                                     'suit': new_suit}
            new_state_str = ' '.join(str(new_state[e]) for e in new_state)
            alternative_new_state_str = ' '.join(str(alternative_new_state[e]) for e in alternative_new_state)
            if new_state_str not in states_dictionary:
                states_dictionary[new_state_str] = state_number
                new_state_number = state_number
                states.append(new_state)
                state_number += 1
            else:
                new_state_number = states_dictionary[new_state_str]

            if alternative_new_state_str not in alternative_states_dictionary:
                alternative_states_dictionary[alternative_new_state_str] = {new_state_number}
            else:
                alternative_states_dictionary[alternative_new_state_str].add(new_state_number)

            bridge_model.add_transition(current_state_number, new_state_number, action)

        else:
            color = state['board'][state['beginning']] % 10
            have_color = False
            for card in state['hands'][state['next']]:
                if (card % 10) == color:
                    have_color = True
                    break
            for card_index, card in enumerate(state['hands'][state['next']]):
                if not ((not have_color) or (card % 10) == color) or card == -1:
                    continue
                new_board = state['board'][:]
                new_board[state['next']] = card

                new_history = state['history'][:]
                new_history.append(card)
                new_history = sorted(new_history)

                new_next = (state['next'] + 1) % 4
                new_hands = [[], [], [], []]
                new_hands[0] = state['hands'][0][:]
                new_hands[1] = state['hands'][1][:]
                new_hands[2] = state['hands'][2][:]
                new_hands[3] = state['hands'][3][:]
                new_hands[state['next']][card_index] = -1

                alternative_new_hands = [[], [], [], []]
                alternative_new_hands[0] = new_hands[0][:]
                alternative_new_hands[1] = remove_values_from_list(new_hands[1], -1)
                alternative_new_hands[2] = new_hands[2][:]
                alternative_new_hands[3] = remove_values_from_list(new_hands[3], -1)

                new_clock = state['clock'] + 1
                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                             'suit': state['suit']}
                alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'], 'next': new_next,
                                         'board': new_board,
                                         'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                         'suit': state['suit']}

                agent_number = state['next']
                if agent_number == 2:
                    agent_number = 0
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                action[agent_number] = card
                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                alternative_new_state_str = ' '.join(str(alternative_new_state[e]) for e in alternative_new_state)
                if new_state_str not in states_dictionary:
                    states_dictionary[new_state_str] = state_number
                    new_state_number = state_number
                    states.append(new_state)
                    state_number += 1
                else:
                    new_state_number = states_dictionary[new_state_str]

                if alternative_new_state_str not in alternative_states_dictionary:
                    alternative_states_dictionary[alternative_new_state_str] = {new_state_number}
                else:
                    alternative_states_dictionary[alternative_new_state_str].add(new_state_number)

                bridge_model.add_transition(current_state_number, new_state_number, action)

    end = time.clock()
    full_time += end - start
    print("Created rest of model in", end - start, "s")
    print("Created model have", len(states), "states")
    print("Begin defining indistuiginshable relation")
    gc.disable()
    start = time.clock()
    bridge_model.states = states
    prepare_epistemic_relation(bridge_model, states_dictionary, alternative_states_dictionary)
    end = time.clock()
    gc.enable()
    full_time += end - start
    print("Created indistuiginshable relation in", end - start, "s")
    print("Created whole model in", full_time, "s")
    return bridge_model


def prepare_epistemic_relation(bridge_model, states_dictionary, alternative_states_dictionary):
    states = bridge_model.states
    visited_states = [0 for _ in itertools.repeat(None, len(states))]
    for i in range(0, len(states)):
        if visited_states[i] == 1:
            continue

        epistemic_class = list(
                prepare_epistemic_class_for_state(states[i], states_dictionary, alternative_states_dictionary))
        bridge_model.add_epistemic_class(0, epistemic_class)
        for state in epistemic_class:
            visited_states[state] = 1


def prepare_epistemic_class_for_state(state, states_dictionary, alternative_states_dictionary):
    state_str = ' '.join(str(state[e]) for e in state)
    epistemic_class = {states_dictionary[state_str]}
    hands_length = len(state['hands'][1])
    no_cards_player_2 = hands_length - state['hands'][1].count(-1)
    if no_cards_player_2 == 0:
        return epistemic_class
    cards = []
    for card in state['hands'][1]:
        if card != -1:
            cards.append(card)

    for card in state['hands'][3]:
        if card != -1:
            cards.append(card)

    cards.sort()
    for player_2_cards in itertools.combinations(cards, no_cards_player_2):
        player_4_cards = cards[:]
        for card in player_2_cards:
            player_4_cards.remove(card)

        new_hands = [state['hands'][0], list(player_2_cards), state['hands'][2],
                     list(player_4_cards)]
        new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': state['next'],
                     'board': state['board'],
                     'beginning': state['beginning'], 'history': state['history'], 'clock': state['clock'],
                     'suit': state['suit']}
        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
        if new_state_str in alternative_states_dictionary:
            epistemic_class.update(alternative_states_dictionary[new_state_str])

    return epistemic_class


def write_empty_atl_model(size):
    print("Start creating empty ATL model")
    start = time.clock()
    empty_atl = ATLModel(3, size)
    end = time.clock()
    print("Created empty ATL model in", end - start, "s")
    print("Start writing empty ATL model to file")
    start = time.clock()
    with open('atl_3_' + size + '.pkl', 'wb') as output:
        pickle.dump(empty_atl, output, pickle.HIGHEST_PROTOCOL)
    end = time.clock()
    print("Writed empty ATL model to file in", end - start, "s")


def write_bridge_model(a, b):
    print("Start generating bridge model with", a, "cards and", b, "lefts")
    start = time.clock()
    bridge_model = generate_bridge_model(a, b)
    end = time.clock()
    print("Created bridge model in", end - start, "s")

    with open('bridge_' + a + '_' + b + '.pkl', 'wb') as output:
        pickle.dump(bridge_model, output, pickle.HIGHEST_PROTOCOL)
    print("Number of states", len(bridge_model.states))


def generate_random_hands(length):
    array = []
    used = []
    card_numbers = [144, 143, 142, 141, 134, 133, 132, 131, 124, 123, 122, 121, 114, 113, 112, 111, 104, 103, 102, 101,
                    94, 93, 92, 91]
    for i in range(0, length):
        used.append(False)

    for i in range(0, length):
        number = random.randrange(length)
        while used[number]:
            number = random.randrange(length)

        array.append(card_numbers[number])
        used[number] = True

    hands = []
    j = 0
    for i in range(0, 4):
        hand = []
        for _ in range(0, int(length / 4)):
            hand.append(array[j])
            j += 1

        hands.append(sorted(hand))

    return hands


def generate_readable_cards_array():
    card_names = ["Ace", "King", "Queen", "Jack", "ten", "nine", "eight", "seven", "six", "five", "four", "three",
                  "two"]
    card_colors = ["Spade", "Heart", "Diamond", "Club"]
    cards = []
    for name in card_names:
        for color in card_colors:
            cards.append(name + color)

    return cards


def generate_cards_dictionary():
    cards = generate_readable_cards_array()
    card_name_number = 14
    cards_dictionary = {}
    i = 0
    while card_name_number > 1:
        card_color_number = 4
        while card_color_number > 0:
            cards_dictionary[card_name_number * 10 + card_color_number] = cards[i]
            i += 1
            card_color_number -= 1
        card_name_number -= 1

    return cards_dictionary


def hands_to_readable_hands(hands):
    cards_dictionary = generate_cards_dictionary()
    readable_hands = []
    for hand in hands:
        readable_hand = []
        for card_number in hand:
            readable_hand.append(cards_dictionary[card_number])
        readable_hands.append(readable_hand)

    return readable_hands


def test_bridge_model(n):
    hands = generate_random_hands(n * 4)
    print('Hands:', hands)
    print('Readable hands:', hands_to_readable_hands(hands))
    # hands = [[121, 133, 141, 143], [114, 122, 134, 142], [111, 112, 123, 132], [113, 124, 131, 144]]
    bridge_model = generate_bridge_model_for_epistemic(n, n, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                                              'hands': hands, 'next': 0, 'history': [],
                                                              'beginning': 0, 'clock': 0, 'suit': -1})

    # print("Maximal memory usage ", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # bridge_model.walk()

    winning_states = []
    i = -1
    for state in bridge_model.states:
        i += 1
        if state['lefts'][0] > n / 2:
            winning_states.append(i)

    print("Start formula verification under imperfect information")
    start = time.clock()
    wynik = bridge_model.minimum_formula_one_agent_multiple_states(0, winning_states)
    end = time.clock()
    print("Time:", end - start, "s")
    print("Number of good states ", len(wynik))
    number_of_correct_beginning_states = 0
    for state_nr in wynik:
        if len(bridge_model.states[state_nr]['history']) == 0 and bridge_model.states[state_nr]['board'] == [-1, -1, -1,
                                                                                                             -1]:
            number_of_correct_beginning_states += 1

    print("Formula result:", number_of_beginning_states == number_of_correct_beginning_states)

    print("Start formula verification under perfect information")
    start = time.clock()
    wynik = bridge_model.minimum_formula_one_agent_multiple_states_perfect_information(0, winning_states)
    end = time.clock()
    print("Time:", end - start, "s")
    print("Number of good states ", len(wynik))
    number_of_correct_beginning_states = 0
    for state_nr in wynik:
        if len(bridge_model.states[state_nr]['history']) == 0 and bridge_model.states[state_nr]['board'] == [-1, -1, -1,
                                                                                                             -1]:
            number_of_correct_beginning_states += 1

    print("Formula result:", number_of_beginning_states == number_of_correct_beginning_states)


def remove_values_from_list(the_list, val):
    return [value for value in the_list if value != val]


n = int(input("n="))
number_of_tests = int(input("Number of tests="))

for _ in range(0, number_of_tests):
    test_bridge_model(n)
    print()

# Pik Kier Karo Trefl
# Spade Heart Diamond Club
