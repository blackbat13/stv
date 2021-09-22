Agent Train[${N_Trains}]:
init: wait
shared a1_aID: wait -> tunnel [aID_in=true]
shared a2_aID: tunnel -> away [aID_in=false]
a3: away -> wait

Agent Controller[${N_Controllers}]:
init: green
% for i in range(1,N_Trains+1):
    shared a1_Train${i}: green -> red
    shared a2_Train${i}: red -> green
% endfor

REDUCTION: [${ (', ').join([f"in_Train{i}" for i in range(1,N_Trains+1)]) }]
COALITION: [${ (', ').join([f"Controller{i}" for i in range(1,N_Controllers+1)])}]
LOGIC: CTL
FORMULA: AF(${ (' | ').join([f"Train{i}_in=True" for i in range(1,N_Trains+1)])})