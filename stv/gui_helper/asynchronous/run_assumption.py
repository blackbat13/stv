import sys
import json
from stv.models.asynchronous.parser import AssumptionParser

modelStr = sys.argv[3]

models, global_model = AssumptionParser().parseBase64String(modelStr)

for model in models:
    model.generate()

global_model.generate()

print(json.dumps({
    "specs": [f"{model}" for model in models],
    "localModels": [model.model.js_dump_model(model.get_formula_winning_states(), model._show_epistemic) for model in models],
    "localModelNames": [model.name for model in models],
    "globalModel": global_model.model.js_dump_model(global_model.get_formula_winning_states(), global_model._show_epistemic)
}))
