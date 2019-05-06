from simple_models.model_generator import ModelGenerator
import itertools
import random


class BridgeModel(ModelGenerator):
    no_cards_available = 0
    no_end_cards = 0
    cards_available = []
    first_state = {}
    beginning_states_count = 0

    def __init__(self, no_cards_available, no_end_cards, first_state):
        super().__init__(no_agents=4)
        self.no_cards_available = no_cards_available
        self.no_end_cards = no_end_cards
        self.first_state = first_state
        self.generate_available_cards()
        print("Starting generating beginning states")
        self.generate_beginning_states()
        self.beginning_states_count = len(self.states)
        print("Generated", self.beginning_states_count, "beginning states")
        print("Starting generating rest of model")
        self.generate_model()
        print("Generated model with", len(self.states), "states")
        print("Starting preparing epistemic relation")
        self.prepare_epistemic_relation()
        print("Prepared epistemic relation")

    def generate_available_cards(self):
        card_number = 14
        for i in range(0, self.no_cards_available):
            for c in range(1, 5):
                self.cards_available.append(card_number * 10 + (5 - c))
            card_number -= 1

    def generate_beginning_states(self):
        enemy_hands = self.first_state['hands'][1][:] + self.first_state['hands'][3][:]
        for player2 in itertools.combinations(enemy_hands, self.no_end_cards):
            player4 = enemy_hands[:]
            for i in player2:
                player4.remove(i)
            new_hands = self.first_state['hands'][:]
            new_hands[1] = sorted(list(player2))
            new_hands[3] = sorted(list(player4))
            state = {'hands': new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                     'beginning': 0, 'history': self.first_state['history'], 'clock': 0, 'suit': -1}
            self.add_state(state)

    def generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            if state['next'] == state['beginning'] and state['clock'] == 0:
                if self.count_remaining_cards(state) == 0:
                    break

                self.generate_states_beginning_of_turn(current_state_number, state)
            elif state['clock'] == 4:
                self.generate_state_end_of_turn(current_state_number, state)
            else:
                self.generate_states_for_play(current_state_number, state)

    def generate_states_beginning_of_turn(self, current_state_number: int, state):
        for card_index, card in enumerate(state['hands'][state['next']]):
            if card == -1:
                continue

            new_state = self.new_state_after_play(state, card_index)
            agent_number = state['next']
            if agent_number == 2:
                agent_number = 0

            actions = [-1, -1, -1, -1]
            actions[agent_number] = card

            new_state_number = self.add_state(new_state)
            self.model.add_transition(current_state_number, new_state_number, actions)

    def generate_state_end_of_turn(self, current_state_number: int, state):
        winner = self.get_winner(state['beginning'], state['board'])
        new_lefts = state['lefts'][:]
        new_lefts[winner % 2] += 1
        new_state = {'hands': state['hands'], 'lefts': new_lefts, 'next': winner, 'board': [-1, -1, -1, -1],
                     'beginning': winner, 'history': state['history'], 'clock': 0,
                     'suit': -1}
        new_state_number = self.add_state(new_state)
        self.model.add_transition(current_state_number, new_state_number, [-1, -1, -1, -1])

    def generate_states_for_play(self, current_state_number: int, state):
        color = state['board'][state['beginning']] % 10
        have_color = False
        for card in state['hands'][state['next']]:
            if (card % 10) == color:
                have_color = True
                break

        for card_index, card in enumerate(state['hands'][state['next']]):
            if not ((not have_color) or (card % 10) == color) or card == -1:
                continue

            new_state = self.new_state_after_play(state, card_index)
            agent_number = state['next']
            if agent_number == 2:
                agent_number = 0

            actions = [-1, -1, -1, -1]
            actions[agent_number] = card

            new_state_number = self.add_state(new_state)
            self.model.add_transition(current_state_number, new_state_number, actions)

    def get_epistemic_state(self, state, agent_number: int) -> hash:
        if agent_number != 0:
            return {}
        epistemic_hands = state['hands'][:]
        epistemic_hands[1] = self.keep_values_in_list(epistemic_hands[1], -1)
        epistemic_hands[3] = self.keep_values_in_list(epistemic_hands[3], -1)
        epistemic_state = {'hands': epistemic_hands, 'lefts': state['lefts'], 'next': state['next'],
                           'board': state['board'], 'beginning': state['beginning'], 'history': state['history'],
                           'clock': state['clock'], 'suit': state['suit']}
        return epistemic_state

    def get_model(self):
        return self.model

    def get_actions(self):
        actions = [-1]
        for i in self.cards_available:
            actions.append(i)

        return [actions, actions[:], actions[:]]

    @staticmethod
    def new_state_after_play(state, card_index):
        card = state['hands'][state['next']][card_index]
        new_board = BridgeModel.new_board_after_play(state, card)
        new_history = BridgeModel.new_history_after_play(state, card)
        new_next = (state['next'] + 1) % 4
        new_clock = state['clock'] + 1
        new_hands = BridgeModel.copy_hands(state['hands'])
        new_hands[state['next']][card_index] = -1
        new_suit = BridgeModel.new_suit(state, card)
        new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                     'suit': new_suit}
        return new_state

    @staticmethod
    def new_suit(state, card):
        if state['next'] == state['beginning']:
            return card % 10
        else:
            return state['suit']

    @staticmethod
    def new_board_after_play(state, card):
        new_board = state['board'][:]
        new_board[state['next']] = card
        return new_board

    @staticmethod
    def new_history_after_play(state, card):
        new_history = state['history'][:]
        new_history.append(card)
        new_history = sorted(new_history)
        return new_history

    @staticmethod
    def count_remaining_cards(state):
        remaining_cards_count = 0
        for card in state['hands'][state['next']]:
            if card != -1:
                remaining_cards_count += 1

        return remaining_cards_count

    @staticmethod
    def get_winner(beginning, board):
        cards = []
        for i in range(0, 4):
            cards.append(board[(beginning + i) % 4])

        winner = beginning
        winning_card = cards[0]
        color = cards[0] % 10

        for i in range(1, 4):
            if cards[i] % 10 == color and cards[i] > winning_card:
                winning_card = cards[i]
                winner = (beginning + i) % 4

        return winner

    @staticmethod
    def copy_hands(hands):
        new_hands = [[], [], [], []]
        for i in range(0, 4):
            new_hands[i] = hands[i][:]

        return new_hands

    @staticmethod
    def keep_values_in_list(the_list, val):
        return [value for value in the_list if value == val]

    @staticmethod
    def get_state_string(state):
        state_str = ' '.join(str(state[e]) for e in state)
        return state_str

    @staticmethod
    def generate_random_hands(no_cards_available, no_cards_in_hand):
        array = []
        used = []
        card_numbers = []
        for i in range(14, 0, -1):
            for j in range(4, 0, -1):
                card_numbers.append(i * 10 + j)

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

    @staticmethod
    def generate_readable_cards_array():
        card_names = ["Ace", "King", "Queen", "Jack", "ten", "nine", "eight", "seven", "six", "five", "four", "three",
                      "two"]
        card_colors = ["Spade", "Heart", "Diamond", "Club"]
        cards = []
        for name in card_names:
            for color in card_colors:
                cards.append(name + color)

        return cards

    @staticmethod
    def generate_cards_dictionary():
        cards = BridgeModel.generate_readable_cards_array()
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

    @staticmethod
    def hands_to_readable_hands(hands):
        cards_dictionary = BridgeModel.generate_cards_dictionary()
        readable_hands = []
        for hand in hands:
            readable_hand = []
            for card_number in hand:
                readable_hand.append(cards_dictionary[card_number])
            readable_hands.append(readable_hand)

        return readable_hands

    @staticmethod
    def card_to_readable(card: int):
        cards_dictionary = BridgeModel.generate_cards_dictionary()
        if card == -1:
            return "Wait"
        return cards_dictionary[card]

    @staticmethod
    def board_to_readable(board):
        cards_dictionary = BridgeModel.generate_cards_dictionary()
        readable_board = []
        for card in board:
            if card == -1:
                readable_board.append("Empty")
            else:
                readable_board.append(cards_dictionary[card])

        return readable_board
