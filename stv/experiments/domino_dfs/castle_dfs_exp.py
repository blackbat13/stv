from stv.models.castle_model import *
from stv.comparing_strats.strategy_comparer import StrategyComparer
from typing import List
import time
import datetime


class CastleDfsExp:
    """
    Class for running experiments with DominoDFS on Castles model
    """

    def __init__(self, castle_sizes: List[int], castle_lifes: List[int], DEBUG: bool = False):
        """

        :param castle_sizes: list of numbers of workers for each castle
        :param castle_lifes: list of castle lifes
        :param DEBUG:
        """
        self.castle_sizes = castle_sizes
        self.castle_lifes = castle_lifes
        self.DEBUG = DEBUG
        self.results_file = None
        self.coalition = []
        self.castle_model = None
        self.winning_states = []
        self.strategy_comparer = None
        self.result = None
        self.strategy = None

    def run_experiments(self) -> None:
        """
        Runs experiments
        :return: None
        """
        print(datetime.datetime.now())
        self.results_file = open("strat_dfs_castles_results.txt", "a")
        self.write_file_header()
        self.coalition_a_b()
        self.generate_model()
        self.create_strategy_comparer()
        self.generate_winning_states()
        generation_time = self.generate_strategy()
        strategy_defined_count = self.count_strategy_defined()
        print(f'Strategy generation time: {generation_time} seconds')
        print(f'Strategy result: {self.result}')
        print(f'Number of states where strategy is defined: {strategy_defined_count}')
        print(self.strategy)
        self.results_file.write(f'Coalition: {self.coalition}\n')
        self.results_file.write(f'Strategy generation time: {generation_time} seconds\n')
        self.results_file.write(f'Strategy found: {self.result}\n')
        self.results_file.write(f'Number of states where strategy is defined: {strategy_defined_count}\n')
        self.results_file.write(f'Found strategy:\n{self.strategy}\n')
        self.results_file.close()

    def write_file_header(self):
        self.results_file.write(f'----------------Castles Model----------------\n')
        self.results_file.write(f'{datetime.datetime.now()}\n')
        self.results_file.write(f'Castles size: {self.castle_sizes}\nCastles life: {self.castle_lifes}\n')

    def coalition_a_b(self):
        self.coalition = []
        for i in range(0, self.castle_sizes[0] + self.castle_sizes[1]):
            self.coalition.append(i)

    def generate_model(self):
        start = time.process_time()
        self.castle_model = CastleModel(castle_sizes=self.castle_sizes, castles_life=self.castle_lifes)
        self.castle_model.model.to_subjective(self.coalition)
        end = time.process_time()
        self.results_file.write(f'Model generated in: {end - start} seconds\n')
        no_states = len(self.castle_model.states)
        print(f"Model have {no_states} states")
        self.results_file.write(f'Number of states in the model: {no_states}\n')

    def create_strategy_comparer(self):
        self.strategy_comparer = StrategyComparer(self.castle_model.model,
                                                  ['idle', 'defend', 'attack 0', 'attack 1', 'attack 2'])

    def generate_winning_states(self):
        self.winning_states = []
        for i, state in enumerate(self.castle_model.model.states):
            if state['defeated'][2]:
                self.winning_states.append(i)
                print(f'Winning state: {state}') if self.DEBUG else None

        print(f'Number of winning states: {len(self.winning_states)}') if self.DEBUG else None

    def generate_strategy(self):
        start = time.process_time()
        (self.result, self.strategy) = self.strategy_comparer.domino_dfs(self.castle_model.model.first_state_id,
                                                                         set(self.winning_states),
                                                                         self.coalition,
                                                                         self.strategy_comparer.visited_states_h)
        end = time.process_time()
        return end - start

    def count_strategy_defined(self):
        strategy_defined_count = 0
        for str in self.strategy:
            if str is not None:
                strategy_defined_count += 1

        return strategy_defined_count


if __name__ == "__main__":
    castle_dfs_test = CastleDfsExp(castle_sizes=[1, 1, 1], castle_lifes=[3, 3, 3], DEBUG=False)
    castle_dfs_test.run_experiments()
