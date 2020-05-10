import stv.logics.atl.mv.mvatl_model as mvatl_model
import random
import copy

__author__ = 'Arthur Queffelec'


class PresidentModel:
    # TODO implement using ModelGenerator
    empty_deck = {"Two": 0, "As": 0,
                  "King": 0, "Queen": 0, "Jack": 0, "Ten": 0, "Nine": 0, "Eight": 0, "Seven": 0, "Six": 0, "Five": 0,
                  "Four": 0, "Three": 0}

    def __init__(self, number_of_players: int, number_of_decks: int, number_of_cards: int = 0):
        self.number_of_decks = number_of_decks
        self.number_of_players = number_of_players
        self.number_of_cards = number_of_cards
        self.deck = {"Two": 4, "As": 4,
                     "King": 4, "Queen": 4, "Jack": 4, "Ten": 4, "Nine": 4, "Eight": 4, "Seven": 4, "Six": 4, "Five": 4,
                     "Four": 4, "Three": 4}
        self.states = []
        self.players_cards = {}
        self.model = None

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
        self.model = mvatl_model.MvATLirModel(self.number_of_players, lattice)
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

    def get_epistemic_classes(self, agent):
        cs = []
        i = 0
        for s1 in self.states:
            c = []
            j = 0
            for s2 in self.states:
                if i == j:
                    continue
                if s1['Cards'][agent] == s2['Cards'][agent] and s1['Hierarchy'] == s2['Hierarchy'] and s1['Turn'] == s2[
                    'Turn'] and s1['Table'] == s2['Table']:
                    c.append(j)
                    print("State i-" + str(i) + " = " + str(s1))
                    print("State j-" + str(j) + " = " + str(s2))
                j += 1
            if len(c) > 0:
                c.append(i)
                cs.append(c)
            i += 1
        return cs

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
        actions = []
        for _ in range(0, self.number_of_players):
            actions.append('Wait')

        states_to_process = [(state, state_number)]
        while len(states_to_process) > 0:
            state = states_to_process[0][0]
            state_number = states_to_process[0][1]
            states_to_process.pop(0)

            if len(self.get_last_players(state['Cards'])) == 1:
                continue

            next_hier = self.get_next_hierarchy(state['Cards'])
            if next_hier == '-1':
                print("Game end")
                continue

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
                    child = {'Cards': copy.deepcopy(state['Cards']), 'Hierarchy': state['Hierarchy'][:],
                             'Turn': state['Turn'],
                             'Table': []}

                    new_actions = actions[:]
                    new_actions[state['Turn']] = 'Clear'
                    self.model.add_transition(state_number, len(self.states), new_actions)
                    self.states.append(child)
                    states_to_process.append((child, len(self.states) - 1))
                    continue

                nb_cards = len(state['Table'][count_pass])
                for card in state['Cards'][state['Turn']]:
                    if state['Cards'][state['Turn']][card] >= nb_cards:
                        if self.can_play(card, state['Table'][count_pass][0]):
                            child = {'Cards': copy.deepcopy(state['Cards']), 'Hierarchy': state['Hierarchy'][:],
                                     'Turn': state['Turn'],
                                     'Table': state['Table'][:]}
                            child['Cards'][child['Turn']][card] -= nb_cards
                            if self.get_nb_cards(child['Cards'][child['Turn']]) == 0:
                                child['Hierarchy'][child['Turn']] = next_hier
                            child['Table'].insert(0, [card] * nb_cards)
                            child['Turn'] = next_turn
                            self.states.append(child)
                            children += 1
                            new_actions = actions[:]
                            new_actions[state['Turn']] = card
                            self.model.add_transition(state_number, len(self.states) - 1, new_actions)
                            states_to_process.append((child, len(self.states) - 1))

                if children == 0:  # Cannot play so I pass
                    child = {'Cards': copy.deepcopy(state['Cards']), 'Hierarchy': state['Hierarchy'][:],
                             'Turn': next_turn,
                             'Table': state['Table'][:]}
                    child['Table'].insert(0, ['Pass'])
                    self.states.append(child)
                    new_actions = actions[:]
                    new_actions[state['Turn']] = 'Pass'
                    self.model.add_transition(state_number, len(self.states) - 1, new_actions)
                    states_to_process.append((child, len(self.states) - 1))
            else:
                for nb_cards in range(1, 4 * self.number_of_decks):
                    for card in state['Cards'][state['Turn']]:
                        if state['Cards'][state['Turn']][card] >= nb_cards:
                            child = {'Cards': copy.deepcopy(state['Cards']), 'Hierarchy': state['Hierarchy'][:],
                                     'Turn': state['Turn'],
                                     'Table': state['Table'][:]}
                            child['Cards'][child['Turn']][card] -= nb_cards
                            if self.get_nb_cards(child['Cards'][child['Turn']]) == 0:
                                child['Hierarchy'][child['Turn']] = next_hier
                            child['Table'].insert(0, [card] * nb_cards)
                            child['Turn'] = next_turn
                            self.states.append(child)
                            new_actions = actions[:]
                            new_actions[state['Turn']] = card
                            self.model.add_transition(state_number, len(self.states) - 1, new_actions)
                            states_to_process.append((child, len(self.states) - 1))
