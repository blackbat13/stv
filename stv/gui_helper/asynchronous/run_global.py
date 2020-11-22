import sys
import json
from stv.models.asynchronous.parser import GlobalModelParser

filePath = sys.argv[3]

global_model = GlobalModelParser().parse(filePath)
global_model.generate(reduction=False)
global_model.generate_local_models()

winning = []

# for state in global_model._states:
#     state.print()
# global_model.print()
localModels = []
for localModel in global_model._local_models:
    localModels.append(localModel._model.js_dump_model([]))

print(json.dumps({
    "localModels": localModels,
    "globalModel": global_model.model.js_dump_model(winning),
}))
