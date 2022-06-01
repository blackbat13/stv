Agent AI[${N_AI}]:
init: start
%% ---Phase1: Gathering data---
start_gathering_data: start -> gather
gather_data: gather -[aID_data<10]> gather [aID_data+=1]
%% 1: Incomplete data
stop_gathering_data: gather -[aID_data<5]> data_ready [aID_data=0,aID_data_completion=1]
%% 2: Complete data
stop_gathering_data: gather -[5<=aID_data<8]> data_ready [aID_data=0,aID_data_completion=2]
%% 3: Too much data
stop_gathering_data: gather -[8<=aID_data]> data_ready [aID_data=0,aID_data_completion=3]
skip_gathering_data: start -> data_ready
%% ---Phase2: Learning (building local model)---
start_learning: data_ready -> learn
keep_learning: learn -[aID_information<10]> learn [aID_information+=aID_data_completion]
%% 1: Incomplete model
stop_learning: learn -[aID_information<7]> educated [aID_information=0,aID_model_status=1]
%% 2: Complete model
stop_learning: learn -[7<=aID_information<8]> educated [aID_information=0,aID_model_status=2]
%% 3: Overtrained model
stop_learning: learn -[8<=aID_information]> educated [aID_information=0,aID_model_status=3]
skip_learning: data_ready -> educated
%% ---Phase3: Sharing local models---
shared share: educated -> end
%% ---Phase4: End---
wait: end -> end

PERSISTENT: [${ (', ').join([f"AI{i}_information, AI{i}_data, AI{i}_data_completion, AI{i}_model_status, AI{i}_model_quality" for i in range(N_AI)]) }]
INITIAL: [${ (', ').join([f"AI{i}_information=0, AI{i}_data=0, AI{i}_data_completion=0, AI{i}_model_status=0" for i in range(N_AI)]) }]
FORMULA: <<AI1>>F(AI1_model_status=1)
SHOW_EPISTEMIC: False