import sys
from stv.models import SimpleVotingModel
from stv.comparing_strats import StrategyComparer


no_voters = int(sys.argv[3])
no_candidates = int(sys.argv[4])
heuristic = int(sys.argv[5])

simple_voting = SimpleVotingModel(no_candidates, no_voters)
simple_voting.generate()

print(simple_voting.model.js_dump_model())

winning = []

state_id = -1
voter_number = 0

for state in simple_voting.states:
    state_id += 1
    if state['finish'][voter_number] == 1 and state['coercer_actions'][voter_number] != 'pun' and state['voted'][
            voter_number] != 1:
        winning.append(state_id)

agents = [1]

strategy_comparer = StrategyComparer(simple_voting.model, simple_voting.get_actions()[1])
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
print(simple_voting.model.js_dump_strategy_objective(strategy))