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

    if no_end_cards == 1:
        bridge_model = ATLModel(3, 100)
    elif no_end_cards == 2:
        bridge_model = ATLModel(3, 1000)
    elif no_end_cards == 3:
        bridge_model = ATLModel(3, 100000)
    elif no_end_cards == 4:
        bridge_model = ATLModel(3, 1000000)
    else:
        bridge_model = ATLModel(3, 8000000)

    full_time = 0
    cards_available = []
    card_number = 14
    for i in range(0, no_cards_available):
        for c in range(1, 5):
            cards_available.append(card_number * 10 + (5 - c))
            bridge_model.add_action(0, card_number * 10 + (5 - c))
            # bridge_model.add_action(2, card_number * 10 + (5 - c))
        card_number -= 1
    pr = []
    pr.append(cards_available[:])
    # pr.append(cards_available[:])
    # for card in cards_available:
    #     bridge_model.add_action(0, card)
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


def generate_blind_bridge_model_for_epistemic(no_cards_available, no_end_cards, first_state):
    # with open('atl_3_1294940.pkl', 'rb') as input:
    #     bridge_model = pickle.load(input)
    global number_of_beginning_states

    if no_cards_available == 1:
        bridge_model = ATLModel(3, 100)
    elif no_cards_available == 2:
        bridge_model = ATLModel(3, 1000)
    elif no_cards_available == 3:
        bridge_model = ATLModel(3, 500000)
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

        alternative_new_hands = [[], [], [], []]
        alternative_new_hands[0] = new_hands[0][:]
        alternative_new_hands[2] = new_hands[2][:]

        state = {'hands': new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                 'beginning': 0, 'history': first_state['history'], 'clock': 0, 'suit': -1,
                 'current_s_hand': new_hands[2], 'current_history': first_state['history']}
        alternative_state = {'hands': alternative_new_hands, 'lefts': [0, 0], 'board': -1,
                             'beginning': 0, 'history': first_state['history']}
        states.append(state)
        state_str = ' '.join(str(state[e]) for e in state)
        alternative_state_str = ' '.join(str(alternative_state[e]) for e in alternative_state)
        states_dictionary[state_str] = state_number
        if alternative_state_str in alternative_states_dictionary:
            alternative_states_dictionary[alternative_state_str].add(state_number)
        else:
            alternative_states_dictionary[alternative_state_str] = {state_number}

        state_number += 1

    end = time.clock()
    full_time += end - start
    print("Created beginning states of model in", end - start, "s")
    print("Number of beginning states of model:", len(states))
    number_of_beginning_states = len(states)
    print("Start creating rest of model")
    start = time.clock()
    for state in states:
        state_str = ' '.join(str(state[e]) for e in state)
        current_state_number = states_dictionary[state_str]

        if state['next'] == state['beginning'] and state['clock'] == 0:
            remaining_cards_count = 0
            for card in state['hands'][state['next']]:
                if card != -1:
                    remaining_cards_count += 1

            # if remaining_cards_count == 0:
            #     break

            if state['next'] == 0:
                # Player 0 should play, but wait
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                bridge_model.add_transition(current_state_number, current_state_number, action)

                # Player 0 play his card
                for card_index, card in enumerate(state['hands'][state['next']]):
                    if card == -1:
                        continue

                    new_board = state['board'][:]
                    new_board[state['next']] = card

                    new_history = state['history'][:]
                    new_history.append(card)
                    new_history = sorted(new_history)

                    alternative_history = state['current_history'][:]
                    alternative_history.append(card)
                    alternative_history = sorted(alternative_history)

                    new_next = (state['next'] + 1) % 4
                    new_clock = state['clock'] + 1
                    new_hands = [[], [], [], []]
                    for i in range(0, 4):
                        new_hands[i] = state['hands'][i][:]

                    new_hands[state['next']][card_index] = -1

                    alternative_new_hands = [[], [], [], []]
                    alternative_new_hands[0] = new_hands[0][:]
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_suit = card % 10
                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': new_suit, 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': alternative_history}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': alternative_history}

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

                if state['board'][2] == -1:
                    # Player 0 play card from table
                    for card_index, card in enumerate(state['hands'][2]):
                        if card == -1:
                            continue

                        new_board = state['board'][:]
                        new_board[2] = card

                        new_history = state['history'][:]
                        new_history.append(card)
                        new_history = sorted(new_history)

                        new_next = state['next']
                        new_clock = state['clock']
                        new_hands = [[], [], [], []]
                        for i in range(0, 4):
                            new_hands[i] = state['hands'][i][:]

                        new_hands[2][card_index] = -1

                        alternative_new_hands = [[], [], [], []]
                        alternative_new_hands[0] = new_hands[0][:]
                        alternative_new_hands[1] = []
                        alternative_new_hands[2] = state['current_s_hand'][:]
                        alternative_new_hands[3] = []

                        new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                     'board': new_board,
                                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                     'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                     'current_history': state['current_history'][:]}
                        alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                 'board': new_board[0],
                                                 'beginning': state['beginning'],
                                                 'history': state['current_history'][:]}
                        agent_number = 2
                        if agent_number == 2:
                            agent_number = 0
                        action = {0: -1, 1: -1, 2: -1, 3: -1}
                        action[agent_number] = card
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        alternative_new_state_str = ' '.join(
                            str(alternative_new_state[e]) for e in alternative_new_state)
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
                    # Player 0 try to play card from table
                    for card_index, card in enumerate(state['current_s_hand']):
                        if card == -1:
                            continue

                        action = {0: card, 1: -1, 2: -1, 3: -1}
                        bridge_model.add_transition(current_state_number, current_state_number, action)
            elif state['next'] == 2:
                # Player 0 waits
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                bridge_model.add_transition(current_state_number, current_state_number, action)
                # Player 0 play card from table
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
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_suit = card % 10
                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': new_suit, 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': state['current_history'][:]}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': state['current_history'][:]}
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

                # Player 0 should play from table, but play his card instead
                if state['board'][0] == -1:
                    for card_index, card in enumerate(state['hands'][0]):
                        if card == -1:
                            continue

                        new_board = state['board'][:]
                        new_board[0] = card

                        new_history = state['history'][:]
                        new_history.append(card)
                        new_history = sorted(new_history)

                        alternative_history = state['current_history'][:]
                        alternative_history.append(card)
                        alternative_history = sorted(alternative_history)

                        new_next = state['next']
                        new_clock = state['clock']
                        new_hands = [[], [], [], []]
                        for i in range(0, 4):
                            new_hands[i] = state['hands'][i][:]

                        new_hands[0][card_index] = -1

                        alternative_new_hands = [[], [], [], []]
                        alternative_new_hands[0] = new_hands[0][:]
                        alternative_new_hands[1] = []
                        alternative_new_hands[2] = state['current_s_hand'][:]
                        alternative_new_hands[3] = []

                        new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                     'board': new_board,
                                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                     'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                     'current_history': alternative_history}
                        alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                 'board': new_board[0],
                                                 'beginning': state['beginning'], 'history': alternative_history}
                        agent_number = 0
                        action = {0: -1, 1: -1, 2: -1, 3: -1}
                        action[agent_number] = card
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        alternative_new_state_str = ' '.join(
                            str(alternative_new_state[e]) for e in alternative_new_state)
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
                # Player 0 wait
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
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_suit = card % 10
                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': new_suit, 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': state['current_history'][:]}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': state['current_history'][:]}
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
                # Player 0 play his card
                for card_index, card in enumerate(state['hands'][state['next']]):
                    for card_index2, card2 in enumerate(state['hands'][0]):
                        if card == -1 or card2 == -1:
                            continue

                        new_board = state['board'][:]
                        new_board[state['next']] = card
                        new_board[0] = card2

                        new_history = state['history'][:]
                        new_history.append(card)
                        new_history.append(card2)
                        new_history = sorted(new_history)

                        alternative_history = state['current_history'][:]
                        alternative_history.append(card2)
                        alternative_history = sorted(alternative_history)

                        if state['next'] == 3:
                            new_next = (state['next'] + 2) % 4
                            new_clock = state['clock'] + 2
                        else:
                            new_next = (state['next'] + 1) % 4
                            new_clock = state['clock'] + 1
                        new_hands = [[], [], [], []]
                        for i in range(0, 4):
                            new_hands[i] = state['hands'][i][:]

                        new_hands[state['next']][card_index] = -1
                        new_hands[0][card_index2] = -1

                        alternative_new_hands = [[], [], [], []]
                        alternative_new_hands[0] = new_hands[0][:]
                        alternative_new_hands[1] = []
                        alternative_new_hands[2] = state['current_s_hand'][:]
                        alternative_new_hands[3] = []

                        new_suit = card % 10
                        new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                     'board': new_board,
                                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                     'suit': new_suit, 'current_s_hand': state['current_s_hand'][:],
                                     'current_history': alternative_history}
                        alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                 'board': new_board[0],
                                                 'beginning': state['beginning'], 'history': alternative_history}
                        agent_number = state['next']
                        if agent_number == 2:
                            agent_number = 0
                        action = {0: card2, 1: -1, 2: -1, 3: -1}
                        action[agent_number] = card
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        alternative_new_state_str = ' '.join(
                            str(alternative_new_state[e]) for e in alternative_new_state)
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
                # Player 0 play card from table
                for card_index, card in enumerate(state['hands'][state['next']]):
                    for card_index2, card2 in enumerate(state['hands'][2]):
                        if card == -1 or card2 == -1:
                            continue

                        new_board = state['board'][:]
                        new_board[state['next']] = card

                        new_history = state['history'][:]
                        new_history.append(card)

                        if state['board'][2] == -1:
                            new_board[2] = card2
                            new_history.append(card2)

                        new_history = sorted(new_history)

                        if state['next'] == 1:
                            new_next = (state['next'] + 2) % 4
                            new_clock = state['clock'] + 2
                        else:
                            new_next = (state['next'] + 1) % 4
                            new_clock = state['clock'] + 1
                        new_hands = [[], [], [], []]
                        for i in range(0, 4):
                            new_hands[i] = state['hands'][i][:]

                        new_hands[state['next']][card_index] = -1
                        new_hands[0][card_index2] = -1

                        alternative_new_hands = [[], [], [], []]
                        alternative_new_hands[0] = new_hands[0][:]
                        alternative_new_hands[1] = []
                        alternative_new_hands[2] = state['current_s_hand'][:]
                        alternative_new_hands[3] = []

                        new_suit = card % 10
                        new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                     'board': new_board,
                                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                     'suit': new_suit, 'current_s_hand': state['current_s_hand'][:],
                                     'current_history': state['current_history'][:]}
                        alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                 'board': new_board[0],
                                                 'beginning': state['beginning'],
                                                 'history': state['current_history'][:]}
                        agent_number = state['next']
                        if agent_number == 2:
                            agent_number = 0
                        action = {0: card2, 1: -1, 2: -1, 3: -1}
                        action[agent_number] = card
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        alternative_new_state_str = ' '.join(
                            str(alternative_new_state[e]) for e in alternative_new_state)
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
        elif state['clock'] >= 4:
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
            alternative_new_hands[1] = []
            alternative_new_hands[2] = state['hands'][2][:]
            alternative_new_hands[3] = []

            new_state = {'hands': state['hands'][:], 'lefts': new_lefts, 'next': new_next, 'board': [-1, -1, -1, -1],
                         'beginning': new_beginning, 'history': new_history, 'clock': new_clock, 'suit': new_suit,
                         'current_s_hand': state['hands'][2][:], 'current_history': new_history}
            alternative_new_state = {'hands': alternative_new_hands, 'lefts': new_lefts,
                                     'board': -1,
                                     'beginning': new_beginning, 'history': new_history}

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

            for card in state['current_s_hand']:
                if card == -1:
                    continue
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
                action = {0: card, 1: -1, 2: -1, 3: -1}

                alternative_new_hands = [[], [], [], []]
                alternative_new_hands[0] = state['hands'][0][:]
                alternative_new_hands[1] = []
                alternative_new_hands[2] = state['hands'][2][:]
                alternative_new_hands[3] = []

                new_state = {'hands': state['hands'][:], 'lefts': new_lefts, 'next': new_next,
                             'board': [-1, -1, -1, -1],
                             'beginning': new_beginning, 'history': new_history, 'clock': new_clock, 'suit': new_suit,
                             'current_s_hand': state['hands'][2][:], 'current_history': new_history}
                alternative_new_state = {'hands': alternative_new_hands, 'lefts': new_lefts,
                                         'board': -1,
                                         'beginning': new_beginning, 'history': new_history}

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

            if state['next'] == 0:
                # Player 0 should play, but wait
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                bridge_model.add_transition(current_state_number, current_state_number, action)

                # Player 0 play his card
                for card_index, card in enumerate(state['hands'][state['next']]):
                    if card == -1:
                        continue

                    new_board = state['board'][:]
                    new_board[state['next']] = card

                    new_history = state['history'][:]
                    new_history.append(card)
                    new_history = sorted(new_history)

                    alternative_history = state['current_history'][:]
                    alternative_history.append(card)
                    alternative_history = sorted(alternative_history)

                    new_next = (state['next'] + 1) % 4
                    new_hands = [[], [], [], []]
                    new_hands[0] = state['hands'][0][:]
                    new_hands[1] = state['hands'][1][:]
                    new_hands[2] = state['hands'][2][:]
                    new_hands[3] = state['hands'][3][:]
                    new_hands[state['next']][card_index] = -1

                    alternative_new_hands = [[], [], [], []]
                    alternative_new_hands[0] = new_hands[0][:]
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_clock = state['clock'] + 1
                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': alternative_history}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': alternative_history}
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
                # Player 0 play card from table
                for card_index, card in enumerate(state['current_s_hand']):
                    if card == -1:
                        continue

                    new_board = state['board'][:]
                    new_history = state['history'][:]

                    new_next = 0
                    new_hands = [[], [], [], []]
                    new_hands[0] = state['hands'][0][:]
                    new_hands[1] = state['hands'][1][:]
                    new_hands[2] = state['hands'][2][:]
                    new_hands[3] = state['hands'][3][:]

                    if state['board'][2] == -1:
                        new_board[2] = card
                        new_history.append(card)
                        new_history = sorted(new_history)
                        new_hands[2][card_index] = -1

                    alternative_new_hands = [[], [], [], []]
                    alternative_new_hands[0] = new_hands[0][:]
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_clock = state['clock']
                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': state['current_history'][:]}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': state['current_history'][:]}
                    action = {0: card, 1: -1, 2: -1, 3: -1}
                    new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                    alternative_new_state_str = ' '.join(
                        str(alternative_new_state[e]) for e in alternative_new_state)
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
            elif state['next'] == 2:
                # Player 0 should play, but wait
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                bridge_model.add_transition(current_state_number, current_state_number, action)

                # Player 0 play card from table
                for card_index, card in enumerate(state['current_s_hand']):
                    if card == -1:
                        continue

                    new_board = state['board'][:]
                    new_history = state['history'][:]

                    new_next = (state['next'] + 1) % 4
                    new_hands = [[], [], [], []]
                    new_hands[0] = state['hands'][0][:]
                    new_hands[1] = state['hands'][1][:]
                    new_hands[2] = state['hands'][2][:]
                    new_hands[3] = state['hands'][3][:]

                    new_board[2] = card
                    new_history.append(card)
                    new_history = sorted(new_history)
                    new_hands[2][card_index] = -1

                    alternative_new_hands = [[], [], [], []]
                    alternative_new_hands[0] = new_hands[0][:]
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_clock = state['clock']
                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': state['current_history'][:]}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': state['current_history'][:]}
                    action = {0: card, 1: -1, 2: -1, 3: -1}
                    new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                    alternative_new_state_str = ' '.join(
                        str(alternative_new_state[e]) for e in alternative_new_state)
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

                # Player 0 play his card
                if state['board'][0] == -1:
                    for card_index, card in enumerate(state['hands'][0]):
                        if card == -1:
                            continue
                        new_board = state['board'][:]
                        new_history = state['history'][:]

                        new_next = 2
                        new_hands = [[], [], [], []]
                        new_hands[0] = state['hands'][0][:]
                        new_hands[1] = state['hands'][1][:]
                        new_hands[2] = state['hands'][2][:]
                        new_hands[3] = state['hands'][3][:]

                        new_board[0] = card
                        new_history.append(card)
                        new_history = sorted(new_history)
                        new_hands[0][card_index] = -1

                        alternative_history = state['current_history'][:]
                        alternative_history.append(card)
                        alternative_history = sorted(alternative_history)

                        alternative_new_hands = [[], [], [], []]
                        alternative_new_hands[0] = new_hands[0][:]
                        alternative_new_hands[1] = []
                        alternative_new_hands[2] = state['current_s_hand'][:]
                        alternative_new_hands[3] = []

                        new_clock = state['clock']
                        new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                     'board': new_board,
                                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                     'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                     'current_history': alternative_history}
                        alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                 'board': new_board[0],
                                                 'beginning': state['beginning'], 'history': alternative_history}
                        action = {0: card, 1: -1, 2: -1, 3: -1}
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        alternative_new_state_str = ' '.join(
                            str(alternative_new_state[e]) for e in alternative_new_state)
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
            elif state['next'] == 1:
                # Player 0 Wait
                for card_index, card in enumerate(state['hands'][state['next']]):
                    if not ((not have_color) or (card % 10) == color) or card == -1:
                        continue

                    new_board = state['board'][:]
                    new_board[state['next']] = card

                    new_history = state['history'][:]
                    new_history.append(card)
                    new_history = sorted(new_history)

                    if state['board'][2] != -1:
                        new_next = (state['next'] + 2) % 4
                        new_clock = state['clock'] + 2
                    else:
                        new_next = (state['next'] + 1) % 4
                        new_clock = state['clock'] + 1

                    new_hands = [[], [], [], []]
                    new_hands[0] = state['hands'][0][:]
                    new_hands[1] = state['hands'][1][:]
                    new_hands[2] = state['hands'][2][:]
                    new_hands[3] = state['hands'][3][:]
                    new_hands[state['next']][card_index] = -1

                    alternative_new_hands = [[], [], [], []]
                    alternative_new_hands[0] = new_hands[0][:]
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': state['current_history'][:]}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': state['current_history'][:]}
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
                # Player 0 play his card
                if state['board'][0] == -1:
                    for card_index, card in enumerate(state['hands'][state['next']]):
                        if not ((not have_color) or (card % 10) == color) or card == -1:
                            continue
                        for card_index2, card2 in enumerate(state['hands'][0]):
                            if card2 == -1:
                                continue
                            new_board = state['board'][:]
                            new_board[state['next']] = card
                            new_board[0] = card2

                            new_history = state['history'][:]
                            new_history.append(card)
                            new_history.append(card2)
                            new_history = sorted(new_history)

                            alternative_history = state['current_history'][:]
                            alternative_history.append(card2)
                            alternative_history = sorted(alternative_history)

                            if state['board'][2] != -1:
                                new_next = (state['next'] + 2) % 4
                                new_clock = state['clock'] + 2
                            else:
                                new_next = (state['next'] + 1) % 4
                                new_clock = state['clock'] + 1

                            new_hands = [[], [], [], []]
                            new_hands[0] = state['hands'][0][:]
                            new_hands[1] = state['hands'][1][:]
                            new_hands[2] = state['hands'][2][:]
                            new_hands[3] = state['hands'][3][:]
                            new_hands[state['next']][card_index] = -1
                            new_hands[0][card_index2] = -1

                            alternative_new_hands = [[], [], [], []]
                            alternative_new_hands[0] = new_hands[0][:]
                            alternative_new_hands[1] = []
                            alternative_new_hands[2] = state['current_s_hand'][:]
                            alternative_new_hands[3] = []

                            new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                         'board': new_board,
                                         'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                         'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                         'current_history': alternative_history}
                            alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                     'board': new_board[0],
                                                     'beginning': state['beginning'],
                                                     'history': alternative_history}
                            agent_number = state['next']
                            if agent_number == 2:
                                agent_number = 0
                            action = {0: card2, 1: -1, 2: -1, 3: -1}
                            action[agent_number] = card
                            new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                            alternative_new_state_str = ' '.join(
                                str(alternative_new_state[e]) for e in alternative_new_state)
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
                # Player 0 play card from table
                for card_index, card in enumerate(state['hands'][state['next']]):
                    if not ((not have_color) or (card % 10) == color) or card == -1:
                        continue
                    for card_index2, card2 in enumerate(state['current_s_hand']):
                        if card2 == -1:
                            continue

                        new_board = state['board'][:]
                        new_board[state['next']] = card

                        new_history = state['history'][:]
                        new_history.append(card)

                        new_next = (state['next'] + 2) % 4
                        new_clock = state['clock'] + 2

                        new_hands = [[], [], [], []]
                        new_hands[0] = state['hands'][0][:]
                        new_hands[1] = state['hands'][1][:]
                        new_hands[2] = state['hands'][2][:]
                        new_hands[3] = state['hands'][3][:]
                        new_hands[state['next']][card_index] = -1

                        if state['board'][2] == -1:
                            new_board[2] = card2
                            new_history.append(card2)
                            new_hands[2][card_index2] = -1

                        new_history = sorted(new_history)

                        alternative_new_hands = [[], [], [], []]
                        alternative_new_hands[0] = new_hands[0][:]
                        alternative_new_hands[1] = []
                        alternative_new_hands[2] = state['current_s_hand'][:]
                        alternative_new_hands[3] = []

                        new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                     'board': new_board,
                                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                     'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                     'current_history': state['current_history'][:]}
                        alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                 'board': new_board[0],
                                                 'beginning': state['beginning'],
                                                 'history': state['current_history'][:]}

                        agent_number = state['next']
                        if agent_number == 2:
                            agent_number = 0
                        action = {0: card2, 1: -1, 2: -1, 3: -1}
                        action[agent_number] = card
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        alternative_new_state_str = ' '.join(
                            str(alternative_new_state[e]) for e in alternative_new_state)
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
            elif state['next'] == 3:
                # Player 0 Wait
                for card_index, card in enumerate(state['hands'][state['next']]):
                    if not ((not have_color) or (card % 10) == color) or card == -1:
                        continue
                    new_board = state['board'][:]
                    new_board[state['next']] = card

                    new_history = state['history'][:]
                    new_history.append(card)
                    new_history = sorted(new_history)

                    if state['board'][0] != -1:
                        new_next = (state['next'] + 2) % 4
                        new_clock = state['clock'] + 2
                    else:
                        new_next = (state['next'] + 1) % 4
                        new_clock = state['clock'] + 1

                    new_hands = [[], [], [], []]
                    new_hands[0] = state['hands'][0][:]
                    new_hands[1] = state['hands'][1][:]
                    new_hands[2] = state['hands'][2][:]
                    new_hands[3] = state['hands'][3][:]
                    new_hands[state['next']][card_index] = -1

                    alternative_new_hands = [[], [], [], []]
                    alternative_new_hands[0] = new_hands[0][:]
                    alternative_new_hands[1] = []
                    alternative_new_hands[2] = state['current_s_hand'][:]
                    alternative_new_hands[3] = []

                    new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next, 'board': new_board,
                                 'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                 'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                 'current_history': state['current_history'][:]}
                    alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'],
                                             'board': new_board[0],
                                             'beginning': state['beginning'], 'history': state['current_history'][:]}

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
                # Player 0 play his card
                if state['board'][0] == -1:
                    for card_index, card in enumerate(state['hands'][state['next']]):
                        if not ((not have_color) or (card % 10) == color) or card == -1:
                            continue
                        for card_index2, card2 in enumerate(state['hands'][0]):
                            if card2 == -1:
                                continue

                            new_board = state['board'][:]
                            new_board[state['next']] = card
                            new_board[0] = card2

                            new_history = state['history'][:]
                            new_history.append(card)
                            new_history.append(card2)
                            new_history = sorted(new_history)

                            alternative_history = state['current_history'][:]
                            alternative_history.append(card2)
                            alternative_history = sorted(alternative_history)

                            new_next = (state['next'] + 2) % 4
                            new_clock = state['clock'] + 2

                            new_hands = [[], [], [], []]
                            new_hands[0] = state['hands'][0][:]
                            new_hands[1] = state['hands'][1][:]
                            new_hands[2] = state['hands'][2][:]
                            new_hands[3] = state['hands'][3][:]
                            new_hands[state['next']][card_index] = -1
                            new_hands[0][card_index2] = -1

                            alternative_new_hands = [[], [], [], []]
                            alternative_new_hands[0] = new_hands[0][:]
                            alternative_new_hands[1] = []
                            alternative_new_hands[2] = state['current_s_hand'][:]
                            alternative_new_hands[3] = []

                            new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                         'board': new_board,
                                         'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                         'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                         'current_history': alternative_history}
                            alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'][:],
                                                     'board': new_board[0],
                                                     'beginning': state['beginning'],
                                                     'history': alternative_history}

                            agent_number = state['next']
                            if agent_number == 2:
                                agent_number = 0
                            action = {0: card2, 1: -1, 2: -1, 3: -1}
                            action[agent_number] = card
                            new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                            alternative_new_state_str = ' '.join(
                                str(alternative_new_state[e]) for e in alternative_new_state)
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
                # Player 0 play card from table
                for card_index, card in enumerate(state['hands'][state['next']]):
                    if not ((not have_color) or (card % 10) == color) or card == -1:
                        continue
                    for card_index2, card2 in enumerate(state['current_s_hand']):
                        if card2 == -1:
                            continue

                        new_board = state['board'][:]
                        new_board[state['next']] = card

                        new_history = state['history'][:]
                        new_history.append(card)

                        if state['board'][0] == -1:
                            new_next = (state['next'] + 1) % 4
                            new_clock = state['clock'] + 1
                        else:
                            new_next = (state['next'] + 2) % 4
                            new_clock = state['clock'] + 2

                        new_hands = [[], [], [], []]
                        new_hands[0] = state['hands'][0][:]
                        new_hands[1] = state['hands'][1][:]
                        new_hands[2] = state['hands'][2][:]
                        new_hands[3] = state['hands'][3][:]
                        new_hands[state['next']][card_index] = -1

                        if state['board'][2] == -1:
                            new_board[2] = card2
                            new_history.append(card2)
                            new_hands[2][card_index2] = -1

                        new_history = sorted(new_history)

                        alternative_new_hands = [[], [], [], []]
                        alternative_new_hands[0] = new_hands[0][:]
                        alternative_new_hands[1] = []
                        alternative_new_hands[2] = state['current_s_hand'][:]
                        alternative_new_hands[3] = []

                        new_state = {'hands': new_hands, 'lefts': state['lefts'][:], 'next': new_next,
                                     'board': new_board,
                                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                                     'suit': state['suit'], 'current_s_hand': state['current_s_hand'][:],
                                     'current_history': state['current_history'][:]}
                        alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'],
                                                 'board': new_board[0],
                                                 'beginning': state['beginning'],
                                                 'history': state['current_history'][:]}

                        agent_number = state['next']
                        if agent_number == 2:
                            agent_number = 0
                        action = {0: card2, 1: -1, 2: -1, 3: -1}
                        action[agent_number] = card
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        alternative_new_state_str = ' '.join(
                            str(alternative_new_state[e]) for e in alternative_new_state)
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
    prepare_blind_epistemic_relation(bridge_model, states_dictionary, alternative_states_dictionary)
    end = time.clock()
    gc.enable()
    full_time += end - start
    print("Created indistuiginshable relation in", end - start, "s")
    print("Created whole model in", full_time, "s")
    return bridge_model


