import sys
from stv.models import TianJiModel


horses = int(sys.argv[3])
v = int(sys.argv[4])

tian_ji_model = TianJiModel(horses)
tian_ji_model.generate()
print(tian_ji_model.model.js_dump_model())

if v == 1:
    atl_model = tian_ji_model.model.to_atl_imperfect(tian_ji_model.get_actions())
else:
    atl_model = tian_ji_model.model.to_atl_perfect(tian_ji_model.get_actions())

winning = set()

state_id = -1

for state in tian_ji_model.states:
    state_id += 1
    if state['tian_ji_score'] > state['king_score'] and len(state['tian_ji_horses']) == 0:
        winning.add(state_id)

result = atl_model.minimum_formula_many_agents([0], winning)
if 0 in result:
    print(1)
else:
    print(0)
print(len(result))
print(tian_ji_model.model.js_dump_strategy_objective(atl_model.strategy))