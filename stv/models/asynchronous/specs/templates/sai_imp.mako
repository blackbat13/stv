<%
    agents_ids = [i for i in range(1, N_AI + 1)]
    imp_right = agents_ids[IMP % N_AI]
    imp_left = agents_ids[IMP - 2]
%>
%for index, agent_id in enumerate(agents_ids):
    %if agent_id != IMP:
        <%
            agent_right_id = agents_ids[(index + 1) % N_AI]
            agent_left_id = agents_ids[index - 1]
        %>
        Agent AI${agent_id}:
        init: start
        %% ---Phase1: Gathering data---
        start_gathering_data: start -> gather
        gather_data: gather -[AI${agent_id}_data<2]> gather [AI${agent_id}_data+=1]
        %% 1: Incomplete data
        stop_gathering_data: gather -[AI${agent_id}_data < 1]> data_ready [AI${agent_id}_data=0, AI${agent_id}_data_completion=1]
        %% 2: Complete data
        stop_gathering_data: gather -[1 <= AI${agent_id}_data < 2]> data_ready [AI${agent_id}_data=0, AI${agent_id}_data_completion=2]
        %% 3: Too much data
        stop_gathering_data: gather -[2 <= AI${agent_id}_data]> data_ready [AI${agent_id}_data=0, AI${agent_id}_data_completion=3]
        skip_gathering_data: start -> data_ready
        %% ---Phase2: Learning (building local model)---
        start_learning: data_ready -> learn
        keep_learning: learn -[AI${agent_id}_information < 2]> learn [AI${agent_id}_information+=AI${agent_id}_data_completion]
        %% 1: Incomplete model
        stop_learning: learn -[AI${agent_id}_information < 1 and AI${agent_id}_model_quality > 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=1, AI${agent_id}_model_quality-=1]
        stop_learning: learn -[AI${agent_id}_information < 1 and AI${agent_id}_model_quality <= 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=1]
        %% 2: Complete model
        stop_learning: learn -[1 <= AI${agent_id}_information < 2 and AI${agent_id}_model_quality < ${MAX_MODEL_QUALITY}]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=2, AI${agent_id}_model_quality+=1]
        stop_learning: learn -[1 <= AI${agent_id}_information < 2 and AI${agent_id}_model_quality >= ${MAX_MODEL_QUALITY}]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=2]
        %% 3: Overtrained model
        stop_learning: learn -[2 <= AI${agent_id}_information and AI${agent_id}_model_quality > 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=3, AI${agent_id}_model_quality-=1]
        stop_learning: learn -[2 <= AI${agent_id}_information and AI${agent_id}_model_quality <= 0]> educated [AI${agent_id}_information=0, AI${agent_id}_model_status=3]
        skip_learning: data_ready -> sharing
        %% ---Phase3: Sharing local models---
        start_sharing: educated -> sharing
        %% Share local model and get average quality of both models
        %if agent_id % 2 == 0:
            %% send right
            shared share_${agent_id}_with_${agent_right_id}: sharing -> sharing2
            %% receive left
            shared share_${agent_left_id}_with_${agent_id}: sharing2 -> sharing3 [AI${agent_id}_model_quality=%AI${agent_left_id}_model_quality]
        %else:
            %% receive left
            shared share_${agent_left_id}_with_${agent_id}: sharing -> sharing2 [AI${agent_id}_model_quality=%AI${agent_left_id}_model_quality]
            %% send right
            shared share_${agent_id}_with_${agent_right_id}: sharing2 -> sharing3
        %endif
        end_sharing: sharing3 -> end
        %% ---Phase4: End---
        wait: end -> end
        repeat: end -> learn
    %endif

%endfor
Agent IMP:
init: start
shared share_${imp_left}_with_${IMP}: start -> start
shared share_${IMP}_with_${imp_right}: start -> start


PERSISTENT: [${ (', ').join([f"AI{i}_information, AI{i}_data, AI{i}_data_completion, AI{i}_model_status, AI{i}_model_quality" for i in range(1, N_AI + 1)]) }]
INITIAL: [${ (', ').join([f"AI{i}_information=0, AI{i}_data=0, AI{i}_data_completion=0, AI{i}_model_status=0, AI{i}_model_quality=0" for i in range(1, N_AI + 1)]) }]
FORMULA: <<AI1>>F(${(' & ').join([f"AI{i}_model_quality>1" for i in range(1, N_AI + 1)])})
SHOW_EPISTEMIC: False