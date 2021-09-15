from stv.models.model_generator import ModelGenerator
from typing import List
from enum import Enum
import itertools


class DiningCryptographers(ModelGenerator):
    class Coin(Enum):
        NONE = 0
        HEAD = 1
        TAIL = 2

    class NumberOfOdd(Enum):
        NONE = 0
        ODD = 1
        EVEN = 2

    def __init__(self, agents_count: int):
        super().__init__(agents_count=agents_count)

    def _generate_initial_states(self):
        available_coins = []
        for _ in range(0, self.agents_count):
            available_coins.append([self.Coin.HEAD, self.Coin.TAIL])

        for coins in itertools.product(*available_coins):
            for paying in range(-1, self.agents_count):
                state = {'number_of_odd': self.NumberOfOdd.NONE, 'coins': list(coins), 'paying': paying}
                self._add_state(state)

    def _generate_model(self):
        current_state_number = -1
        for state in self.model.states:
            current_state_number += 1
            if state['number_of_odd'] != self.NumberOfOdd.NONE:
                continue

            actions = []
            number = 0
            for agent_no in range(0, self.agents_count):
                if state['coins'][agent_no] == state['coins'][agent_no - 1]:
                    actions.append('say_equal')
                    number += 1
                else:
                    actions.append('say_different')

            if number % 2 == 0:
                number_of_odd = self.NumberOfOdd.EVEN
            else:
                number_of_odd = self.NumberOfOdd.ODD

            new_state = {'number_of_odd': number_of_odd, 'coins': state['coins'], 'paying': state['paying']}
            new_state_number = self._add_state(new_state)
            self.model.add_transition(current_state_number, new_state_number, actions)

    def _get_epistemic_state(self, state, agent_no):
        epistemic_coins = state['coins'][:]
        for i in range(0, self.agents_count):
            if i == agent_no or i == agent_no - 1:
                continue

            epistemic_coins[i] = self.Coin.NONE
        epistemic_state = {'number_of_odd': state['number_of_odd'], 'coins': epistemic_coins, 'paying': -2}
        return epistemic_state

    def _get_props_for_state(self, state: hash) -> List[str]:
        pass

    def get_actions(self):
        pass

    def get_props_list(self) -> List[str]:
        pass

    def get_winning_states(self, prop: str) -> List[int]:
        pass


if __name__ == "__main__":
    model = DiningCryptographers(3)
    model.generate()