def generate_abstract_bridge_model_for_epistemic(no_cards_available, no_end_cards, first_state, abstraction):
    global number_of_beginning_states

    if no_end_cards == 1:
        bridge_model = ATLModel(3, 100)
    elif no_end_cards == 2:
        bridge_model = ATLModel(3, 1000)
    elif no_end_cards == 3:
        bridge_model = ATLModel(3, 100000)
    elif no_end_cards == 4:
        bridge_model = ATLModel(3, 1000000)
    else:
        bridge_model = ATLModel(3, 8000000)

    full_time = 0
    cards_available = prepare_available_cards(no_cards_available, bridge_model)

    bridge_model.add_action(0, 1001)
    bridge_model.add_action(0, 1002)
    bridge_model.add_action(0, 1003)
    bridge_model.add_action(0, 1004)
    pr = []
    pr.append(cards_available[:])
    bridge_model.add_action(0, -1)
    states = []
    abstract_states = []
    states_dictionary = {}
    abstract_states_dictionary = {}
    alternative_states_dictionary = {}
    state_number = 0
    abstract_state_number = 0
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

        abstract_new_hands = [[], [], [], []]
        for i in range(0, 4):
            abstract_new_hands[i] = new_hands[i][:]
            if i == 1 or i == 3:
                for j in range(0, len(abstract_new_hands[i])):
                    if abstract_new_hands[i][j] in abstraction:
                        abstract_new_hands[i][j] = 1000 + abstract_new_hands[i][j] % 10
                abstract_new_hands[i] = sorted(abstract_new_hands[i])

        # print(abstract_new_hands)

        alternative_new_hands = abstract_new_hands[:]
        alternative_new_hands[1] = []
        alternative_new_hands[3] = []

        state = {'hands': new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                 'beginning': 0, 'history': first_state['history'], 'clock': 0, 'suit': -1}
        abstract_state = {'hands': abstract_new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                          'beginning': 0, 'history': first_state['history'], 'clock': 0, 'suit': -1}
        alternative_state = {'hands': alternative_new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                          'beginning': 0, 'history': first_state['history'], 'clock': 0, 'suit': -1}
        states.append(state)
        state_str = ' '.join(str(state[e]) for e in state)
        abstract_state_str = ' '.join(str(abstract_state[e]) for e in abstract_state)
        alternative_state_str = ' '.join(str(alternative_state[e]) for e in alternative_state)
        states_dictionary[state_str] = state_number
        if abstract_state_str not in abstract_states_dictionary:
            abstract_states_dictionary[abstract_state_str] = abstract_state_number
            if alternative_state_str not in alternative_states_dictionary:
                alternative_states_dictionary[alternative_state_str] = {abstract_state_number}
            else:
                alternative_states_dictionary[alternative_state_str].add(abstract_state_number)

            abstract_state_number += 1
            abstract_states.append(abstract_state)
        # else:
        #     new_state_number = abstract_states_dictionary[abstract_state_str]

        state_number += 1

    end = time.clock()
    full_time += end - start
    print("Created beginning states of model in", end - start, "s")
    print("Number of beginning states of model:", len(states))
    number_of_beginning_states = len(abstract_states)
    print("Start creating rest of model")
    start = time.clock()
    current_state_number = -1
    for state in states:
        abstract_hands = [[], [], [], []]
        for i in range(0, 4):
            abstract_hands[i] = state['hands'][i][:]
            if i == 1 or i == 3:
                for j in range(0, len(abstract_hands[i])):
                    if abstract_hands[i][j] in abstraction:
                        abstract_hands[i][j] = 1000 + abstract_hands[i][j] % 10
                abstract_hands[i] = sorted(abstract_hands[i])

        # print(abstract_hands)

        abstract_history = state['history'][:]
        for i in range(0, len(abstract_history)):
            if abstract_history[i] in abstraction:
                abstract_history[i] = 1000 + abstract_history[i] % 10
        abstract_history = sorted(abstract_history)

        abstract_board = state['board'][:]
        if abstract_board[1] in abstraction:
            abstract_board[1] = 1000 + abstract_board[1] % 10
        if abstract_board[3] in abstraction:
            abstract_board[3] = 1000 + abstract_board[3] % 10

        abstract_current_state = {'hands': abstract_hands, 'lefts': state['lefts'], 'next': state['next'],
                                  'board': abstract_board, 'beginning': state['beginning'], 'history': abstract_history,
                                  'clock': state['clock'], 'suit': state['suit']}

        abstract_state_str = ' '.join(str(abstract_current_state[e]) for e in abstract_current_state)

        current_state_number = abstract_states_dictionary[abstract_state_str]

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

                abstract_history = new_history[:]
                for i in range(0, len(abstract_history)):
                    if abstract_history[i] in abstraction:
                        abstract_history[i] = 1000 + abstract_history[i] % 10

                abstract_history = sorted(abstract_history)

                abstract_board = new_board[:]
                if abstract_board[1] in abstraction:
                    abstract_board[1] = 1000 + abstract_board[1] % 10
                if abstract_board[3] in abstraction:
                    abstract_board[3] = 1000 + abstract_board[3] % 10

                new_next = (state['next'] + 1) % 4
                new_clock = state['clock'] + 1
                new_hands = [[], [], [], []]
                abstract_new_hands = [[], [], [], []]
                for i in range(0, 4):
                    new_hands[i] = state['hands'][i][:]
                    abstract_new_hands[i] = state['hands'][i][:]
                    if i == 1 or i == 3:
                        for j in range(0, len(abstract_new_hands[i])):
                            if abstract_new_hands[i][j] in abstraction:
                                abstract_new_hands[i][j] = 1000 + abstract_new_hands[i][j] % 10

                new_hands[state['next']][card_index] = -1
                abstract_new_hands[state['next']][card_index] = -1
                abstract_new_hands[1] = sorted(abstract_new_hands[1])
                abstract_new_hands[3] = sorted(abstract_new_hands[3])

                alternative_new_hands = [[], [], [], []]
                alternative_new_hands[0] = abstract_new_hands[0][:]
                alternative_new_hands[1] = keep_values_in_list(abstract_new_hands[1], -1)
                alternative_new_hands[2] = abstract_new_hands[2][:]
                alternative_new_hands[3] = keep_values_in_list(abstract_new_hands[3], -1)

                # print(alternative_new_hands)

                new_suit = card % 10
                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                             'suit': new_suit}

                abstract_new_state = {'hands': abstract_new_hands, 'lefts': state['lefts'], 'next': new_next,
                                      'board': abstract_board,
                                      'beginning': state['beginning'], 'history': abstract_history, 'clock': new_clock,
                                      'suit': new_suit}

                alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'], 'next': new_next,
                                         'board': abstract_board,
                                         'beginning': state['beginning'], 'history': abstract_history, 'clock': new_clock,
                                         'suit': new_suit}

                agent_number = state['next']
                if agent_number == 2:
                    agent_number = 0
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                action[agent_number] = card
                if (agent_number == 1 or agent_number == 3) and (card in abstraction):
                    action[agent_number] = 1000 + card % 10
                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                abstract_new_state_str = ' '.join(str(abstract_new_state[e]) for e in abstract_new_state)
                alternative_new_state_str = ' '.join(str(alternative_new_state[e]) for e in alternative_new_state)
                if new_state_str not in states_dictionary:
                    states_dictionary[new_state_str] = state_number
                    # new_state_number = state_number
                    states.append(new_state)
                    state_number += 1
                # else:
                #     new_state_number = states_dictionary[new_state_str]

                if abstract_new_state_str not in abstract_states_dictionary:
                    abstract_states_dictionary[abstract_new_state_str] = abstract_state_number
                    new_state_number = abstract_state_number
                    abstract_state_number += 1
                    abstract_states.append(abstract_new_state)
                else:
                    new_state_number = abstract_states_dictionary[abstract_new_state_str]

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

            abstract_history = new_history[:]
            for i in range(0, len(abstract_history)):
                if abstract_history[i] in abstraction:
                    abstract_history[i] = 1000 + abstract_history[i] % 10

            abstract_history = sorted(abstract_history)

            abstract_new_hands = [[], [], [], []]
            for i in range(0, 4):
                abstract_new_hands[i] = state['hands'][i][:]
                if i == 1 or i == 3:
                    for j in range(0, len(abstract_new_hands[i])):
                        if abstract_new_hands[i][j] in abstraction:
                            abstract_new_hands[i][j] = 1000 + abstract_new_hands[i][j] % 10
                    abstract_new_hands[i] = sorted(abstract_new_hands[i])

            alternative_new_hands = [[], [], [], []]
            alternative_new_hands[0] = abstract_new_hands[0][:]
            alternative_new_hands[1] = keep_values_in_list(abstract_new_hands[1], -1)
            alternative_new_hands[2] = abstract_new_hands[2][:]
            alternative_new_hands[3] = keep_values_in_list(abstract_new_hands[3], -1)

            new_state = {'hands': state['hands'], 'lefts': new_lefts, 'next': new_next, 'board': [-1, -1, -1, -1],
                         'beginning': new_beginning, 'history': new_history, 'clock': new_clock, 'suit': new_suit}
            abstract_new_state = {'hands': abstract_new_hands, 'lefts': new_lefts, 'next': new_next,
                                  'board': [-1, -1, -1, -1],
                                  'beginning': new_beginning, 'history': abstract_history, 'clock': new_clock,
                                  'suit': new_suit}
            alternative_new_state = {'hands': alternative_new_hands, 'lefts': new_lefts, 'next': new_next,
                                     'board': [-1, -1, -1, -1],
                                     'beginning': new_beginning, 'history': abstract_history, 'clock': new_clock,
                                     'suit': new_suit}
            new_state_str = ' '.join(str(new_state[e]) for e in new_state)
            abstract_new_state_str = ' '.join(str(abstract_new_state[e]) for e in abstract_new_state)
            alternative_new_state_str = ' '.join(str(alternative_new_state[e]) for e in alternative_new_state)
            if new_state_str not in states_dictionary:
                states_dictionary[new_state_str] = state_number
                # new_state_number = state_number
                states.append(new_state)
                state_number += 1
            # else:
            #     new_state_number = states_dictionary[new_state_str]

            if abstract_new_state_str not in abstract_states_dictionary:
                abstract_states_dictionary[abstract_new_state_str] = abstract_state_number
                new_state_number = abstract_state_number
                abstract_state_number += 1
                abstract_states.append(abstract_new_state)
            else:
                new_state_number = abstract_states_dictionary[abstract_new_state_str]

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

                abstract_board = new_board[:]
                if abstract_board[1] in abstraction:
                    abstract_board[1] = 1000 + abstract_board[1] % 10
                if abstract_board[3] in abstraction:
                    abstract_board[3] = 1000 + abstract_board[3] % 10

                new_history = state['history'][:]
                new_history.append(card)
                new_history = sorted(new_history)

                abstract_history = new_history[:]
                for i in range(0, len(abstract_history)):
                    if abstract_history[i] in abstraction:
                        abstract_history[i] = 1000 + abstract_history[i] % 10

                abstract_history = sorted(abstract_history)

                new_next = (state['next'] + 1) % 4
                new_hands = [[], [], [], []]
                new_hands[0] = state['hands'][0][:]
                new_hands[1] = state['hands'][1][:]
                new_hands[2] = state['hands'][2][:]
                new_hands[3] = state['hands'][3][:]
                new_hands[state['next']][card_index] = -1

                abstract_new_hands = [[], [], [], []]
                for i in range(0, 4):
                    abstract_new_hands[i] = state['hands'][i][:]
                    if i == 1 or i == 3:
                        for j in range(0, len(abstract_new_hands[i])):
                            if abstract_new_hands[i][j] in abstraction:
                                abstract_new_hands[i][j] = 1000 + abstract_new_hands[i][j] % 10

                abstract_new_hands[state['next']][card_index] = -1
                abstract_new_hands[1] = sorted(abstract_new_hands[1])
                abstract_new_hands[3] = sorted(abstract_new_hands[3])

                alternative_new_hands = [[], [], [], []]
                alternative_new_hands[0] = abstract_new_hands[0][:]
                alternative_new_hands[1] = keep_values_in_list(abstract_new_hands[1], -1)
                alternative_new_hands[2] = abstract_new_hands[2][:]
                alternative_new_hands[3] = keep_values_in_list(abstract_new_hands[3], -1)

                new_clock = state['clock'] + 1
                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                             'suit': state['suit']}
                abstract_new_state = {'hands': abstract_new_hands, 'lefts': state['lefts'], 'next': new_next,
                                      'board': abstract_board,
                                      'beginning': state['beginning'], 'history': abstract_history, 'clock': new_clock,
                                      'suit': state['suit']}
                alternative_new_state = {'hands': alternative_new_hands, 'lefts': state['lefts'], 'next': new_next,
                                         'board': abstract_board,
                                         'beginning': state['beginning'], 'history': abstract_history, 'clock': new_clock,
                                         'suit': state['suit']}

                agent_number = state['next']
                if agent_number == 2:
                    agent_number = 0
                action = {0: -1, 1: -1, 2: -1, 3: -1}
                action[agent_number] = card
                if (agent_number == 1 or agent_number == 3) and (card in abstraction):
                    action[agent_number] = 1000 + card % 10
                new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                abstract_new_state_str = ' '.join(str(abstract_new_state[e]) for e in abstract_new_state)
                alternative_new_state_str = ' '.join(str(alternative_new_state[e]) for e in alternative_new_state)
                if new_state_str not in states_dictionary:
                    states_dictionary[new_state_str] = state_number
                    # new_state_number = state_number
                    states.append(new_state)
                    state_number += 1
                # else:
                #     new_state_number = states_dictionary[new_state_str]

                if abstract_new_state_str not in abstract_states_dictionary:
                    abstract_states_dictionary[abstract_new_state_str] = abstract_state_number
                    new_state_number = abstract_state_number
                    abstract_state_number += 1
                    abstract_states.append(abstract_new_state)
                else:
                    new_state_number = abstract_states_dictionary[abstract_new_state_str]

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
    bridge_model.states = abstract_states
    prepare_blind_epistemic_relation(bridge_model, abstract_states_dictionary, alternative_states_dictionary)
    end = time.clock()
    gc.enable()
    full_time += end - start
    print("Created indistuiginshable relation in", end - start, "s")
    print("Created whole model in", full_time, "s")
    return bridge_model


