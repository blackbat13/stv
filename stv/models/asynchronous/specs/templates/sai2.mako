%for agent_id in range(1, N_AI + 1):
    Agent AI${agent_id}:
    init: start
    %% ---Phase1: Gathering data---
    start_gathering_data: start -> gather
    gather_data: gather -[AI${agent_id}_data<10]> gather [AI${agent_id}_data+=1]
    %% 1: Incomplete data
    stop_gathering_data: gather -[AI${agent_id}_data < 5]> data_ready [AI${agent_id}_data=0, AI${agent_id}_data_completion=1]
    %% 2: Complete data
    stop_gathering_data: gather -[5 <= AI${agent_id}_data < 8]> data_ready [AI${agent_id}_data=0, AI${agent_id}_data_completion=2]
    %% 3: Too much data
    stop_gathering_data: gather -[8 <= AI${agent_id}_data]> data_ready [AI${agent_id}_data=0, AI${agent_id}_data_completion=3]
    skip_gathering_data: start -> data_ready
    %% ---Phase2: Learning (building local model)---
    start_learning: data_ready -> learn
    keep_learning: learn -[AI${agent_id}_information < 10]> learn [AI${agent_id}_information+=AI${agent_id}_data_completion]
    %% 1: Incomplete model
    stop_learning: learn -[AI${agent_id}_information < 7 and AI${agent_id}_model_quality > 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=1, AI${agent_id}_model_quality-=1]
    stop_learning: learn -[AI${agent_id}_information < 7 and AI${agent_id}_model_quality <= 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=1]
    %% 2: Complete model
    stop_learning: learn -[7 <= AI${agent_id}_information < 8 and AI${agent_id}_model_quality < ${MAX_MODEL_QUALITY}]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=2, AI${agent_id}_model_quality+=1]
    stop_learning: learn -[7 <= AI${agent_id}_information < 8 and AI${agent_id}_model_quality >= ${MAX_MODEL_QUALITY}]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=2]
    %% 3: Overtrained model
    stop_learning: learn -[8 <= AI${agent_id}_information and AI${agent_id}_model_quality > 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=3, AI${agent_id}_model_quality-=1]
    stop_learning: learn -[8 <= AI${agent_id}_information and AI${agent_id}_model_quality <= 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=3]
    skip_learning: data_ready -> sharing
    %% ---Phase3: Sharing local models---
    start_sharing: educated -> sharing
    %% Share local model and get average quality of both models
    %for db_id in range(1, N_DB + 1):
        shared AI${agent_id}_send_to_DB${db_id}: sharing -> sharing
        shared AI${agent_id}_get_from_DB${db_id}: sharing -> sharing [AI${agent_id}_model_quality=%DB${db_id}_model_quality]
    %endfor
    end_sharing: sharing -> end
    %% ---Phase4: End---
    wait: end -> end
    repeat: end -> learn

%endfor

%for agent_id in range(1, N_DB + 1):
    Agent DB${agent_id}:
    init: start
    %for ai_id in range(1, N_AI + 1):
        shared AI${ai_id}_send_to_DB${agent_id}: start -> start [DB${agent_id}_model_quality=%AI${ai_id}_model_quality]
        shared AI${ai_id}_get_from_DB${agent_id}: start -> start
    %endfor

%endfor

PERSISTENT: [${ (', ').join([f"AI{i}_information, AI{i}_data, AI{i}_data_completion, AI{i}_model_status, AI{i}_model_quality" for i in range(1, N_AI + 1)]) }, ${(', ').join([f"DB{i}_model_quality" for i in range(1, N_DB + 1)])}]
INITIAL: [${ (', ').join([f"AI{i}_information=0, AI{i}_data=0, AI{i}_data_completion=0, AI{i}_model_status=0, AI{i}_model_quality=0" for i in range(1, N_AI + 1)]) }, ${(', ').join([f"DB{i}_model_quality=0" for i in range(1, N_DB + 1)])}]
FORMULA: <<AI1>>F(DB1_model_quality>1)
SHOW_EPISTEMIC: False