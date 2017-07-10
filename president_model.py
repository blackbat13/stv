import random
import copy
import mvatl_model


class PresidentModel:
    number_of_players = 3
    number_of_decks = 1
    number_of_cards = 0
    model = None
    states = []
    players_cards = {}
    deck = {"Two": 4, "As": 4,
            "King": 4, "Queen":4, "Jack":4, "Ten":4, "Nine":4, "Eight": 4, "Seven":4, "Six":4, "Five":4, "Four":4, "Three":4}
    empty_deck = {"Two": 0, "As": 0,
                  "King": 0, "Queen":0, "Jack":0, "Ten":0, "Nine":0, "Eight": 0, "Seven":0, "Six":0, "Five":0, "Four":0, "Three":0}

    def __init__(self, number_of_players, number_of_decks, number_of_cards=0):
        self.number_of_decks = number_of_decks
        self.number_of_players = number_of_players
        self.number_of_cards = number_of_cards

    def add_actions(self):
        for key in self.deck:
            for agent in range(0, self.number_of_players):
                self.model.add_action(agent, key)

        for agent in range(0, self.number_of_players):
            self.model.add_action(agent, 'Wait')
            self.model.add_action(agent, 'Pass')
            self.model.add_action(agent, 'Clear')

    def pop_card(self):
        ok = False
        for v in self.deck.values():
            if v > 0:
                ok = True
                break
        if not ok:
            return "Error"

        rand = random.randint(0, len(self.deck) - 1)
        keys = list(self.deck.keys())
        while self.deck[keys[rand]] == 0:
            rand = random.randint(0, len(self.deck) - 1)

        self.deck[keys[rand]] -= 1
        return keys[rand]

    def deal_cards(self):
        print("Cards by players : " + str(self.number_cards_players()))
        for n in range(0, self.number_of_players):
            self.players_cards[n] = copy.deepcopy(self.empty_deck)
            for _ in range(0, int(self.number_cards_players())):
                self.players_cards[n][self.pop_card()] += 1

    def number_cards_players(self):
        if self.number_of_cards == 0:
            return ((self.number_of_decks * len(self.deck) * 4) - (
                (self.number_of_decks * len(self.deck) * 4) % self.number_of_players)) / self.number_of_players
        else:
            return self.number_of_cards

    def create_mvatl_model(self):
        # TODO: Approx number of states
        if self.number_of_players < 5:
            lattice = mvatl_model.QBAlgebra('t', 'b', [('b', 'n'), ('n', 't')])
        else:
            lattice = mvatl_model.QBAlgebra('t', 'b', [('b', 'd'), ('d', 'n'), ('n', 'p'), ('p', 't')])
        self.model = mvatl_model.MvATLModel(self.number_of_players, 10000, lattice)
        self.add_actions()

    def generate_model(self):
        self.deal_cards()
        print("Players cards :" + str(self.players_cards))
        cards = []
        hier = []
        for n in range(0, self.number_of_players):
            cards.insert(len(cards), self.players_cards[n])
            hier.insert(0, 'n')
        init_state = {'Cards': cards, 'Hierarchy': hier, 'Turn': 0, 'Table': []}
        self.states.append(init_state)
        self.generate_children(init_state, 0)

    def get_nb_cards(self, deck):
        nb = 0
        for card in deck:
            nb += deck[card]

        return nb

    def get_next_hierarchy(self, decks):
        nb = 0
        for deck in decks:
            if self.get_nb_cards(deck) == 0:
                nb += 1
        if nb == self.number_of_players:
            return '-1'
        if nb == 0:
            return self.model.lattice.top
        if self.number_of_players > 4:
            if nb == 1:
                return 'p'
            neutral = self.number_of_players - 4
            if nb - (neutral + 2) <= 0:
                return 'n'
            return self.model.lattice.bottom
        else:
            if nb == 1:
                return 'p'
            neutral = self.number_of_players - 2
            if nb - (neutral + 1) <= 0:
                return 'n'
            if nb - (neutral + 1) == 1:
                return 'd'
            return self.model.lattice.bottom

    def get_last_players(self, decks):
        l = []
        n = 0
        for deck in decks:
            if self.get_nb_cards(deck) > 0:
                l.insert(0, n)
            n += 1
        return l

    def get_next_turn(self, current, last):
        turn = (current + 1) % self.number_of_players
        while turn not in last:
            turn = (turn + 1) % self.number_of_players
        return turn

    def can_play(self, card, last_card):
        if card == last_card:
            return False
        if list(self.empty_deck.keys()).index(card, 0) < list(self.empty_deck.keys()).index(last_card, 0):
            return True
        return False

    def generate_children(self, state, state_number):
        if len(self.get_last_players(state['Cards'])) == 1:
            return

        next_hier = self.get_next_hierarchy(state['Cards'])
        if next_hier == '-1':
            print("Game end")
            return

        actions = []
        for n in range(0, self.number_of_players):
            actions.insert(n, 'Wait')

        next_turn = self.get_next_turn(state['Turn'], self.get_last_players(state['Cards']))
        children = 0
        # I do not have the hand so I need to follow
        if len(state['Table']) > 0:
            count_pass = 0
            for p in state['Table']:
                if p == ['Pass']:
                    count_pass += 1
                else:
                    break

            # I take the hand and clear the board
            if count_pass == len(self.get_last_players(state['Cards'])) - 1:
                child = copy.deepcopy(state)
                child['Table'] = []
                new_actions = copy.deepcopy(actions)
                new_actions[state['Turn']] = 'Clear'
                self.model.add_transition(state_number, len(self.states), new_actions)
                print_create_for_state(len(self.states), child)
                self.states.append(child)
                self.generate_children(child, len(self.states) - 1)
                return

            nb_cards = len(state['Table'][count_pass])
            for card in state['Cards'][state['Turn']]:
                if state['Cards'][state['Turn']][card] >= nb_cards:
                    if self.can_play(card, state['Table'][count_pass][0]):
                        child = copy.deepcopy(state)
                        child['Cards'][child['Turn']][card] -= nb_cards
                        if self.get_nb_cards(child['Cards'][child['Turn']]) == 0:
                            child['Hierarchy'][child['Turn']] = next_hier
                        child['Table'].insert(0, [card] * nb_cards)
                        child['Turn'] = next_turn
                        self.states.append(child)
                        children += 1
                        new_actions = copy.deepcopy(actions)
                        new_actions[state['Turn']] = card
                        self.model.add_transition(state_number, len(self.states) - 1, new_actions)
                        print_create_for_state(len(self.states) - 1, child)
                        self.generate_children(child, len(self.states) - 1)

            if children == 0:  # Cannot play so I pass
                child = copy.deepcopy(state)
                child['Turn'] = next_turn
                child['Table'].insert(0, ['Pass'])
                self.states.append(child)
                new_actions = copy.deepcopy(actions)
                new_actions[state['Turn']] = 'Pass'
                self.model.add_transition(state_number, len(self.states) - 1, new_actions)
                print_create_for_state(len(self.states) - 1, child)
                self.generate_children(child, len(self.states) - 1)
        else:
            for nb_cards in range(1, 4 * self.number_of_decks):
                for card in state['Cards'][state['Turn']]:
                    if state['Cards'][state['Turn']][card] >= nb_cards:
                        child = copy.deepcopy(state)
                        child['Cards'][child['Turn']][card] -= nb_cards
                        if self.get_nb_cards(child['Cards'][child['Turn']]) == 0:
                            child['Hierarchy'][child['Turn']] = next_hier
                        child['Table'].insert(0, [card] * nb_cards)
                        child['Turn'] = next_turn
                        self.states.append(child)
                        new_actions = copy.deepcopy(actions)
                        new_actions[state['Turn']] = card
                        self.model.add_transition(state_number, len(self.states) - 1, new_actions)
                        print_create_for_state(len(self.states) - 1, child)
                        self.generate_children(child, len(self.states) - 1)


