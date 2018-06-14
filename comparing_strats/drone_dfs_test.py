from comparing_strats.drone_model import *
from comparing_strats.strat_simpl import StrategyComparer
from comparing_strats.strategy_generator import StrategyGenerator
from comparing_strats.graph_drawing import GraphDrawing


DEBUG = True
no_drones = 1
energies = [2]
print(no_drones, energies)
drone_model = DroneModel(no_drones=no_drones, energies=energies, map=CracowMap(), is_random=False)
no_states = len(drone_model.states)
print(f"Model have {no_states} states")

graphDrawing = GraphDrawing(drone_model.model)
graphDrawing.draw()

winning_states = []
max_visited = 0

for i, state in enumerate(drone_model.states):
    if DEBUG:
        print(state)
    visited = set()
    for vis in state['visited']:
        visited.update(vis)
    if len(visited) > max_visited:
        max_visited = len(visited)

for i, state in enumerate(drone_model.states):
    visited = set()
    for vis in state['visited']:
        visited.update(vis)
    if len(visited) >= max_visited:
        if DEBUG:
            print(f'Winning state: {state}')
        winning_states.append(i)

if DEBUG:
    print(f'Max visited: {max_visited}')
    print(f'Number of winning states: {len(winning_states)}')

strategy_comparer = StrategyComparer(drone_model.model, ['N', 'S', 'W', 'E', 'Wait'])
result = strategy_comparer.generate_strategy_dfs(0, set(winning_states), None)
print(f'Strategy result: {result}')
for index, value in enumerate(strategy_comparer.winning_strategy):
    if value is not None:
        print(f"{index}: {value}")
