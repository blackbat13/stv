from stv.models.bridge_model import *
from stv.comparing_strats.strategy_comparer import StrategyComparer
from stv.experiments.aexperiment import AExperiment
from stv.tools.list_tools import ListTools
import time
import datetime


class BridgeDfsExp(AExperiment):
    def __init__(self, n: int, DEBUG: bool = False):
        super().__init__(DEBUG)
        self.__n = n
        self.__hands = BridgeModel.generate_random_hands(n, n)
        self._file_name = "strat_dfs_bridge_results.txt"
        self.__strategy = None

    def _write_file_header(self):
        self._results_file.write(f'----------------Bridge Model----------------\n')
        self._results_file.write(f'{datetime.datetime.now()}\n')
        self._results_file.write(
            f'Number of cards: {self.__n}\nInitial hands: {BridgeModel.hands_to_readable_hands(self.__hands)}\n')

    def _generate_model(self):
        start = time.process_time()
        self._model = BridgeModel(no_cards_available=self.__n, no_end_cards=self.__n,
                                  first_state={'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                               'hands': self.__hands, 'next': 0, 'history': [],
                                               'beginning': 0, 'clock': 0, 'suit': -1})
        self._model.generate()
        end = time.process_time()
        self._results_file.write(f'Model generated in: {end - start} seconds\n')
        no_states = len(self._model.model.states)
        self._results_file.write(f'Number of states in the model: {no_states}\n')
        print(f"Model have {no_states} states") if self._DEBUG else None

    def _run_mc(self):
        winning_states = self._model.get_winning_states('ns_win')
        if self._DEBUG:
            print(f'Number of winning states: {len(winning_states)}')
        strategy_comparer = StrategyComparer(self._model.model, [])
        start = time.process_time()
        (result, self.__strategy) = strategy_comparer.domino_dfs(0, set(winning_states), [0], strategy_comparer.basic_h)
        end = time.process_time()
        self._results_file.write(f'Strategy generated in: {end - start} seconds\n')
        self._results_file.write(f'Strategy found: {result}\n')
        self._results_file.write(f'Found strategy:\n{self.__strategy}\n')
        if self._DEBUG:
            print(f'Strategy result: {result}')
            print(self.__strategy)

    def _write_result(self):
        strategy_defined_count = ListTools.count_not_none(self.__strategy)
        self._results_file.write(f'Number of states where strategy is defined: {strategy_defined_count}\n')
        if self._DEBUG:
            for index, value in enumerate(self.__strategy):
                if value is not None:
                    print(f"{index}: {BridgeModel.card_to_readable(int(value[0]))}")
                    print(
                        f"{BridgeModel.board_to_readable(self._model.model.states[index]['board'])}: {BridgeModel.card_to_readable(value[0])}")


if __name__ == "__main__":
    bridge_dfs_exp = BridgeDfsExp(1, True)
    bridge_dfs_exp.run_experiments()
