import sys
import json
from stv.models.asynchronous.parser import GlobalModelParser

mode = sys.argv[3]  # "global" | "reduced"
filePath = sys.argv[4]
v = int(sys.argv[5])

global_model = GlobalModelParser().parse(filePath)
global_model.generate(reduction=False)
global_model.generate_local_models()

if v == 1:
    atl_model_global = global_model.model.to_atl_imperfect()
else:
    atl_model_global = global_model.model.to_atl_perfect()

winning_global = global_model.get_formula_winning_states()
result_global = atl_model_global.minimum_formula_many_agents([global_model.get_agent()], winning_global)
# print(result_global)
reduced_model = None
if mode == "reduced":
    reduced_model = GlobalModelParser().parse(filePath)
    reduced_model.generate(reduction=True)
    winning_reduced = reduced_model.get_formula_winning_states()
    if v == 1:
        atl_model_reduced = reduced_model.model.to_atl_imperfect(reduced_model.get_actions())
    else:
        atl_model_reduced = reduced_model.model.to_atl_perfect(reduced_model.get_actions())

    result_reduced = atl_model_reduced.minimum_formula_many_agents([reduced_model.get_agent()], winning_reduced)


# for state in global_model._states:
#     state.print()
# global_model.print()
localModels = []
localModelNames = []
for localModel in global_model._local_models:
    localModels.append(localModel._model.js_dump_model(winning=[], epistemic=True))
    localModelNames.append(localModel._agent_name)

print(json.dumps({
    "localModels": localModels,
    "localModelNames": localModelNames,
    "globalModel": global_model.model.js_dump_strategy_objective(atl_model_global.strategy),
    "reducedModel": reduced_model.model.js_dump_strategy_objective(atl_model_reduced.strategy) if reduced_model else None,
    "globalResult": 0 in result_global,
    "reducedResult": 0 in result_reduced if reduced_model else None,
    "strategy": atl_model_global.strategy,
    "globalStatesCount": len(result_global),
    "reducedStatesCount": len(result_reduced) if reduced_model else None,
}))
