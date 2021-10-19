<%!
    import itertools
%>

Agent EA[1]:
init prepare
shared is_ready: prepare -> start
% for perm in list(itertools.permutations(range(1,N_Voters + N_CVoters + 1))):
    gen_trackers${(loop.index+1)}: start -> generate [${ ', '.join([f"aID_tracker{v_i + 1}={tr_val}" for v_i,tr_val in enumerate(perm)]) }]
% endfor
shared start_voting: generate -> voting
% for vi in range(1, N_Voters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared send_vote_Voter${vi}: voting -[aID_tracker${ti}==${vi}]> voting [aID_tracker${ti}_vote=?Voter${vi}_vote]
    % endfor
% endfor
% for vi in range(1, N_CVoters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared send_vote_VoterC${vi}: voting -[aID_tracker${ti}==${vi + N_Voters}]> voting [aID_tracker${ti}_vote=?VoterC${vi}_vote]
        shared send_fvote_VoterC${vi}: voting -[aID_tracker${ti}==${vi + N_Voters}]> voting [aID_tracker${ti}_vote=?VoterC${vi}_vote]
    % endfor
% endfor
shared finish_voting: voting -> finish
% for vi in range(1, N_Voters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared send_tracker_Voter${vi}: finish -[aID_tracker${ti}==${vi}]> finish [Voter${vi}_tracker=${ti}]
    % endfor
% endfor
% for vi in range(1, N_CVoters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared send_tracker_VoterC${vi}: finish -[aID_tracker${ti}==${vi + N_Voters}]> finish [VoterC${vi}_tracker=${ti}]
    % endfor
% endfor
shared finish_sending_trackers: finish -> check
% for ti in range(1, N_Voters + N_CVoters + 1):
    % for vi in range(1, N_Voters + 1):
        shared check_tracker${ti}_Voter${vi}: check -> check [Voter${vi}_tracker${ti}=?aID_tracker${ti}_vote]
    % endfor
    % for vi in range(1, N_CVoters + 1):
        shared check_tracker${ti}_VoterC${vi}: check -> check [VoterC${vi}_tracker${ti}=?aID_tracker${ti}_vote]
    % endfor
    shared check_tracker${ti}_Coercer1: check -> check [Coercer1_tracker${ti}=?aID_tracker${ti}_vote]
% endfor
PROTOCOL: [${', '.join(['['+(', '.join([f"check_tracker{t_i}_Voter{v_i}" for t_i in range(1, N_Voters + N_CVoters + 1) ]))+']' for v_i in range(1,N_Voters+1)])}, ${', '.join(['['+(', '.join([f"check_tracker{t_i}_VoterC{v_i}" for t_i in range(1, N_Voters + N_CVoters + 1) ]))+']' for v_i in range(1,N_CVoters+1)])}, [${', '.join([f"check_tracker{t_i}_Coercer1" for t_i in range(1, N_Voters + N_CVoters + 1) ])}]]

% if N_Voters > 0:
    Agent Voter[${N_Voters}]:
    init start
    shared start_voting: start -> voting
    % for i in range(1, N_Candidates + 1):
        vote${i}: voting -> vote [aID_vote=${i}]
    % endfor
    shared send_vote_aID: vote -> send
    shared finish_voting: send -> finish
    shared send_tracker_aID: finish -> tracker
    shared finish_sending_trackers: tracker -> check
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared check_tracker${ti}_aID: check -> end
    % endfor
% endif

Agent VoterC[${N_CVoters}]:
init start
% for i in range(1, N_Candidates + 1):
    shared coerce${i}_aID: start -> coerced [aID_required=${i}]
% endfor
% for i in range(1, N_Candidates + 1):
    select_vote${i}: coerced -> prepared [aID_vote=${i}, aID_prep_vote=${i}]
% endfor
shared is_ready: prepared -> ready
shared start_voting: ready -> voting
shared aID_vote: voting -> vote [Coercer1_aID_vote=?aID_vote, Coercer1_aID_revote=?aID_revote]
shared send_vote_aID: vote -> send
% for j in range(1, N_Revote):
    revote_vote_${j}: send -[aID_revote==${j}]> voting [aID_vote=?aID_required, aID_revote=${j+1}]
    skip_revote_${j}: send -[aID_revote==${j}]> votingf
% endfor
final_vote: send -[aID_revote==${N_Revote}]> votingf [aID_vote=?aID_prep_vote]
skip_final: send -[aID_revote==${N_Revote}]> votingf
shared send_fvote_aID: votingf -> sendf
shared finish_voting: sendf -> finish
shared send_tracker_aID: finish -> tracker
shared finish_sending_trackers: tracker -> trackers_sent
% for ti in range(1, N_Voters + N_CVoters + 1):
    shared give${ti}_aID: trackers_sent -> interact [Coercer1_aID_tracker=${ti}]
% endfor
shared not_give_aID: trackers_sent -> interact [Coercer1_aID_tracker=0]
shared punish_aID: interact -> ckeck [aID_punish=true]
shared not_punish_aID: interact -> check [aID_punish=false]
% for ti in range(1, N_Voters + N_CVoters + 1):
    shared check_tracker${ti}_aID: check -> end
% endfor
PROTOCOL: [[${', '.join([f"coerce{c_i}_aID" for c_i in range(1,N_Candidates+1)])}], [punish, not_punish]]

Agent Coercer[1]:
init coerce
% for vi in range(1, N_CVoters + 1):
    % for ci in range(1, N_Candidates + 1):
        shared coerce${ci}_VoterC${vi}: coerce -> coerce [aID_VoterC${vi}_required=${ci}]
    % endfor
% endfor
shared start_voting: coerce -> voting
% for vi in range(1, N_CVoters + 1):
    shared VoterC${vi}_vote: voting -> voting
% endfor
shared finish_voting: voting -> finish
shared finish_sending_trackers: finish -> trackers_sent
% for vi in range(1, N_CVoters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared give${ti}_VoterC${vi}: trackers_sent -> trackers_sent
    % endfor
    shared not_give_VoterC${vi}: trackers_sent -> trackers_sent
% endfor
to_check: trackers_sent -> check
% for ti in range(1, N_Voters + N_CVoters + 1):
    shared check_tracker${ti}_Coercer1: check -> check
% endfor
to_interact: check -> interact
% for vi in range(1, N_CVoters + 1):
    shared punish_VoterC${vi}: interact -> interact
    shared not_punish_VoterC${vi}: interact -> interact
% endfor
finish: interact -> end [aID_finish=1]
PROTOCOL: [${','.join(['['+(', '.join([f"give{t_i}_VoterC{v_i}" for t_i in range(1, N_Voters + N_CVoters + 1) ]))+f', not_give_VoterC{v_i}]' for v_i in range(1,N_CVoters+1)])}]

INITIAL: [${', '.join([f"VoterC{v_i}_revote=1" for v_i in range(1,N_CVoters+1)])}]
REDUCTION: [VoterC1_vote, VoterC1_revote, Coercer1_finish]
COALITION: [Coercer1]
PERSISTENT: [Coercer1_finish, ${', '.join([f"Voter{v_i}_vote, Voter{v_i}_tracker" for v_i in range(1,N_Voters+1)])}, ${', '.join([f"VoterC{v_i}_vote, Coercer1_VoterC{v_i}_vote, VoterC{v_i}_tracker, VoterC{v_i}_required, Coercer1_VoterC{v_i}_tracker, Coercer1_VoterC{v_i}_required, VoterC{v_i}_revote, Coercer1_VoterC{v_i}_revote, VoterC{v_i}_prep_vote" for v_i in range(1,N_CVoters+1)])}, ${', '.join([f"EA1_tracker{t_i}, EA1_tracker{t_i}_vote" for t_i in range(1,N_Voters+N_CVoters+1)])}]
%% FORMULA: <<VoterC1>>F(Coercer1_VoterC1_tracker=1 || Coercer1_VoterC1_tracker=2)
%% FORMULA: <<Coercer1>>F(VoterC1_revote=${N_Revote-1} -> K_Coercer1 VoterC1_vote)
FORMULA: <<Coercer1>>F(Coercer1_finish=1)
SHOW_EPISTEMIC: False