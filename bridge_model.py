from atl_model import *
import time
import pickle
import gc
import resource

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
    print(bridge_model.numberOfAgents)
    print(bridge_model.numberOfStates)
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


def generate_bridge_model_for_epistemic(no_cards_available, no_end_cards, first_state):
    # with open('atl_3_1294940.pkl', 'rb') as input:
    #     bridge_model = pickle.load(input)
    # 1294936 dla (3,2)
    # bridge_model = ATLModel(3, 3445920)
    bridge_model = ATLModel(3, 4000000)
    # bridge_model = ATLModel(3, 415950)
    print(bridge_model.numberOfAgents)
    print(bridge_model.numberOfStates)
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
    print("Start creating beginning epistemic class states of model")
    # gc.disable()
    enemy_hands = first_state['hands'][1][:] + first_state['hands'][3][:]
    start = time.clock()
    for player2 in itertools.combinations(enemy_hands, no_end_cards):
        player4 = enemy_hands[:]
        for i in player2:
            player4.remove(i)
        new_hands = first_state['hands'][:]
        new_hands[1] = list(player2)
        new_hands[3] = list(player4)
        state = {'hands': new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                 'beginning': 0, 'history': first_state['history'], 'clock': 0, 'suit': -1}
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

                new_history = state['history'].copy()
                new_history.add(card)

                new_next = (state['next'] + 1) % 4
                new_clock = state['clock'] +1
                new_hands = [[], [], [], []]
                new_hands[0] = state['hands'][0][:]
                new_hands[1] = state['hands'][1][:]
                new_hands[2] = state['hands'][2][:]
                new_hands[3] = state['hands'][3][:]
                new_hands[state['next']].remove(card)
                new_suit = card % 10
                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': new_history, 'clock': new_clock, 'suit': new_suit}
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
            new_history = state['history'].copy()
            # for i in state['board']:
            #     new_history.add(i)
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
            new_state = {'hands': state['hands'], 'lefts': new_lefts, 'next': new_next, 'board': [-1, -1, -1, -1],
                         'beginning': new_beginning, 'history': new_history, 'clock': new_clock, 'suit': new_suit}
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

                new_history = state['history'].copy()
                new_history.add(card)

                new_next = (state['next'] + 1) % 4
                new_hands = [[], [], [], []]
                new_hands[0] = state['hands'][0][:]
                new_hands[1] = state['hands'][1][:]
                new_hands[2] = state['hands'][2][:]
                new_hands[3] = state['hands'][3][:]
                new_hands[state['next']].remove(card)
                if new_next == state['beginning']:
                    new_next = -1

                new_clock = state['clock'] + 1
                new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                             'beginning': state['beginning'], 'history': new_history, 'clock': new_clock, 'suit': state['suit']}
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
    prepare_epistemic_relation(bridge_model, states_dictionary)
    end = time.clock()
    gc.enable()
    print("Created indistuiginshable relation in", end - start, "s")
    # with open('same_array_3_2.pkl', 'wb') as output:
    #     pickle.dump(same_relation, output, pickle.HIGHEST_PROTOCOL)

    return bridge_model


def prepare_epistemic_relation(bridge_model, states_dictionary):
    states = bridge_model.states
    visited_states = [0 for i in itertools.repeat(None, len(states))]
    for i in range(0, len(states)):
        if visited_states[i] == 1:
            continue
        epistemic_class = prepare_epistemic_class_for_state(states[i])
        for x in range(0, len(epistemic_class)):
            state_a = epistemic_class[x]
            state_a_string = ' '.join(str(state_a[e]) for e in state_a)
            if state_a_string not in states_dictionary:
                continue
            state_a_number = states_dictionary[state_a_string]
            visited_states[state_a_number] = 1
            for y in range(x + 1, len(epistemic_class)):
                state_b = epistemic_class[y]
                state_b_string = ' '.join(str(state_b[e]) for e in state_b)
                # print(state_a_string)
                # print(state_b_string)
                if state_b_string not in states_dictionary:
                    continue
                state_b_number = states_dictionary[state_b_string]
                bridge_model.set_same_state(0, state_a_number, state_b_number)

                # for i in range(0, len(states)):
                #     for j in range(i + 1, len(states)):
                #         state_a = states[i]
                #         state_b = states[j]
                #         if len(state_a['hands'][0]) != len(state_b['hands'][0]):
                #             break
                #         if state_a['hands'][0] == state_b['hands'][0] and state_a['hands'][2] == state_b['hands'][2] and state_a[
                #             'lefts'] == state_b['lefts'] and state_a['board'] == state_b['board'] and state_a['beginning'] == \
                #                 state_b['beginning'] and state_a['next'] == state_b['next'] and state_a['history'] == state_b[
                #             'history']:
                #             bridge_model.set_same_state(0, i, j)


