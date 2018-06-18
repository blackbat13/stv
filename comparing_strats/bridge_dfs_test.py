from comparing_strats.bridge_model import *
from comparing_strats.strat_simpl import StrategyComparer
from comparing_strats.strategy_generator import StrategyGenerator
from comparing_strats.graph_drawing import GraphDrawing


DEBUG = True
n = 2
hands = BridgeModel.generate_random_hands(n, n)
print(BridgeModel.hands_to_readable_hands(hands))
bridge_model = BridgeModel(no_cards_available=n, no_end_cards=n, first_state={'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                          'hands': hands, 'next': 0, 'history': [],
                                          'beginning': 0, 'clock': 0, 'suit': -1})
no_states = len(bridge_model.model.states)
print(f"Model have {no_states} states")

winning_states = []
max_visited = 0

for i, state in enumerate(bridge_model.model.states):
    if state['lefts'][0] >= n:
        if DEBUG:
            print(f'Winning state: {state}')
        winning_states.append(i)

if DEBUG:
    print(f'Max visited: {max_visited}')
    print(f'Number of winning states: {len(winning_states)}')

strategy_comparer = StrategyComparer(bridge_model.model, ['N', 'S', 'W', 'E', 'Wait'])
(result, strategy) = strategy_comparer.generate_strategy_dfs(0, set(winning_states), strategy_comparer.basic_h)
print(f'Strategy result: {result}')
print(strategy)
for index, value in enumerate(strategy):
    if value is not None:
        print(f"{index}: {BridgeModel.card_to_readable(value[0])}")
        print(f"{BridgeModel.board_to_readable(bridge_model.model.states[index]['board'])}: {BridgeModel.card_to_readable(value[0])}")

graphDrawing = GraphDrawing(bridge_model.model, strategy)
graphDrawing.draw()
