from simple_models.simple_voting_2_model import SimpleVoting2Model

simple_voting = SimpleVoting2Model(1, 2)
# simple_voting.model.simulate(0)

voter_id = 0
gaunt_pref = [('Exist', 'se'), ('All', 'sc'), ('Exist', 'sv')]
bind_pref = [('se', 0), ('sc', 1), ('sv', 2)]
formula = 'F (end_v & vote_v_0 & !punish_v)'

winning_states = []
state_id = -1
for state in simple_voting.states:
    state_id += 1
    if state['finish'][voter_id] and state['vote'][voter_id] == 0 and not state['pun'][voter_id]:
        winning_states.append(state_id)
        print(state)

sl_model = simple_voting.model.to_sl_perfect(simple_voting.get_actions())

result = sl_model.verify(winning_states, gaunt_pref, bind_pref)
print(result)
for state_id in result:
    print(state_id, simple_voting.states[state_id])