def prepare_available_cards(no_cards_available, bridge_model):
    cards_available = []
    card_number = 14
    for i in range(0, no_cards_available):
        for c in range(1, 5):
            cards_available.append(card_number * 10 + (5 - c))
            bridge_model.add_action(0, card_number * 10 + (5 - c))
        card_number -= 1

    return cards_available


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


def prepare_blind_epistemic_relation(bridge_model, states_dictionary, alternative_states_dictionary):
    for state, epistemic_class in alternative_states_dictionary.items():
        bridge_model.add_epistemic_class(0, epistemic_class)


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


def generate_random_hands(no_cards_available, no_cards_in_hand):
    array = []
    used = []
    # card_numbers = [144, 143, 142, 141, 134, 133, 132, 131, 124, 123, 122, 121, 114, 113, 112, 111, 104, 103, 102, 101,
    #                 94, 93, 92, 91]
    card_numbers = []
    for i in range(14, 0, -1):
        for j in range(4, 0, -1):
            card_numbers.append(i * 10 + j)

    print(card_numbers)

    for i in range(0, no_cards_available * 4):
        used.append(False)

    for i in range(0, no_cards_in_hand * 4):
        number = random.randrange(no_cards_available * 4)
        while used[number]:
            number = random.randrange(no_cards_available * 4)

        array.append(card_numbers[number])
        used[number] = True

    hands = []
    j = 0
    for i in range(0, 4):
        hand = []
        for _ in range(0, no_cards_in_hand):
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


