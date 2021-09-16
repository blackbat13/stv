Agent Voter[${N_Voters}]:
init: q0
% for i in range(1, N_Candidates + 1):
    vote${i}: q0 -> q1 [aID_vote=${i}]
% endfor
shared gv_aID: q1 -> q2 [Coercer1_aID_vote=?aID_vote]
shared ng_aID: q1 -> q2
shared pun_aID: q2 -> q3
shared npun_aID: q2 -> q3
PROTOCOL: [[pun_aID, npun_aID]]

Agent Coercer[1]:
init: q0
% for i in range(1, N_Voters + 1):
shared gv_Voter${i}: q0 -> q0 [aID_Voter${i}_gv=true]
shared ng_Voter${i}: q0 -> q0 [aID_Voter${i}_ngv=true]
shared pun_Voter${i}: q0 -> q0 [aID_pun${i}=true]
shared npun_Voter${i}: q0 -> q0 [aID_npun${i}=true]
% endfor
PROTOCOL: [${ (', ').join([f"[gv_Voter{i}, ng_Voter{i}]" for i in range(1,N_Voters+1)])}]

REDUCTION: [Coercer1_pun1]
COALITION: [Coercer1]
PERSISTENT: [${ (', ').join([f"Voter{i}_vote, Coercer1_Voter{i}_vote, Coercer1_pun{i}, Coercer1_npun{i}" for i in range(1,N_Voters+1)])}]
FORMULA: <<Coercer1>>F(Coercer1_pun1=True)
SHOW_EPISTEMIC: False