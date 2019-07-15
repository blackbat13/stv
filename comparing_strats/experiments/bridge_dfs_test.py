from simple_models.bridge_model import *
from comparing_strats.strat_simpl import StrategyComparer
# from comparing_strats.graph_drawing import GraphDrawing
import time
import datetime

DEBUG = True
results_file = open("strat_dfs_bridge_results.txt", "a")
results_file.write(f'----------------Bridge Model----------------\n')
results_file.write(f'{datetime.datetime.now()}\n')
n = 2
hands = BridgeModel.generate_random_hands(n, n)
print(BridgeModel.hands_to_readable_hands(hands))
results_file.write(f'Number of cards: {n}\nInitial hands: {BridgeModel.hands_to_readable_hands(hands)}\n')
start = time.process_time()
bridge_model = BridgeModel(no_cards_available=n, no_end_cards=n, first_state={'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                          'hands': hands, 'next': 0, 'history': [],
                                          'beginning': 0, 'clock': 0, 'suit': -1})
bridge_model.generate()
end = time.process_time()
results_file.write(f'Model generated in: {end - start} seconds\n')
no_states = len(bridge_model.model.states)
print(f"Model have {no_states} states")
results_file.write(f'Number of states in the model: {no_states}\n')

winning_states = bridge_model.get_winning_states('ns_win')

if DEBUG:
    print(f'Number of winning states: {len(winning_states)}')

strategy_comparer = StrategyComparer(bridge_model.model, [])
start = time.process_time()
(result, strategy) = strategy_comparer.generate_strategy_dfs(0, set(winning_states), [0], strategy_comparer.basic_h)
end = time.process_time()
results_file.write(f'Strategy generated in: {end - start} seconds\n')
print(f'Strategy result: {result}')
results_file.write(f'Strategy found: {result}\n')
print(strategy)
results_file.write(f'Found strategy:\n{strategy}\n')

strategy_defined_count = 0
for str in strategy:
    if str is not None:
        strategy_defined_count += 1

results_file.write(f'Number of states where strategy is defined: {strategy_defined_count}\n')

for index, value in enumerate(strategy):
    if value is not None:
        print(f"{index}: {BridgeModel.card_to_readable(int(value[0]))}")
        print(f"{BridgeModel.board_to_readable(bridge_model.model.states[index]['board'])}: {BridgeModel.card_to_readable(value[0])}")

results_file.close()
# graphDrawing = GraphDrawing(bridge_model.model, strategy)
# graphDrawing.draw()
