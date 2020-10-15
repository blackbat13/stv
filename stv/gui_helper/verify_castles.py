import sys
from stv.models import CastleModel


castle1_size = int(sys.argv[3])
castle2_size = int(sys.argv[4])
castle3_size = int(sys.argv[5])
life = int(sys.argv[6])
v = int(sys.argv[7])

castle_model = CastleModel([castle1_size, castle2_size, castle3_size], [life, life, life])
castle_model.generate()

print(castle_model.model.js_dump_model())

if v == 1:
    atl_model = castle_model.model.to_atl_imperfect(castle_model.get_actions())
else:
    atl_model = castle_model.model.to_atl_perfect(castle_model.get_actions())

winning = set()

state_id = -1

for state in castle_model.states:
    state_id += 1
    if state['lifes'][2] == 0:
        winning.add(state_id)

agents = []
for i in range(0, castle1_size):
    agents.append(i)

result = atl_model.minimum_formula_many_agents(agents, winning)
if 0 in result:
    print(1)
else:
    print(0)
print(len(result))
print(castle_model.model.js_dump_strategy_objective(atl_model.strategy))