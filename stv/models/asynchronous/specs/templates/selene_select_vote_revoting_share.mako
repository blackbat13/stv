<%!
    import itertools
%>

Agent EA1:
LOCAL: [${', '.join([f"EA1_tracker{t_i}, EA1_tracker{t_i}_vote" for t_i in range(1,N_Voters+N_CVoters+1)])}]
PERSISTENT: [${', '.join([f"EA1_tracker{t_i}, EA1_tracker{t_i}_vote" for t_i in range(1,N_Voters+N_CVoters+1)])}]
INITIAL: []
init prepare
shared[${N_CVoters + 1}] is_ready[is_ready]: prepare -> start
% for perm in list(itertools.permutations(range(1,N_Voters + N_CVoters + 1))):
    gen_trackers${(loop.index+1)}_EA1: start -> generate [${ ', '.join([f"EA1_tracker{v_i + 1}:={tr_val}" for v_i,tr_val in enumerate(perm)]) }]
% endfor
shared[${N_Voters + N_CVoters + 2}] start_voting[start_voting]: generate -> voting
% for vi in range(1, N_Voters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        % for ci in range(1, N_Candidates + 1):
            shared[2] send_vote${ci}_Voter${vi}[send_vote_Voter${vi}]: voting [EA1_tracker${ti}==${vi}] -> voting [EA1_tracker${ti}_vote:=${ci}]
        %endfor
    % endfor
% endfor
% for vi in range(1, N_CVoters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        % for ci in range(1, N_Candidates + 1):
            shared[2] send_vote${ci}_VoterC${vi}[send_vote_VoterC${vi}]: voting [EA1_tracker${ti}==${vi + N_Voters}] -> voting [EA1_tracker${ti}_vote:=${ci}]
            shared[2] send_fvote${ci}_VoterC${vi}[send_fvote_VoterC${vi}]: voting [EA1_tracker${ti}==${vi + N_Voters}] -> voting [EA1_tracker${ti}_vote:=${ci}]
        %endfor
    % endfor
% endfor
shared[${N_Voters + N_CVoters + 2}] finish_voting[finish_voting]: voting -> finish
% for vi in range(1, N_Voters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared[2] send_tracker${ti}_Voter${vi}[send_tracker${ti}_Voter${vi}]: finish [EA1_tracker${ti}==${vi}] -> finish
    % endfor
% endfor
% for vi in range(1, N_CVoters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared[2] send_tracker${ti}_VoterC${vi}[send_tracker${ti}_VoterC${vi}]: finish [EA1_tracker${ti}==${vi + N_Voters}] -> finish
    % endfor
% endfor
shared[${N_Voters + N_CVoters + 2}] finish_sending_trackers[finish_sending_trackers]: finish -> check
% for ti in range(1, N_Voters + N_CVoters + 1):
    % for ci in range(1, N_Candidates + 1):
        % for vi in range(1, N_Voters + 1):
            shared[2] check${ci}_tracker${ti}_Voter${vi}[check${ci}_tracker_Voter${vi}]: check [EA1_tracker${ti}_vote==${ci}] -> check
        % endfor
        % for vi in range(1, N_CVoters + 1):
            shared[2] check${ci}_tracker${ti}_VoterC${vi}[check${ci}_tracker_VoterC${vi}]: check [EA1_tracker${ti}_vote==${ci}] -> check
        % endfor
        shared[2] check${ci}_tracker${ti}_Coercer1[check${ci}_tracker_Coercer1]: check [EA1_tracker${ti}_vote==${ci}] -> check
    %endfor
% endfor

% if N_Voters > 0:
    % for vi in range(1, N_Voters + 1):
        Agent Voter${vi}:
        LOCAL: [Voter${vi}_vote, ${', '.join([f"Voter{vi}_tracker{ti}" for ti in range(1, N_Voters + N_CVoters + 1)])}]
        PERSISTENT: [Voter${vi}_vote]
        INITIAL: []
        init start
        shared[${N_Voters + N_CVoters + 2}] start_voting[start_voting]: start -> voting
        % for ci in range(1, N_Candidates + 1):
            vote${ci}_Voter${vi}: voting -> vote [Voter${vi}_vote:=${ci}]
            shared[2] send_vote${ci}_Voter${vi}[send_vote${ci}_Voter${vi}]: vote [Voter${vi}_vote==${ci}] -> send
        % endfor
        shared[${N_Voters + N_CVoters + 2}] finish_voting[finish_voting]: send -> finish
        % for ti in range(1, N_Voters + N_CVoters + 1):
            shared[2] send_tracker${ti}_Voter${vi}[send_tracker_Voter${vi}]: finish -> tracker [Voter${vi}_tracker:=${ti}]
        %endfor
        shared[${N_Voters + N_CVoters + 2}] finish_sending_trackers[finish_sending_trackers]: tracker -> check
        % for ti in range(1, N_Voters + N_CVoters + 1):
            % for ci in range(1, N_Candidates + 1):
                shared[2] check${ci}_tracker${ti}_Voter${vi}[check_tracker${ti}_Voter${vi}]: check -> end [Voter${vi}_tracker${ti}:=${ci}]
            %endfor
        % endfor

    % endfor
% endif

% for vc in range(1, N_CVoters + 1):
    Agent VoterC${vc}:
    LOCAL: [VoterC${vc}_vote, VoterC${vc}_tracker, VoterC${vc}_required, VoterC${vc}_revote, VoterC${vc}_prep_vote, VoterC${vc}_punish, ${', '.join([f"VoterC{vc}_tracker{ti}" for ti in range(1, N_Voters + N_CVoters + 1)])}]
    PERSISTENT: [VoterC${vc}_vote, VoterC${vc}_required, VoterC${vc}_revote, VoterC${vc}_prep_vote, VoterC${vc}_punish]
    INITIAL: [VoterC${vc}_revote:=1]
    init start
    % for i in range(1, N_Candidates + 1):
        shared[2] coerce${i}_VoterC${vc}[coerce_VoterC${vc}]: start -> coerced [VoterC${vc}_required:=${i}]
    % endfor
    % for i in range(1, N_Candidates + 1):
        select_vote${i}_VoterC${vc}: coerced -> prepared [VoterC${vc}_vote:=${i}, VoterC${vc}_prep_vote:=${i}]
    % endfor
    shared[${N_CVoters + 1}] is_ready[is_ready]: prepared -> ready
    shared[${N_Voters + N_CVoters + 2}] start_voting[start_voting]: ready -> voting
    % for ci in range(1, N_Candidates + 1):
        shared[2] send_vote${ci}_VoterC${vc}[send_vote${ci}_VoterC${vc}]: vote [VoterC${vc}_vote==${ci}] -> send
    %endfor
    % for ri in range(1, N_Revote + 1):
        % for ci in range(1, N_Candidates + 1):
                shared[2] VoterC${vc}_vote${ci}_rev${ri}[VoterC${vc}_vote${ci}_rev${ri}]: voting [VoterC${vc}_vote==${ci} && VoterC${vc}_revote==${ri}] -> vote
        %endfor
    %endfor
    % for j in range(1, N_Revote):
        revote_vote_${j}_VoterC${vc}: send [VoterC${vc}_revote==${j}] -> voting [VoterC${vc}_vote:=VoterC${vc}_required, VoterC${vc}_revote:=${j+1}]
        skip_revote_${j}_VoterC${vc}: send [VoterC${vc}_revote==${j}] -> votingf
    % endfor
    final_vote_VoterC${vc}: send [VoterC${vc}_revote==${N_Revote}] -> votingf [VoterC${vc}_vote:=VoterC${vc}_prep_vote]
    skip_final_VoterC${vc}: send [VoterC${vc}_revote==${N_Revote}] -> votingf
    % for ci in range(1, N_Candidates + 1):
        shared[2] send_fvote${ci}_VoterC${vc}[send_fvote${ci}_VoterC${vc}]: votingf [VoterC${vc}_vote==${ci}] -> sendf
    %endfor
    shared[${N_Voters + N_CVoters + 2}] finish_voting[finish_voting]: sendf -> finish
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared[2] send_tracker${ti}_VoterC${vc}[send_tracker_VoterC${vc}]: finish -> tracker [VoterC${vc}_tracker:=${ti}]
    %endfor
    shared[${N_Voters + N_CVoters + 2}] finish_sending_trackers[finish_sending_trackers]: tracker -> trackers_sent
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared[2] give${ti}_VoterC${vc}[give${ti}_VoterC${vc}]: trackers_sent -> interact
    % endfor
    shared[2] not_give_VoterC${vc}[not_give_VoterC${vc}]: trackers_sent -> interact
    shared[2] punish_VoterC${vc}[interact_VoterC${vc}]: interact -> check [VoterC${vc}_punish:=1]
    shared[2] not_punish_VoterC${vc}[interact_VoterC${vc}]: interact -> check [VoterC${vc}_punish:=0]
    % for ti in range(1, N_Voters + N_CVoters + 1):
        % for ci in range(1, N_Candidates + 1):
            shared[2] check${ci}_tracker${ti}_VoterC${vc}[check_tracker${ti}_VoterC${vc}]: check -> end [VoterC${vc}_tracker${ti}:=${ci}]
        %endfor
    % endfor
% endfor

Agent Coercer1:
LOCAL: [Coercer1_finish, ${', '.join([f"Coercer1_VoterC{v_i}_vote, Coercer1_VoterC{v_i}_tracker, Coercer1_VoterC{v_i}_required, Coercer1_VoterC{v_i}_revote" for v_i in range(1,N_CVoters+1)])}, ${', '.join([f"Coercer1_tracker{ti}" for ti in range(1, N_Voters + N_CVoters + 1)])}]
PERSISTENT: [Coercer1_finish, ${', '.join([f"Coercer1_VoterC{v_i}_vote, Coercer1_VoterC{v_i}_tracker, Coercer1_VoterC{v_i}_required, Coercer1_VoterC{v_i}_revote" for v_i in range(1,N_CVoters+1)])}]
INITIAL: []
init coerce
% for vi in range(1, N_CVoters + 1):
    % for ci in range(1, N_Candidates + 1):
        shared[2] coerce${ci}_VoterC${vi}[coerce${ci}_VoterC${vi}]: coerce -> coerce [Coercer1_VoterC${vi}_required:=${ci}]
    % endfor
% endfor
shared[${N_Voters + N_CVoters + 2}] start_voting[start_voting]: coerce -> voting
% for vi in range(1, N_CVoters + 1):
    % for ci in range(1, N_Candidates + 1):
        % for ri in range(1, N_Revote + 1):
            shared[2] VoterC${vi}_vote${ci}_rev${ri}[VoterC${vi}_vote]: voting -> voting [Coercer1_VoterC${vi}_vote:=${ci}, Coercer1_VoterC${vi}_revote:=${ri}]
        %endfor
    %endfor
% endfor
shared[${N_Voters + N_CVoters + 2}] finish_voting[finish_voting]: voting -> finish
shared[${N_Voters + N_CVoters + 2}] finish_sending_trackers[finish_sending_trackers]: finish -> trackers_sent
% for vi in range(1, N_CVoters + 1):
    % for ti in range(1, N_Voters + N_CVoters + 1):
        shared[2] give${ti}_VoterC${vi}[interact_VoterC${vi}]: trackers_sent -> trackers_sent [Coercer1_VoterC${vi}_tracker:=${ti}]
    % endfor
    shared[2] not_give_VoterC${vi}[interact_VoterC${vi}]: trackers_sent -> trackers_sent [Coercer1_VoterC${vi}_tracker:=0]
% endfor
to_check_Coercer1: trackers_sent -> check
% for ti in range(1, N_Voters + N_CVoters + 1):
    % for ci in range(1, N_Candidates + 1):
        shared[2] check${ci}_tracker${ti}_Coercer1[check_tracker${ti}_Coercer1]: check -> check [Coercer1_tracker${ti}:=${ci}]
    %endfor
% endfor
to_interact_Coercer1: check -> interact
% for vi in range(1, N_CVoters + 1):
    shared[2] punish_VoterC${vi}[punish_VoterC${vi}]: interact -> interact
    shared[2] not_punish_VoterC${vi}[not_punish_VoterC${vi}]: interact -> interact
% endfor
finish_Coercer1: interact -> end [Coercer1_finish:=1]

## FORMULA: <<Coercer1>>G(((Coercer1_finish==1 && Coercer1_VoterC1_vote==1) => VoterC1_punish==0) && ((Coercer1_finish==1 && VoterC1!=1) => VoterC1_punish==1))