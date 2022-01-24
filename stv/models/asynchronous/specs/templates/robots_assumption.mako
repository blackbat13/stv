<%!
    import itertools
%>

SEMANTICS: synchronous
Agent Robot0[1]:
init: idle
INTERFACE: [${ (', ').join([f"f_{i}_a_1, f_{i}_a_2, f_{i}_s" for i in range(1,N_Fields+1)]) }]
LOCAL: [aID_r_x, aID_r_e, aID_r_t, aID_r_p]
move_f: idle -[aID_r_x<${N_Fields} and aID_r_e>0 and aID_r_t==0]> idle [aID_r_x+=1, aID_r_e-=1]
move_b: idle -[aID_r_x>1 and aID_r_e>0 and aID_r_t==0]> idle [aID_r_x-=1, aID_r_e-=1]
% for i in range(1, N_Fields+1):
    pick${i}: idle -[aID_r_x==${i} and f_${i}_a_0==1 and aID_r_p==0 and aID_r_e>0]> s_pick${i} [aID_r_t=1]
    cont_pick${i}: s_pick${i} -[f_${i}_s==0]> cont_pick${i} [aID_r_p=1]
    fin_pick${i}: cont_pick${i} -[f_${i}_s!=0]> idle [aID_r_t=0]
% endfor
% for i in range(1, N_Fields+1):
    drop${i}: idle -[aID_r_x==${i} and aID_r_p==1 and f_${i}_a_1==0]> s_drop${i} [aID_r_t=2]
    cont_drop${i}: s_drop${i} -[f_${i}_s==0]> cont_drop${i} [aID_r_p=0]
    fin_drop${i}: cont_drop${i} -[f_${i}_s!=0]> idle [aID_r_t=0]
% endfor

Agent Assumption[1]:
init: idle
% for i in range(1, N_Fields + 1):
    pick_0_${i}: idle -[Robot01_r_x==${i} and f_${i}_a_0==1 and Robot01_r_t==1]> s_pick_0_${i} [f_${i}_a_0=0, f_${i}_s=0]
    fin_pick_0_${i}: s_pick_0_${i} -[Robot01_r_t==1 and Robot01_r_p==1]> idle [f_${i}_s=-1]
    drop_0_${i}: idle -[Robot01_r_x==${i} and f_${i}_a_1==0 and Robot01_r_t==2]> s_drop_0_${i} [f_${i}_a_1=1, f_${i}_s=0]
    fin_drop_0_${i}: s_drop_0_${i} -[Robot01_r_t==2 and Robot01_r_p==0]> idle [f_${i}_s=-1]
    % for j in range(1, N_Robots):
        pick_${j}_${i}: idle -[Robot${j}1_r_x==${i} and f_${i}_a_${j}==1 and Robot${j}1_r_p==0]> idle [f_${i}_a_${j}=0, Robot${j}1_r_p=1]
        drop_${j}_${i}: idle -[Robot${j}1_r_x==${i} and f_${i}_a_${(j+1)%N_Robots}==0 and Robot${j}1_r_p==1]> idle [f_${i}_a_${(j+1)%N_Robots}=1, Robot${j}1_r_p=0]
    % endfor
% endfor
% for j in range(1, N_Robots):
    move_f: idle -[Robot${j}1_r_x<${N_Fields} and Robot${j}1_r_e>0]> idle [Robot${j}1_r_x+=1, Robot${j}1_r_e-=1]
    move_b: idle -[Robot${j}1_r_x>1 and Robot${j}1_r_e>0]> idle [Robot${j}1_r_x-=1, Robot${j}1_r_e-=1]
% endfor

INITIAL: [${ (', ').join([f"Robot{i}1_r_x=1, Robot{i}1_r_e={Energy}, Robot{i}1_r_p=0, Robot{i}1_r_t=0" for i in range(0,N_Robots)]) }, ${ (', ').join([f"f_{i}_s=-1" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}=1" for i, j in itertools.product(range(1, 2), range(0, N_Robots))]) }, ${ (', ').join([f"f_{i}_a_{j}=0" for i, j in itertools.product(range(2, N_Fields + 1), range(0, N_Robots))]) }]
REDUCTION: [${(', ').join([f"f_{N_Fields}_a_{i}" for i in range(1, N_Robots + 1)])}]
COALITION: [Robot01]
PERSISTENT: [${ (', ').join([f"Robot{i}1_r_x, Robot{i}1_r_e, Robot{i}1_r_p, Robot{i}1_r_t" for i in range(0,N_Robots)]) }, ${ (', ').join([f"f_{i}_s" for i in range(1,N_Fields+1)]) }, ${ (', ').join([f"f_{i}_a_{j}" for i, j in itertools.product(range(1, N_Fields + 1), range(0, N_Robots))]) }]
LOGIC: ATL
FORMULA: <<Robot01>>F(${(' | ').join([f"f_{N_Fields}_a_{i}=1" for i in range(0, N_Robots)])})
%% FORMULA: <<Robot01>>(r1_e>0 && r2_e>0)U(p3_a1==1 || p3_a2==1)
SHOW_EPISTEMIC: False