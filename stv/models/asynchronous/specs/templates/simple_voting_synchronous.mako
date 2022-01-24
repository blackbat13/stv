SEMANTICS: synchronous
Agent Voter[${N_Voters}]:
init: q0
% for i in range(1, N_Candidates + 1):
    vote${i}: q0 -> q1 [aID_vote=${i}]
% endfor
give: q1 -> q2 [aID_reported=?aID_vote]
ngive: q1 -> q2 [aID_reported=-1]
pun: q2 -[Coercer1_pun_ID == 1]> q3 [aID_pun=1]
npun: q2 -[Coercer1_pun_ID == -1]> q3 [aID_pun=0]
loop: q3->q3

Agent Coercer[1]:
init: q0
% for i in range(1, N_Voters + 1):
pun_Voter${i}: q0 -[Voter${i}_reported != 0 and aID_pun_${i} == 0]> q0 [aID_pun_${i}=1]
npun_Voter${i}: q0 -[Voter${i}_reported != 0 and aID_pun_${i} == 0]> q0 [aID_pun_${i}=-1]
% endfor

REDUCTION: []
COALITION: [Voter1]
PERSISTENT: [${ (', ').join([f"Voter{i}_vote, Voter{i}_reported, Voter{i}_pun, Coercer1_pun_{i}" for i in range(1,N_Voters+1)])}]
INITIAL: [${ (', ').join([f"Voter{i}_vote=0, Voter{i}_reported=0, Voter{i}_pun=0, Coercer1_pun_{i}=0" for i in range(1,N_Voters+1)])}]
FORMULA: <<Voter1>>G(Voter1_vote=1 | Voter1_pun=0)
SHOW_EPISTEMIC: False