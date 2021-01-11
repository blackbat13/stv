import sys
import json
from stv.models.asynchronous.parser import GlobalModelParser

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

# @todo real computation of correspondingNodeIds
correspondingNodeIds = []
n = 11
for i in range(3, 7):
    correspondingNodeIds.append([i, n - i - 1])

print(json.dumps({
    "model1": global_model1.model.js_dump_model(winning),
    "model2": global_model2.model.js_dump_model(winning),
    "correspondingNodeIds": correspondingNodeIds,
}))
