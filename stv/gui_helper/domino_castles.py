import sys
from stv.models import CastleModel
from stv.comparing_strats import StrategyComparer


castle1_size = int(sys.argv[3])
castle2_size = int(sys.argv[4])
castle3_size = int(sys.argv[5])
life = int(sys.argv[6])
heuristic = int(sys.argv[7])

castle_model = CastleModel([castle1_size, castle2_size, castle3_size], [life, life, life])
castle_model.generate()

winning = []

state_id = -1

for state in castle_model.states:
    state_id += 1
    if state['lifes'][2] == 0:
        winning.append(state_id)
        print(state)

agents = []
for i in range(0, castle1_size):
    agents.append(i)

strategy_comparer = StrategyComparer(castle_model.model, castle_model.get_actions()[0])
if heuristic == 0:
    (result, strategy) = strategy_comparer.domino_dfs(0, set(winning), agents, strategy_comparer.basic_h)
elif heuristic == 1:
    (result, strategy) = strategy_comparer.domino_dfs(0, set(winning), agents, strategy_comparer.control_h)
elif heuristic == 2:
    (result, strategy) = strategy_comparer.domino_dfs(0, set(winning), agents, strategy_comparer.epistemic_h)
elif heuristic == 3:
    (result, strategy) = strategy_comparer.domino_dfs(0, set(winning), agents, strategy_comparer.visited_states_h)

if result:
    print("1")
else:
    print("0")
print(castle_model.model.js_dump_strategy_objective(strategy))