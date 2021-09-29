<%!
    import itertools
%>

SEMANTICS: synchronous
Agent Robot[${N_Robots}]:
init: idle
INTERFACE: [${ (', ').join([f"f_{i}_a_1, f_{i}_a_2, f_{i}_s" for i in range(1,N_Fields+1)]) }]
LOCAL: [r_ID_x, r_ID_e, r_ID_t, r_ID_p]
move_f: idle -[r_ID_x<3 and r_ID_e>0 and r_ID_t==0]> idle [r_ID_x+=1, r_ID_e-=1]
move_b: idle -[r_ID_x>1 and r_ID_e>0 and r_ID_t==0]> idle [r_ID_x-=1, r_ID_e-=1]
% for i in range(1, N_Fields+1):
    pick${i}: idle -[r_ID_x==1 and f_${i}_a_ID==1 and r_ID_p==0]> s_pick${i} [r_ID_t=1]
    cont_pick${i}: s_pick${i} -[f_${i}_s==ID]> cont_pick${i} [r_ID_p=1]
    fin_pick${i}: cont_pick1 -[f_${i}_s!=ID]> idle [r_ID_t=0]
% endfor
% for i in range(1, N_Fields+1):
    % for j in range(1, N_Robots + 1):
        drop${i}_a${j}: idle -[r_ID_x==1 and r_ID_p==1 and f_${i}_a_${j}==0]> s_drop${i} [r_ID_t=2, r_ID_d=${j}]
        cont_drop${i}_a${j}: s_drop${i} -[f_${i}_s==ID]> cont_drop${i} [r_ID_p=0]
        fin_drop${i}_a${j}: cont_drop${i} -[f_${i}_s!=ID]> idle [r_ID_t=0]
    % endfor
% endfor

Agent Field[${N_Fields}]:
init: idle
INTERFACE: [${ (', ').join([f"r_{i}_x, r_{i}_t, r_{i}_p, r_{i}_d" for i in range(1,N_Robots+1)]) }]
LOCAL: [f_ID_s, ${ (', ').join([f"f_ID_a_{i}" for i in range(1,N_Robots+1)]) }]
% for i in range(1, N_Robots + 1):
    pick${i}: idle -[r_${i}_x==ID and f_ID_a_${i}==1 and r_${i}_t==1]> s_pick${i} [f_ID_a_${i}=0, f_ID_s=${i}]
    fin_pick${i}: s_pick${i} -[r_${i}_t==1 and r_${i}_p==1]> idle [f_ID_s=0]
% endfor
% for i in range(1, N_Robots + 1):
    % for j in range(1, N_Robots + 1):
        drop${i}_a${j}: idle -[r_${i}_x==ID and f_ID_a_${j}==0 and r_${i}_t==2 and r_${i}_d==${j}]> s_drop${i}_a${j} [f_ID_a_${j}=1, f_ID_s=${i}]
        fin_drop${i}_a${j}: s_drop${i}_a${j} -[r_${i}_t==2 and r_${i}_p==0]> idle [f_ID_s=0]
    % endfor
% endfor

INITIAL: [${ (', ').join([f"r_{i}_x=1, r_{i}_e=5, r_{i}_p=0, r_{i}_t=0, r_{i}_d=0" for i in range(1,N_Robots+1)]) }, ${ (', ').join([f"f_{i}_s=0" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}=1" for i, j in itertools.product(range(1, 2), range(1, N_Robots + 1))]) }, ${ (', ').join([f"f_{i}_a_{j}=0" for i, j in itertools.product(range(2, N_Fields + 1), range(1, N_Robots + 1))]) }]
REDUCTION: []
COALITION: [Robot1]
PERSISTENT: [${ (', ').join([f"r_{i}_x, r_{i}_e, r_{i}_p, r_{i}_t, r_{i}_d" for i in range(1,N_Robots+1)]) }, ${ (', ').join([f"f_{i}_s" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}" for i, j in itertools.product(range(1, N_Fields + 1), range(1, N_Robots + 1))]) }]
LOGIC: ATL
FORMULA: <<Robot1>>F(f_3_a_1=1 || f_3_a_2=1)
%% FORMULA: <<Robot1>>(r1_e>0 && r2_e>0)U(p3_a1==1 || p3_a2==1)
SHOW_EPISTEMIC: False

%% x - wspolrzedna,
%% e - energia
%% p - plecak
%% t - tryb: 0 - idle, 1 - pick, 2 - drop
%% d - destination (dla kogo drop)
%% s - semafor
%% a - adresat