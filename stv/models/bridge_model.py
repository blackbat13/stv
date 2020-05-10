from stv.models.model_generator import ModelGenerator
from typing import List, Set
import itertools
import random


class BridgeModel(ModelGenerator):

    def __init__(self, no_cards_available: int, no_end_cards: int, first_state: hash):
        super().__init__(agents_count=4)
        self._no_cards_available = no_cards_available
        self._no_end_cards = no_end_cards
        self._first_state = first_state
        self._initial_states_count = 0
        self._cards_available = []

    @property
    def initial_states_count(self) -> int:
        return self._initial_states_count

    def generate(self):
        self._generate_available_cards()
        self._generate_initial_states()
        self._initial_states_count = len(self.states)
        self._generate_model()
        self._prepare_epistemic_relation()

    def _generate_available_cards(self):
        card_number = 14
        for i in range(0, self._no_cards_available):
            for c in range(1, 5):
                self._cards_available.append(card_number * 10 + (5 - c))
            card_number -= 1

    def _generate_initial_states(self):
        enemy_hands = self._first_state['hands'][1][:] + self._first_state['hands'][3][:]
        for player2 in itertools.combinations(enemy_hands, self._no_end_cards):
            player4 = enemy_hands[:]
            for i in player2:
                player4.remove(i)
            new_hands = self._first_state['hands'][:]
            new_hands[1] = sorted(list(player2))
            new_hands[3] = sorted(list(player4))
            state = {'hands': new_hands, 'lefts': [0, 0], 'next': 0, 'board': [-1, -1, -1, -1],
                     'beginning': 0, 'history': self._first_state['history'], 'clock': 0, 'suit': -1}
            self._add_state(state)

    def _generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            if state['next'] == state['beginning'] and state['clock'] == 0:
                if self._count_remaining_cards(state) == 0:
                    break

                self._generate_states_beginning_of_turn(current_state_number, state)
            elif state['clock'] == 4:
                self._generate_state_end_of_turn(current_state_number, state)
            else:
                self._generate_states_for_play(current_state_number, state)

    def _generate_states_beginning_of_turn(self, current_state_number: int, state):
        for card_index, card in enumerate(state['hands'][state['next']]):
            if card == -1:
                continue

            new_state = self._new_state_after_play(state, card_index)
            agent_number = state['next']
            if agent_number == 2:
                agent_number = 0

            actions = [-1, -1, -1, -1]
            actions[agent_number] = card

            new_state_number = self._add_state(new_state)
            self.model.add_transition(current_state_number, new_state_number, actions)

    def _generate_state_end_of_turn(self, current_state_number: int, state):
        winner = self._get_winner(state['beginning'], state['board'])
        new_lefts = state['lefts'][:]
        new_lefts[winner % 2] += 1
        new_state = {'hands': state['hands'], 'lefts': new_lefts, 'next': winner, 'board': [-1, -1, -1, -1],
                     'beginning': winner, 'history': state['history'], 'clock': 0,
                     'suit': -1}
        new_state_number = self._add_state(new_state)
        self.model.add_transition(current_state_number, new_state_number, [-1, -1, -1, -1])

    def _generate_states_for_play(self, current_state_number: int, state):
        color = state['board'][state['beginning']] % 10
        have_color = False
        for card in state['hands'][state['next']]:
            if (card % 10) == color:
                have_color = True
                break

        for card_index, card in enumerate(state['hands'][state['next']]):
            if not ((not have_color) or (card % 10) == color) or card == -1:
                continue

            new_state = self._new_state_after_play(state, card_index)
            agent_number = state['next']
            if agent_number == 2:
                agent_number = 0

            actions = [-1, -1, -1, -1]
            actions[agent_number] = card

            new_state_number = self._add_state(new_state)
            self.model.add_transition(current_state_number, new_state_number, actions)

    def _get_epistemic_state(self, state, agent_id: int) -> hash:
        if agent_id != 0:
            return {}
        epistemic_hands = state['hands'][:]
        epistemic_hands[1] = self._keep_values_in_list(epistemic_hands[1], -1)
        epistemic_hands[3] = self._keep_values_in_list(epistemic_hands[3], -1)
        epistemic_state = {'hands': epistemic_hands, 'lefts': state['lefts'], 'next': state['next'],
                           'board': state['board'], 'beginning': state['beginning'], 'history': state['history'],
                           'clock': state['clock'], 'suit': state['suit']}
        return epistemic_state

    def get_actions(self):
        actions = [-1]
        for i in self._cards_available:
            actions.append(i)

        return [actions, actions[:], actions[:]]

    def get_props_list(self) -> List[str]:
        return ["finish", "ns_win", "ew_win", "draw"]

    def get_winning_states(self, prop: str) -> Set[int]:
        winning = set()
        state_id = -1
        for state in self.states:
            state_id += 1
            if prop in state["props"]:
                winning.add(state_id)
        return winning

    def _get_props_for_state(self, state: hash) -> List[str]:
        props = []
        if state['lefts'][0] + state['lefts'][1] == self._no_end_cards:
            props.append("finish")
            if state['lefts'][0] > state['lefts'][1]:
                props.append("ns_win")
            elif state['lefts'][0] < state['lefts'][1]:
                props.append("ew_win")
            else:
                props.append("draw")

        return props

    def transitions_to_readable(self):
        for state_id in range(0, len(self.model.graph)):
            for transition in self.model.graph[state_id]:
                for act_id in range(0, len(transition.actions)):
                    transition.actions[act_id] = self.card_to_readable(transition.actions[act_id])

    @staticmethod
    def _new_state_after_play(state, card_index):
        card = state['hands'][state['next']][card_index]
        new_board = BridgeModel._new_board_after_play(state, card)
        new_history = BridgeModel._new_history_after_play(state, card)
        new_next = (state['next'] + 1) % 4
        new_clock = state['clock'] + 1
        new_hands = BridgeModel._copy_hands(state['hands'])
        new_hands[state['next']][card_index] = -1
        new_suit = BridgeModel._new_suit(state, card)
        new_state = {'hands': new_hands, 'lefts': state['lefts'], 'next': new_next, 'board': new_board,
                     'beginning': state['beginning'], 'history': new_history, 'clock': new_clock,
                     'suit': new_suit}
        return new_state

    @staticmethod
    def _new_suit(state, card):
        if state['next'] == state['beginning']:
            return card % 10

        return state['suit']

    @staticmethod
    def _new_board_after_play(state, card):
        new_board = state['board'][:]
        new_board[state['next']] = card
        return new_board

    @staticmethod
    def _new_history_after_play(state, card):
        new_history = state['history'][:]
        new_history.append(card)
        new_history = sorted(new_history)
        return new_history

    @staticmethod
    def _count_remaining_cards(state):
        remaining_cards_count = 0
        for card in state['hands'][state['next']]:
            if card != -1:
                remaining_cards_count += 1

        return remaining_cards_count

    @staticmethod
    def _get_winner(beginning, board):
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
    def _copy_hands(hands):
        new_hands = [[], [], [], []]
        for i in range(0, 4):
            new_hands[i] = hands[i][:]

        return new_hands

    @staticmethod
    def _keep_values_in_list(the_list, val):
        return [value for value in the_list if value == val]

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
    def _generate_cards_dictionary():
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
        cards_dictionary = BridgeModel._generate_cards_dictionary()
        readable_hands = []
        for hand in hands:
            readable_hand = []
            for card_number in hand:
                readable_hand.append(cards_dictionary[card_number])
            readable_hands.append(readable_hand)

        return readable_hands

    @staticmethod
    def card_to_readable(card: int):
        cards_dictionary = BridgeModel._generate_cards_dictionary()
        if card == -1:
            return "Wait"
        return cards_dictionary[card]

    @staticmethod
    def board_to_readable(board):
        cards_dictionary = BridgeModel._generate_cards_dictionary()
        readable_board = []
        for card in board:
            if card == -1:
                readable_board.append("Empty")
            else:
                readable_board.append(cards_dictionary[card])

        return readable_board


if __name__ == "__main__":
    n = 2
    model = BridgeModel(n, n, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                               'hands': BridgeModel.generate_random_hands(n, n), 'next': 0,
                               'history': [],
                               'beginning': 0, 'clock': 0, 'suit': -1})
    model.generate()