def prepare_epistemic_class_for_state(state):
    no_cards_player_2 = len(state['hands'][1])
    cards = state['hands'][1] + state['hands'][3]
    # print(cards)
    epistemic_class = [state]
    for player_2_cards in itertools.combinations(cards, no_cards_player_2):
        player_4_cards = cards[:]
        for card in player_2_cards:
            player_4_cards.remove(card)
        new_hands = [state['hands'][0], list(player_2_cards), state['hands'][2], list(player_4_cards)]
        new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': state['next'], 'board': state['board'],
                     'beginning': state['beginning'], 'history': state['history']}
        epistemic_class.append(new_state)
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


# write_bridge_model(3, 1)

# with open('bridge_2_2.pkl', 'rb') as input:
#     bridge_model = pickle.load(input)
# print("Ilość stanów ", len(bridge_model.states))

# bridge_model = generate_bridge_model(2, 2)

# bridge_model = generate_bridge_model_for_epistemic(1, 1, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
#                                                           'hands': [[144], [143], [142],
#                                                                     [141]], 'next': 0, 'history': set(),
#                                                           'beginning': 0, 'clock': 0, 'suit': -1})

bridge_model = generate_bridge_model_for_epistemic(2, 2, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                                          'hands': [[144, 143], [142, 141], [134, 133],
                                                                    [132, 131]], 'next': 0, 'history': set(),
                                                          'beginning': 0, 'clock': 0, 'suit': -1})

# bridge_model = generate_bridge_model_for_epistemic(2, 1, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
#                                                           'hands': [[134], [144], [133],
#                                                                     [132]], 'next': 0, 'history': set(),
#                                                           'beginning': 0, 'clock': 0, 'suit': -1})

# bridge_model = generate_bridge_model_for_epistemic(3, 3, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
#                                                           'hands': [[144, 143, 142], [141, 134, 133], [132, 131, 124],
#                                                                     [123, 122, 121]], 'next': 0, 'history': set(),
#                                                           'beginning': 0, 'clock': 0, 'suit': -1})
# bridge_model = generate_bridge_model_for_epistemic(4, 4, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
#                                                           'hands': [[114, 113, 112, 111], [144, 143, 142, 141],
#                                                                     [134, 133, 132, 131], [124, 123, 122, 121]],
#                                                           'next': 0, 'history': set(),
#                                                           'beginning': 0, 'clock': 0, 'suit': -1})
# bridge_model = read_bridge_model(3)
print("Ilość stanów ", len(bridge_model.states))
print("Maksymalne zużycie pamięci ", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

for state in bridge_model.states:
    print(state)


winning_states = []
i = -1
for state in bridge_model.states:
    i += 1
    if len(state['hands'][0]) == 0 and state['lefts'][0] == 2:
        winning_states.append(i)

start = time.clock()
wynik = bridge_model.minimum_formula_one_agent_multiple_states(0, winning_states)
end = time.clock()
print("Time:", end - start, "s")
print("Ilość spełniających stanów ", len(wynik))
for state_nr in wynik:
    if len(bridge_model.states[state_nr]['history']) == 0 and bridge_model.states[state_nr]['board'] == [-1, -1, -1,
                                                                                                         -1]:
        print(bridge_model.states[state_nr])

print("Model checking perfect information")
start = time.clock()
wynik = bridge_model.minimum_formula_one_agent_multiple_states_perfect_information(0, winning_states)
end = time.clock()
print("Time:", end - start, "s")
print("Ilość spełniających stanów ", len(wynik))
for state_nr in wynik:
    if len(bridge_model.states[state_nr]['history']) == 0 and bridge_model.states[state_nr]['board'] == [-1, -1, -1,
                                                                                                         -1]:
        print(bridge_model.states[state_nr])