def print_create_for_state(state_number, state):
    return
    # msg = "CREATE (S" + str(state_number) + ":State { "
    # i = 1
    # TODO: Are they all prop ?
    # for prop in state:
    #    if isinstance( state[prop], int ):
    #        msg +=  "[" + prop + "]" + "=" + str(state[prop]) + " "
    #    elif prop == 'Table' or prop == 'Hierarchy':
    #        msg +=  "[" + prop + "]" + "=" + str(state[prop]) + " "
    #    elif len(state[prop]) > 1:
    #        for val in state[prop]:
    #            msg += "[" + prop + str(i) + "]" + " = " + str(val) + " "
    #            i += 1
    #        i = 1
    #    else:
    #        msg += "[" + prop + "]" + " = " + str(state[prop]) + " "
    # msg += "]}"
    # print(msg)

test = PresidentModel(3, 1, 4)
test.create_mvatl_model()
test.generate_model()
print(f'Number of states: {len(test.states)}')
test.model.states = test.states
test.model.walk_perfect_information(0)
# print(len(test.states))
# i = 0
# print()
# print("#states")
# for s in test.states:
#    print("s"+str(i))
#    i+=1
# print("#initial")
# print("s0")
# print("#accepting")
# print("#alphabet")
# print("Wait1\nWait2\nWait3\nPass1\nPass2\nPass3\nClear1\nClear2\nClear3\nTwo1\nAs1\nKing1\nTwo2\nAs2\nKing2\nTwo3\nAs3\nKing3")
# print("#transitions")
# i = 0
# for s1 in test.model.transitions:
#    for t in s1:
#        s2 = t['nextState']
#        j = 1
#        for a in t['actions']:
#            print("s"+str(i)+":"+a+str(j)+">s"+str(s2))
#            j +=1
#    i+=1
# print(test.model.transitions)
