<%!
    import itertools
%>

SEMANTICS: synchronous
% for r_id in range(0, N_Robots):
    Agent Robot${r_id}:
    init: idle
    INTERFACE: [${ (', ').join([f"f_{i}_a_1, f_{i}_a_2, f_{i}_s" for i in range(1,N_Fields+1)]) }]
    LOCAL: [aID_r_x, aID_r_e, aID_r_t, aID_r_p]
    move_f: idle -[aID_r_x<${N_Fields} and aID_r_e>0 and aID_r_t==0]> idle [aID_r_x+=1, aID_r_e-=1]
    move_b: idle -[aID_r_x>1 and aID_r_e>0 and aID_r_t==0]> idle [aID_r_x-=1, aID_r_e-=1]
    % for i in range(1, N_Fields+1):
        pick${i}: idle -[aID_r_x==${i} and f_${i}_a_${r_id}==1 and aID_r_p==0 and aID_r_e>0]> s_pick${i} [aID_r_t=1]
        cont_pick${i}: s_pick${i} -[f_${i}_s==${r_id}]> cont_pick${i} [aID_r_p=1]
        fin_pick${i}: cont_pick${i} -[f_${i}_s!=${r_id}]> idle [aID_r_t=0]
    % endfor
    % for i in range(1, N_Fields+1):
        drop${i}: idle -[aID_r_x==${i} and aID_r_p==1 and f_${i}_a_${(r_id+1)%N_Robots}==0]> s_drop${i} [aID_r_t=2]
        cont_drop${i}: s_drop${i} -[f_${i}_s==${r_id}]> cont_drop${i} [aID_r_p=0]
        fin_drop${i}: cont_drop${i} -[f_${i}_s!=${r_id}]> idle [aID_r_t=0]
    % endfor
    charge: idle -[aID_r_e==0]> end [aID_r_t=3]

% endfor

Agent Factory:
init: idle
INTERFACE: [${ (', ').join([f"Robot{i}_r_x, Robot{i}_r_t, Robot{i}_r_p, Robot{i}_r_e" for i in range(0,N_Robots)]) }]
LOCAL: [${(', ').join(f"f_{fID}_s, " + (', ').join([f"f_{fID}_a_{rID}" for rID in range(0,N_Robots)]) for fID in range(1, N_Fields + 1)) }]
% for fID in range(1, N_Fields + 1):
    % for i in range(0, N_Robots):
        pick${i}_f${fID}: idle -[Robot${i}_r_x==${fID} and f_${fID}_a_${i}==1 and Robot${i}_r_t==1]> s_pick${i}_f${fID} [f_${fID}_a_${i}=0, f_${fID}_s=${i}]
        fin_pick${i}_f${fID}: s_pick${i}_f${fID} -[Robot${i}_r_t==1 and Robot${i}_r_p==1]> idle [f_${fID}_s=-1]
    % endfor
    % for i in range(0, N_Robots):
        drop${i}_f${fID}: idle -[Robot${i}_r_x==${fID} and f_${fID}_a_${(i+1)%N_Robots}==0 and Robot${i}_r_t==2]> s_drop${i}_f${fID} [f_${fID}_a_${(i+1)%N_Robots}=1, f_${fID}_s=${i}]
        fin_drop${i}_f${fID}: s_drop${i}_f${fID} -[Robot${i}_r_t==2 and Robot${i}_r_p==0]> idle [f_${fID}_s=-1]
    % endfor
% endfor
wait: idle -[${(" and ").join(f"Robot{rID}_r_t==3" for rID in range(0, N_Robots))}]> idle

INITIAL: [${ (', ').join([f"Robot{i}_r_x={Positions[i]}, Robot{i}_r_e={Energy}, Robot{i}_r_p=0, Robot{i}_r_t=0" for i in range(0,N_Robots)]) }, ${ (', ').join([f"f_{i}_s=-1" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}=1" for i, j in itertools.product(range(1, 2), range(0, N_Robots))]) }, ${ (', ').join([f"f_{i}_a_{j}=0" for i, j in itertools.product(range(2, N_Fields + 1), range(0, N_Robots))]) }]
REDUCTION: [${(', ').join([f"f_{N_Fields}_a_{i}" for i in range(1, N_Robots + 1)])}]
COALITION: [${(', ').join([f"Robot{i}" for i in range(N_Robots)])}]
PERSISTENT: [${ (', ').join([f"Robot{i}_r_x, Robot{i}_r_e, Robot{i}_r_p, Robot{i}_r_t" for i in range(0,N_Robots)]) }, ${ (', ').join([f"f_{i}_s" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}" for i, j in itertools.product(range(1, N_Fields + 1), range(0, N_Robots))]) }]
LOGIC: ATL
FORMULA: <<${(', ').join([f"Robot{i}" for i in range(N_Robots)])}>>FG(${(' | ').join([f"f_{N_Fields}_a_{i}=1" for i in range(N_Robots)])})
SHOW_EPISTEMIC: False

%% x - wspolrzedna,
%% e - energia
%% p - plecak
%% t - tryb: 0 - idle, 1 - pick, 2 - drop
%% d - destination (dla kogo drop)
%% s - semafor
%% a - adresat