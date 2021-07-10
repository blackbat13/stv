import sys
from stv.models import DroneModel, CracowMap


n = int(sys.argv[3])
k = int(sys.argv[4])

energies = []
for _ in range(0, n):
    energies.append(k)

drone_model = DroneModel(n, energies, CracowMap())
drone_model.generate()

winning = []

state_id = -1

for state in drone_model.states:
    state_id += 1
    if len(state['visited'][0]) >= 2:#len(drone_model.graph):
        winning.append(state_id)

drone_model.listify_states()
print(drone_model.model.js_dump_model(winning))