import sys
from stv.models import CastleModel


castle1_size = int(sys.argv[1])
castle2_size = int(sys.argv[2])
castle3_size = int(sys.argv[3])
life = int(sys.argv[4])

castle_model = CastleModel([castle1_size, castle2_size, castle3_size], [life, life, life])

winning = []

state_id = -1

for state in castle_model.states:
    state_id += 1
    if state['lifes'][2] == 0:
        winning.append(state_id)

print(castle_model.model.js_dump_model(winning))