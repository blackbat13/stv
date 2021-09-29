SEMANTICS: synchronous
Agent Train[${N_Trains}]:
init: wait
wt: wait -[s==ID]> tunnel [x_ID=1]
ta: tunnel -> away [x_ID=2]
% for i in range(N_Trains+1):
    aw${i}: away -[s==${i}]> wait [x_ID=0]
% endfor

Agent Controller[${N_Controllers}]:
init: idle
% for i in range(1,N_Trains+1):
    it${i}: idle -[x_${i}==0]> t${i} [s=${i}]
    t${i}i: t${i} -[x_${i}==2]> idle [s=0]
% endfor

REDUCTION: []
COALITION: [${ (', ').join([f"Train{i}" for i in range(1,N_Trains+1)])}]
PERSISTENT: [s, ${ (', ').join([f"x_{i}" for i in range(1,N_Trains+1)])}]
LOGIC: ATL
INITIAL: [s=0, ${ (', ').join([f"x_{i}=0" for i in range(1,N_Trains+1)])}]
FORMULA: <<${ (', ').join([f"Train{i}" for i in range(1,N_Trains+1)])}>>F((x_1=1 & x_2=2) | (x_2=1 & x_1=2))
SHOW_EPISTEMIC: False