tgen = 0
low_tverif = 0
up_tverif = 0
low_true = 0
up_true = 0
match = 0
states_count = 0


def test_bridge_model(n, m):
    global tgen
    global low_tverif
    global up_tverif
    global low_true
    global up_true
    global match
    global states_count

    hands = generate_random_hands(n, m)
    # hands = [[133, 134], [132, 143], [141, 144], [131, 142]]
    # hands = [[133, 141, 142], [123, 143, 144], [121, 122, 124], [131, 132, 134]]
    # hands = [[124, 134, 144], [74, 84, 94], [64, 104, 114], [34, 44, 91]]
    # hands = [[124, 134, 144], [71, 72, 74], [122, 132, 142], [64, 81, 82]]
    # hands = [[124, 131, 142, 144], [111, 112, 133, 141], [114, 122, 123, 143], [113, 121, 132, 134]]
    print('Hands:', hands)
    print('Readable hands:', hands_to_readable_hands(hands))
    # print("Blind bridge model")
    print("Abstract bridge model")

    start = time.clock()
    # hands = [[121, 133, 141, 143], [114, 122, 134, 142], [111, 112, 123, 132], [113, 124, 131, 144]]
    bridge_model = generate_abstract_bridge_model_for_epistemic(n, m, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                                                       'hands': hands, 'next': 0, 'history': [],
                                                                       'beginning': 0, 'clock': 0, 'suit': -1},
                                                                [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42,
                                                                 43, 44, 51, 52, 53, 54, 61, 62, 63, 64, 71, 72, 73, 74,
                                                                 81, 82, 83, 84, 91, 92, 93, 94])

    # bridge_model = generate_bridge_model_for_epistemic(n, m, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
    #                                                                    'hands': hands, 'next': 0, 'history': [],
    #                                                                    'beginning': 0, 'clock': 0, 'suit': -1})

    end = time.clock()

    tgen += (end - start)
    # print("Maximal memory usage ", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # bridge_model.walk(0)
    states_count += len(bridge_model.states)
    winning_states = []
    i = -1
    for state in bridge_model.states:
        i += 1
        if state['lefts'][0] >= m / 2 and state['lefts'][0] + state['lefts'][1] == m:
            winning_states.append(i)
            # print(i)
            # print(state)
        # elif state['lefts'][0] + state['lefts'][1] == m:
            # print(state)


    print("Start formula verification under imperfect information")
    start = time.clock()
    result = bridge_model.minimum_formula_one_agent_multiple_states(0, winning_states)
    end = time.clock()
    low_tverif += (end - start)
    print("Time:", end - start, "s")
    print("Number of good states ", len(result))
    number_of_correct_beginning_states = 0
    for state_nr in result:
        # if len(bridge_model.states[state_nr]['history']) <= 4:
        #     print(bridge_model.states[state_nr])
        if len(bridge_model.states[state_nr]['history']) == 0 and bridge_model.states[state_nr]['board'] == [-1, -1, -1,
                                                                                                             -1]:
            number_of_correct_beginning_states += 1

    print("Formula result:", number_of_beginning_states == number_of_correct_beginning_states)
    imperfect = False
    if number_of_beginning_states == number_of_correct_beginning_states:
        low_true += 1
        imperfect = True

    print("Start formula verification under perfect information")
    start = time.clock()
    result = bridge_model.minimum_formula_one_agent_multiple_states_perfect_information(0, winning_states)
    end = time.clock()
    up_tverif += (end - start)
    print("Time:", end - start, "s")
    print("Number of good states ", len(result))
    number_of_correct_beginning_states = 0
    for state_nr in result:
        if len(bridge_model.states[state_nr]['history']) == 0 and bridge_model.states[state_nr]['board'] == [-1, -1, -1,
                                                                                                             -1]:
            number_of_correct_beginning_states += 1

    print("Formula result:", number_of_beginning_states == number_of_correct_beginning_states)

    perfect = False
    if number_of_beginning_states == number_of_correct_beginning_states:
        up_true += 1
        perfect = True

    if perfect == imperfect:
        match += 1


def remove_values_from_list(the_list, val):
    return [value for value in the_list if value != val]


def keep_values_in_list(the_list, val):
    return [value for value in the_list if value == val]


n = int(input("number of figures in game ="))
m = int(input("number of cards in hand ="))
number_of_tests = int(input("Number of tests="))

for _ in range(0, number_of_tests):
    test_bridge_model(n, m)
    print()

print()
print("STATISTICS")
print("#states", states_count / number_of_tests)
print("tgen", tgen / number_of_tests)
print("low tverif", low_tverif / number_of_tests)
print("low true", 100 * (low_true / number_of_tests), "%")
print("up tverif", up_tverif / number_of_tests)
print("up true", 100 * (up_true / number_of_tests), "%")
print("match", 100 * (match / number_of_tests), "%")
# Pik Kier Karo Trefl
# Spade Heart Diamond Club
