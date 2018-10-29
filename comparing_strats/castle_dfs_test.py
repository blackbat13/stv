from simple_models.castle_model import *
from comparing_strats.strat_simpl import StrategyComparer
# from comparing_strats.graph_drawing import GraphDrawing
import time
import datetime

DEBUG = True
now = datetime.datetime.now()
print(now)
castle_model = CastleModel(castle_sizes=[2, 1, 1], castle_lifes=[1, 1, 1])
no_states = len(castle_model.states)
print(f"Model have {no_states} states")

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
(result, strategy) = strategy_comparer.generate_strategy_dfs(0, set(winning_states), [0, 1, 2], strategy_comparer.epistemic_h)
end = time.process_time()
strategy_defined_count = 0
for str in strategy:
    if str is not None:
        strategy_defined_count += 1
print(f'Strategy generation time: {end - start} seconds')
print(f'Strategy result: {result}')
print(f'Number of states where strategy is defined: {strategy_defined_count}')
print(strategy)
