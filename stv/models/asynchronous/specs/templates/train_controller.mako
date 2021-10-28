Agent Train[${N_Trains}]:
init: wait
shared in_aID: wait -> tunnel [aID_in=True]
shared out_aID: tunnel -> away [aID_out=True]
return: away -> wait [aID_return=True]

Agent Controller[${N_Controllers}]:
init: green
% for i in range(1,N_Trains+1):
    shared in_Train${i}: green -> red
    shared back_Train${i}: red -> green
% endfor

%% REDUCTION: [${ (', ').join([f"in_Train{i}" for i in range(1,N_Trains+1)]) }]
%% COALITION: [${ (', ').join([f"Controller{i}" for i in range(1,N_Controllers+1)])}]
%% LOGIC: CTL
%% FORMULA: AF(${ (' | ').join([f"Train{i}_in=True" for i in range(1,N_Trains+1)])})
REDUCTION: [Train1_return]
COALITION: [Train1]
LOGIC: ATL
FORMULA: <<Train1>>F(Train1_return=True)