from simple_model.tian_ji_model import TianJiModel

tian_ji_model = TianJiModel(4)
# tian_ji_model.model.simulate(0)

atl_model = tian_ji_model.model.to_atl_imperfect(tian_ji_model.get_actions())

winning = []

state_id = -1

for state in tian_ji_model.states:
    state_id += 1
    if state['tian_ji_score'] > state['king_score'] and len(state['tian_ji_horses']) == 0:
        winning.append(state_id)

result = atl_model.minimum_formula_many_agents([0], winning)

print(result)