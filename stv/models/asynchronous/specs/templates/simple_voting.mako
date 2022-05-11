% for vi in range(1, N_Voters + 1):
    Agent Voter${vi}:
    LOCAL: [${', '.join([f"Voter{vi}_vote" for vi in range(1, N_Voters + 1)])}]
    PERSISTENT: [${', '.join([f"Voter{vi}_vote" for vi in range(1, N_Voters + 1)])}]
    INITIAL: []
    init q0
    % for i in range(1, N_Candidates + 1):
        vote${i}: q0 -> q1 [Voter${vi}_vote:=${i}]
        shared[2] gv_${i}_Voter${vi}[gv_${i}_Voter${vi}]: q1 [Voter${vi}_vote==${i}] -> q2
    % endfor
    shared[2] ng_Voter${vi}[ng_Voter${vi}]: q1 -> q2
    shared[2] pun_Voter${vi}[pn_Voter${vi}]: q2 -> q3
    shared[2] npun_Voter${vi}[pn_Voter${vi}]: q2 -> q3
% endfor

Agent Coercer1:
LOCAL: [${', '.join([f"Coercer1_Voter{vi}_vote, Coercer1_Voter{vi}_gv, Coercer1_pun{vi}, Coercer1_npun{vi}" for vi in range(1, N_Voters + 1)])}]
PERSISTENT: [${', '.join([f"Coercer1_Voter{vi}_vote, Coercer1_Voter{vi}_gv, Coercer1_pun{vi}, Coercer1_npun{vi}" for vi in range(1, N_Voters + 1)])}]
INITIAL: []
init q0
% for vi in range(1, N_Voters + 1):
    % for i in range(1, N_Candidates + 1):
        shared[2] gv_${i}_Voter${vi}[g_Voter${vi}]: q0 -> q0 [Coercer1_Voter${vi}_vote:=${i}, Coercer1_Voter${i}_gv:=1]
    % endfor
shared[2] ng_Voter${vi}[g_Voter${vi}]: q0 -> q0 [Coercer1_Voter${vi}_gv:=2]
shared[2] pun_Voter${vi}[pun_Voter${vi}]: q0 -> q0 [Coercer1_pun${vi}:=1]
shared[2] npun_Voter${vi}[npun_Voter${vi}]: q0 -> q0 [Coercer1_npun${vi}:=1]
% endfor