<%!
    import itertools
%>

SEMANTICS: asynchronous
% for r_id in range(0, N_Robots):
    Agent Robot${r_id}[1]:
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

% endfor

Agent Field[${N_Fields}]:
init: idle
INTERFACE: [${ (', ').join([f"r_{i}_x, r_{i}_t, r_{i}_p, r_{i}_d" for i in range(1,N_Robots+1)]) }]
LOCAL: [aID_f_s, ${ (', ').join([f"aID_f_a_{i}" for i in range(0,N_Robots)]) }]
% for i in range(0, N_Robots):
    pick${i}: idle -[Robot${i}1_r_x==ID and f_ID_a_${i}==1 and Robot${i}1_r_t==1]> s_pick${i} [f_ID_a_${i}=0, f_ID_s=${i}]
    fin_pick${i}: s_pick${i} -[Robot${i}1_r_t==1 and Robot${i}1_r_p==1]> idle [f_ID_s=-1]
% endfor
% for i in range(0, N_Robots):
    drop${i}: idle -[Robot${i}1_r_x==ID and f_ID_a_${(i+1)%N_Robots}==0 and Robot${i}1_r_t==2]> s_drop${i} [f_ID_a_${(i+1)%N_Robots}=1, f_ID_s=${i}]
    fin_drop${i}: s_drop${i} -[Robot${i}1_r_t==2 and Robot${i}1_r_p==0]> idle [f_ID_s=-1]
% endfor

INITIAL: [${ (', ').join([f"Robot{i}1_r_x=1, Robot{i}1_r_e={Energy}, Robot{i}1_r_p=0, Robot{i}1_r_t=0" for i in range(0,N_Robots)]) }, ${ (', ').join([f"f_{i}_s=-1" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}=1" for i, j in itertools.product(range(1, 2), range(0, N_Robots))]) }, ${ (', ').join([f"f_{i}_a_{j}=0" for i, j in itertools.product(range(2, N_Fields + 1), range(0, N_Robots))]) }]
REDUCTION: [${(', ').join([f"f_{N_Fields}_a_{i}" for i in range(1, N_Robots + 1)])}]
COALITION: [${(', ').join([f"Robot{i}1" for i in range(N_Robots)])}]
PERSISTENT: [${ (', ').join([f"Robot{i}1_r_x, Robot{i}1_r_e, Robot{i}1_r_p, Robot{i}1_r_t" for i in range(0,N_Robots)]) }, ${ (', ').join([f"f_{i}_s" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}" for i, j in itertools.product(range(1, N_Fields + 1), range(0, N_Robots))]) }]
LOGIC: ATL
FORMULA: <<${(', ').join([f"Robot{i}1" for i in range(N_Robots)])}>>F(${(' | ').join([f"f_{N_Fields}_a_{i}=1" for i in range(0, N_Robots)])})
%% FORMULA: <<Robot01>>(r1_e>0 && r2_e>0)U(p3_a1==1 || p3_a2==1)
SHOW_EPISTEMIC: False

%% x - wspolrzedna,
%% e - energia
%% p - plecak
%% t - tryb: 0 - idle, 1 - pick, 2 - drop
%% d - destination (dla kogo drop)
%% s - semafor
%% a - adresat