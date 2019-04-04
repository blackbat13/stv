from simple_models.bridge_model import BridgeModel

n = 1
bridge_model = BridgeModel(n, n, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                  'hands': BridgeModel.generate_random_hands(n, n), 'next': 0, 'history': [],
                                  'beginning': 0, 'clock': 0, 'suit': -1})

winning_states = set()
for state_id in range(0, len(bridge_model.states)):
    state = bridge_model.states[state_id]
    if state['lefts'][0] > state['lefts'][1] and state['lefts'][0] + state['lefts'][1] == n:
        winning_states.add(state_id)

atl_model = bridge_model.model.to_atl_imperfect(bridge_model.get_actions())
result = atl_model.minimum_formula_many_agents([0], winning_states)
print(result)
print(atl_model.strategy)
