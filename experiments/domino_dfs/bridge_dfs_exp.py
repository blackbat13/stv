from simple_models.bridge_model import *
from comparing_strats.strat_simpl import StrategyComparer
# from comparing_strats.graph_drawing import GraphDrawing
import time
import datetime


class BridgeDfsExp:
    def __init__(self, n: int, DEBUG: bool = False):
        self.n = n
        self.DEBUG = DEBUG
        self.hands = BridgeModel.generate_random_hands(n, n)
        self.model = None
        self.results_file = None

    def run_experiments(self):
        self.open_results_file()
        self.write_file_header()
        self.generate_model()

        winning_states = self.model.get_winning_states('ns_win')

        if self.DEBUG:
            print(f'Number of winning states: {len(winning_states)}')

        strategy_comparer = StrategyComparer(self.model.model, [])
        start = time.process_time()
        (result, strategy) = strategy_comparer.domino_dfs(0, set(winning_states), [0], strategy_comparer.basic_h)
        end = time.process_time()
        self.results_file.write(f'Strategy generated in: {end - start} seconds\n')
        print(f'Strategy result: {result}')
        self.results_file.write(f'Strategy found: {result}\n')
        print(strategy)
        self.results_file.write(f'Found strategy:\n{strategy}\n')

        strategy_defined_count = 0
        for str in strategy:
            if str is not None:
                strategy_defined_count += 1

        self.results_file.write(f'Number of states where strategy is defined: {strategy_defined_count}\n')

        for index, value in enumerate(strategy):
            if value is not None:
                print(f"{index}: {BridgeModel.card_to_readable(int(value[0]))}")
                print(
                    f"{BridgeModel.board_to_readable(self.model.model.states[index]['board'])}: {BridgeModel.card_to_readable(value[0])}")

        self.results_file.close()
        # graphDrawing = GraphDrawing(bridge_model.model, strategy)
        # graphDrawing.draw()

    def open_results_file(self):
        self.results_file = open("strat_dfs_bridge_results.txt", "a")

    def write_file_header(self):
        self.results_file.write(f'----------------Bridge Model----------------\n')
        self.results_file.write(f'{datetime.datetime.now()}\n')
        self.results_file.write(
            f'Number of cards: {self.n}\nInitial hands: {BridgeModel.hands_to_readable_hands(self.hands)}\n')

    def generate_model(self):
        start = time.process_time()
        self.model = BridgeModel(no_cards_available=self.n, no_end_cards=self.n,
                                 first_state={'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                              'hands': self.hands, 'next': 0, 'history': [],
                                              'beginning': 0, 'clock': 0, 'suit': -1})
        self.model.generate()
        end = time.process_time()
        self.results_file.write(f'Model generated in: {end - start} seconds\n')
        no_states = len(self.model.model.states)
        self.results_file.write(f'Number of states in the model: {no_states}\n')
        print(f"Model have {no_states} states") if self.DEBUG else None

# bridge_dfs_exp = BridgeDfsExp(1, True)
# bridge_dfs_exp.run_experiments()
