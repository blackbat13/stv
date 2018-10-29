from simple_models.castle_model import *
from comparing_strats.strat_simpl import StrategyComparer
# from comparing_strats.graph_drawing import GraphDrawing
import time
import datetime

DEBUG = True
castle_sizes = [3, 1, 1]
castle_lifes = [3, 3, 3]
coalition = [0, 1, 2, 3]
results_file = open("strat_dfs_castles_results.txt", "a")
now = datetime.datetime.now()
print(now)
results_file.write(f'----------------Castles Model----------------\n')
results_file.write(f'{datetime.datetime.now()}\n')
results_file.write(f'Castles size: {castle_sizes}\nCastles life: {castle_lifes}\n')
start = time.process_time()
castle_model = CastleModel(castle_sizes=castle_sizes, castle_lifes=castle_lifes)
end = time.process_time()
results_file.write(f'Model generated in: {end - start} seconds\n')
no_states = len(castle_model.states)
print(f"Model have {no_states} states")
results_file.write(f'Number of states in the model: {no_states}\n')

winning_states = []

for i, state in enumerate(castle_model.model.states):
    if state['lifes'][2] == 0 and state['lifes'][0] > 0:
        if DEBUG:
            print(f'Winning state: {state}')
        winning_states.append(i)

if DEBUG:
    print(f'Number of winning states: {len(winning_states)}')

strategy_comparer = StrategyComparer(castle_model.model, ['idle', 'defend', 'attack 0', 'attack 1', 'attack 2'])
start = time.process_time()
(result, strategy) = strategy_comparer.generate_strategy_dfs(0, set(winning_states), coalition,
                                                             strategy_comparer.visited_states_h)
end = time.process_time()
strategy_defined_count = 0
for str in strategy:
    if str is not None:
        strategy_defined_count += 1
print(f'Strategy generation time: {end - start} seconds')
print(f'Strategy result: {result}')
print(f'Number of states where strategy is defined: {strategy_defined_count}')
print(strategy)

results_file.write(f'Coalition: {coalition}\n')
results_file.write(f'Strategy generation time: {end - start} seconds\n')
results_file.write(f'Strategy found: {result}\n')
results_file.write(f'Number of states where strategy is defined: {strategy_defined_count}\n')
results_file.write(f'Found strategy:\n{strategy}\n')
results_file.close()
