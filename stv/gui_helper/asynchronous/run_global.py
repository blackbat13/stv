import sys
import json
from stv.models.asynchronous.parser import GlobalModelParser

mode = sys.argv[3]  # "global" | "reduced"
filePath = sys.argv[4]

global_model = GlobalModelParser().parse(filePath)
global_model.generate(reduction=False)
global_model.generate_local_models()

reduced_model = None
if mode == "reduced":
    reduced_model = GlobalModelParser().parse(filePath)
    reduced_model.generate(reduction=True)

winning = []

# for state in global_model._states:
#     state.print()
# global_model.print()
localModels = []
localModelNames = []
for localModel in global_model._local_models:
    localModels.append(localModel._model.js_dump_model(winning=[], epistemic=False))
    localModelNames.append(localModel._agent_name)

print(json.dumps({
    "localModels": localModels,
    "localModelNames": localModelNames,
    "globalModel": global_model.model.js_dump_model(winning, False, True),
    "reducedModel": reduced_model.model.js_dump_model(winning, False, True) if reduced_model else None,
}))
