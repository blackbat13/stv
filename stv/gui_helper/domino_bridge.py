import json
import sys
from stv.models import BridgeModel
from stv.comparing_strats import StrategyComparer


n = int(sys.argv[3])
k = int(sys.argv[4])
heuristic = int(sys.argv[5])

file_hands = open("bridge_hands.txt", "r")
json_hands = file_hands.readline()
file_hands.close()

hands = json.loads(json_hands)

bridge_model = BridgeModel(n, k, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                  'hands': hands, 'next': 0, 'history': [],
                                  'beginning': 0, 'clock': 0, 'suit': -1})
bridge_model.generate()
bridge_model.transitions_to_readable()
bridge_model.model.to_subjective([0])

winning = []

state_id = -1

for state in bridge_model.states:
    state_id += 1
    if state['lefts'][0] > state['lefts'][1] and state['lefts'][0] + state['lefts'][1] == k:
        winning.append(state_id)

strategy_comparer = StrategyComparer(bridge_model.model, bridge_model.get_actions()[0])
if heuristic == 0:
    (result, strategy) = strategy_comparer.domino_dfs(bridge_model.model.first_state_id, set(winning), [0],
                                                                 strategy_comparer.basic_h)
elif heuristic == 1:
    (result, strategy) = strategy_comparer.domino_dfs(bridge_model.model.first_state_id, set(winning), [0],
                                                                 strategy_comparer.control_h)
elif heuristic == 2:
    (result, strategy) = strategy_comparer.domino_dfs(bridge_model.model.first_state_id, set(winning), [0],
                                                                 strategy_comparer.epistemic_h)
elif heuristic == 3:
    (result, strategy) = strategy_comparer.domino_dfs(bridge_model.model.first_state_id, set(winning), [0],
                                                                 strategy_comparer.visited_states_h)

if result:
    print("1")
else:
    print("0")

print(bridge_model.model.js_dump_strategy_subjective(strategy))
