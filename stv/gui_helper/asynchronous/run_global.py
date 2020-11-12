import sys
import json
from stv.models.asynchronous.parser import GlobalModelParser

filePath = sys.argv[3]

global_model = GlobalModelParser().parse(filePath)
global_model.generate(reduction=False)

winning = []

# for state in global_model._states:
#     state.print()
# global_model.print()
localModels = []
for localModel in global_model._local_models:
    localModels.append(global_model.model.js_dump_model(winning))

print(json.dumps({
    "localModels": localModels,
    "globalModel": global_model.model.js_dump_model(winning),
}))
