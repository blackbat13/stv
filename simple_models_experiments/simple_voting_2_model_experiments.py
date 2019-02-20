from simple_models.simple_voting_2_model import SimpleVoting2Model
import time

no_candidates = 2
no_voters = 5
start = time.perf_counter()
simple_voting = SimpleVoting2Model(no_voters, no_candidates)
stop = time.perf_counter()
time_generation = stop - start

print(time_generation)
print(len(simple_voting.states))
#simple_voting.model.simulate(0)

quant_pref = [('Exist', 'se'), ('All', 'sc'), ('Exist', 'sv')]
bind_pref = [('se', 0), ('sc', 1), ('sv', 2)]

quant_all_ids = [1]

for voter_id in range(1, no_voters):
    quant_pref.append(('Exist', f'sv{voter_id}'))
    bind_pref.append((f'sv{voter_id}', voter_id + 2))
    #quant_all_ids.append(voter_id + 2)

formula = 'F (end_v & vote_v_0 & !punish_v)'

winning_states = []
state_id = -1
voter_id = 0
for state in simple_voting.states:
    state_id += 1
    if state['finish'][voter_id] and state['vote'][voter_id] == 0 and state['pun'][voter_id] == False:
        winning_states.append(state_id)

sl_model = simple_voting.model.to_sl_perfect(simple_voting.get_actions())

start = time.perf_counter()
#result = sl_model.verify(winning_states, quant_pref, bind_pref, quant_all_ids)
stop = time.perf_counter()

time_verification = stop - start

# for state_id in result:
#     print(simple_voting.states[state_id])
formula_result = False

# if 0 in result:
#     formula_result = True
#     print("True")
# else:
#     print("False")


file = open("results-sv2.txt", "a")
file.write(f"no_candidates: {no_candidates}\n")
file.write(f"no_voters: {no_voters}\n")
file.write(f"no_states: {len(simple_voting.states)}\n")
file.write(f"generation time: {time_generation}\n")
file.write(f"verification time: {time_verification}\n")
file.write(f"formula result: {formula_result}\n")
file.write("\n\n")

file.close()
