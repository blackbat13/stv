from atl_model import *
import time
import pickle
import gc

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
    bridge_model = ATLModel(3, 3445920)
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
    for cards in itertools.product(*pr):
        if cards[0] != cards[1]:
            bridge_model.add_action(0, [cards[0], cards[1]])
    states = []
    states_dictionary = {}
    state_number = 0
    print("Start creating beginning states of model")
    # gc.disable()
    start = time.clock()
    for combination in itertools.combinations(cards_available, no_end_cards * 4):
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
                    state = {'hands': hands, 'lefts': [0, 0, 0, 0], 'next': 0}
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
        if len(state['hands'][0]) == 0:
            break
        for card1 in state['hands'][state['next']]:
            played = [0, 0, 0, 0]
            played[state['next']] = card1
            color = card1 % 10
            player1 = state['next']
            player2 = (player1 + 1) % 4
            player3 = (player2 + 1) % 4
            player4 = (player3 + 1) % 4
            have_color2 = False
            for card2 in state['hands'][player2]:
                if (card2 % 10) == color:
                    have_color2 = True
                    break
            have_color3 = False
            for card3 in state['hands'][player3]:
                if (card3 % 10) == color:
                    have_color3 = True
                    break
            have_color4 = False
            for card4 in state['hands'][player4]:
                if (card4 % 10) == color:
                    have_color4 = True
                    break
            for card2 in state['hands'][player2]:
                if not ((not have_color2) or (card2 % 10) == color):
                    continue
                played[player2] = card2
                for card3 in state['hands'][player3]:
                    if not ((not have_color3) or (card3 % 10) == color):
                        continue
                    played[player3] = card3
                    for card4 in state['hands'][player4]:
                        if not ((not have_color4) or (card4 % 10) == color):
                            continue
                        played[player4] = card4
                        winner = player1
                        winner_card = card1
                        if have_color2 and card2 > winner_card:
                            winner = player2
                            winner_card = card2
                        if have_color3 and card3 > winner_card:
                            winner = player3
                            winner_card = card3
                        if have_color4 and card4 > winner_card:
                            winner = player4
                            winner_card = card4
                        new_lefts = state['lefts'][:]
                        new_lefts[winner] += 1
                        new_hands = [[], [], [], []]
                        new_hands[0] = state['hands'][0][:]
                        new_hands[1] = state['hands'][1][:]
                        new_hands[2] = state['hands'][2][:]
                        new_hands[3] = state['hands'][3][:]
                        new_hands[player1].remove(card1)
                        new_hands[player2].remove(card2)
                        new_hands[player3].remove(card3)
                        new_hands[player4].remove(card4)
                        new_next = winner
                        action = {0: [played[0], played[1]], 1: played[2], 2: played[3]}
                        new_state = {'hands': new_hands, 'lefts': new_lefts, 'next': new_next}
                        new_state_str = ' '.join(str(new_state[e]) for e in new_state)
                        new_state_number = 0
                        if new_state_str not in states_dictionary:
                            states_dictionary[new_state_str] = state_number
                            new_state_number = state_number
                            states.append(new_state)
                            state_number += 1
                        else:
                            new_state_number = states_dictionary[new_state_str]

                        trans += 1
                        # transitions.append(
                        #     {'from_state': current_state_number, 'to_state': new_state_number, 'action': action})
                        # bridge_model.add_transition(current_state_number, new_state_number, action)

    end = time.clock()
    # gc.enable()
    print("Created rest of model in", end - start, "s")

    print("Created model have", len(states), "states")
    print("Created model have", trans, "transitions")

    # with open('state_array_3_2.pkl', 'wb') as output:
    #     pickle.dump(states, output, pickle.HIGHEST_PROTOCOL)
    #
    # with open('state_dictionary_3_2.pkl', 'wb') as output:
    #     pickle.dump(states_dictionary, output, pickle.HIGHEST_PROTOCOL)

    # with open('transitions_array_3_2.pkl', 'wb') as output:
    #     pickle.dump(transitions, output, pickle.HIGHEST_PROTOCOL)

    print("Begin defining indistuiginshable relation")
    # gc.disable()
    start = time.clock()
    bridge_model.states = states
    same_relation = [[] for i in itertools.repeat(None, len(states))]
    for i in range(0, len(states)):
        for j in range(i + 1, len(states)):
            state_a = states[i]
            state_b = states[j]
            if len(state_a['hands'][0]) != len(state_b['hands'][0]):
                break
            if state_a['hands'][0] == state_b['hands'][0] and state_a['hands'][1] == state_b['hands'][1] and state_a[
                'lefts'] == state_b['lefts']:
                # bridge_model.set_same_state(0, i, j)
                same_relation[i].append(j)
                same_relation[j].append(i)
    end = time.clock()
    # gc.enable()
    print("Created indistuiginshable relation in", end - start, "s")
    with open('same_array_3_2.pkl', 'wb') as output:
        pickle.dump(same_relation, output, pickle.HIGHEST_PROTOCOL)

    return bridge_model


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

# bridge_model = generate_bridge_model(3, 2)
bridge_model = read_bridge_model(3)
print("Ilość stanów ", len(bridge_model.states))

winning_states = []
i = -1
for state in bridge_model.states:
    i += 1
    if len(state['hands'][0]) == 0 and state['lefts'][0] >= 1:
        winning_states.append(i)

start = time.clock()
wynik = bridge_model.minimum_formula_multiple_agents_and_states([0], winning_states)
end = time.clock()
print("Time:", end - start, "s")
print("Ilość spełniających stanów ", len(wynik))
for state_nr in wynik:
    print(bridge_model.states[state_nr])
