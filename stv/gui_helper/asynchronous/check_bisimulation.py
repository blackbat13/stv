import sys
import json
from stv.models.asynchronous.parser import GlobalModelParser
from stv.models import SimpleModel

model1FilePath = sys.argv[3]
model2FilePath = sys.argv[4]
relationPath = sys.argv[5]

global_model1 = GlobalModelParser().parse(model1FilePath)
global_model1.generate(reduction=False)
global_model1.generate_local_models()

global_model2 = GlobalModelParser().parse(model2FilePath)
global_model2.generate(reduction=False)
global_model2.generate_local_models()

winning = []

mapping, coalition = SimpleModel.parse_mapping_sets(relationPath)

mapping2, coalition2 = SimpleModel.parse_mapping(relationPath)

bis_result = global_model1.model.check_bisimulation(global_model2.model, mapping2, coalition2)

# # @todo real computation of correspondingNodeIds
# correspondingNodeIds = []
# # n = 11
#
# for pair in mapping:
#
#
# for state_id in mapping:
#     for sim_state_id in mapping[state_id]:
#         correspondingNodeIds.append([state_id, sim_state_id])

# for i in range(3, 7):
#     correspondingNodeIds.append([i, n - i - 1])

print(json.dumps({
    "model1": global_model1.model.js_dump_model(winning),
    "model2": global_model2.model.js_dump_model(winning),
    "mapping": mapping,
    "bisimulation_result": bis_result,
    "coalition": global_model1.coalition_ids_to_str(coalition),
}))
