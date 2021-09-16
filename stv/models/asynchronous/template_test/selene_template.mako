<%!
    import itertools
%>

Agent EA[1]:
init: ea_init
% for perm in list(itertools.permutations(range(1,N_Voters+1))):
    shared generateTrackers_${(loop.index+1)}: ea_init -> ea_gen [${ ', '.join([f"aID_t{v_i}={tr_val}" for v_i,tr_val in enumerate(perm)]) }]
% endfor
shared startVoting: ea_gen -> ea_start
% for v_i in range(1,N_Voters+1):
    % for tr_i in range(1,N_Voters+1):
        shared sendVote_Voter${v_i}: ea_start -[aID_t${tr_i}==${v_i}]> ea_start [aID_vote${tr_i}=?Voter${v_i}_vote]
    % endfor
% endfor
shared finishVoting: ea_start -> ea_finish
% for v_i in range(1,N_Voters+1):
    % for tr_i in range(1,N_Voters+1):
        shared sendTracker_Voter${v_i}: ea_start -[aID_t${tr_i}==${v_i}]> ea_finish [Voter${v_i}_true_tracker=${tr_i}]
    % endfor
% endfor
shared allTrackerSend: ea_finish -> ea_send
% for v_i in range(1,N_Voters+1):
    shared coercerWBB${v_i}: ea_send -> ea_send [Coercer1_wbb${v_i}=?aID_vote${v_i}]
% endfor

Agent Voter[${N_Voters}]:
init: v_init
% for c_i in range(1,N_Candidates+1):
    shared requestVoteFor${c_i}_aID: v_init -> v_request [aID_req=${c_i}]
% endfor
shared leave_aID: v_init -> v_request [aID-req=0]
shared startVoting: v_request -> v_start
% for c_i in range(1,N_Candidates+1):
    fillVote${c_i}: v_start -> v_fill [aID_vote=${c_i}]
% endfor
shared sendVote_aID: v_fill -> v_send
shared finishVoting: v_send -> v_finish
% for c_i in range(1,N_Candidates+1):
    computeFalseTracker${c_i}: v_finish -> v_false_tr [aID_false_tr=${c_i}]
% endfor
dontComputeFalseAlphaTerm: v_finish -> v_false_tr
shared sendTracker_aID: v_false_tr -> v_send_tr
shared allTrackerSend: v_send_tr -> v_wbb
% for tr_i in range(1,N_Voters+1):
    shared showTracker${tr_i}_aID: v_wbb -[aID_true_tr==${tr_i}]> v_show
    shared showTracker${tr_i}_aID: v_wbb -[aID_false_tr==${tr_i}]> v_show
% endfor
PROTOCOL: [[leave_aID,${','.join([f"requestVoteFor{c_i}_aID" for c_i in range(1,N_Candidates+1)])}]]

Agent Coercer[1]:
init: c_init
% for v_i in range(1,N_Voters+1):
    % for c_i in range(1, N_Candidates+1):
        shared requestVoteFor${c_i}_Voter${v_i}: c_init -> c_init [aID_req${v_i}=${c_i}]
    % endfor
    shared leave_Voter${v_i}: c_init -> c_init [aID_req${v_i}=0]
% endfor
shared finishVoting: c_init -> c_finish
% for v_i in range(1,N_Voters+1):
    shared coercerWBB${v_i}: c_finish -> c_finish
% endfor
% for v_i in range(1,N_Voters+1):
    % for tr_i in range(1,N_Voters+1):
        shared showTracker${tr_i}_Voter${v_i}: c_finish -> c_finish [aID_tr${v_i}=${tr_i}]
    % endfor
% endfor
PROTOCOL: [${','.join(['['+(','.join([f"showTracker{tr_i}_Voter{v_i}" for tr_i in range(1,N_Voters+1) ]))+']' for v_i in range(1,N_Voters+1)])}]
REDUCTION: [${', '.join([f"Voter{v_i}_vote" for v_i in range(1,N_Voters+1)])}, Coercer1_end]
PERSISTENT: [${', '.join([f"EA1_t{v_i}, EA1_vote{v_i}, Coercer1_req{v_i}, Coercer1_tr{v_i}, Coercer1_wbb{v_i}, Voter{v_i}_true_tr, Voter{v_i}_req, Voter{v_i}_false_tr, Voter{v_i}_vote" for v_i in range(1,N_Voters+1)])}]
COALITION: [Coercer1]
FORMULA: <<Coercer1>>F(Voter1_vote=1)