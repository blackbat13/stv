from simple_models.drone_model import DroneModel, CracowMap

drone_model = DroneModel(1, [1], CracowMap())
drone_model.generate()

atl_imperfect_model = drone_model.model.to_atl_imperfect(drone_model.get_actions())

winning = []

state_id = -1

for state in drone_model.states:
    state_id += 1
    if len(state['visited'][0]) == len(drone_model.graph):
        winning.append(state_id)
        print(state)

result = atl_imperfect_model.minimum_formula_many_agents([0], winning)

print(result)
drone_model.listify_states()
print(drone_model.model.js_dump_model())


