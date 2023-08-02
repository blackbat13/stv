import sys
import json
from stv.models.asynchronous.parser import GlobalModelParser
from stv.comparing_strats import StrategyComparer

params = json.loads(sys.argv[3])
if(params["fileContent"]):
    global_model = GlobalModelParser().parseFromString(params["fileContent"])
else:
    global_model = GlobalModelParser().parse(params["filePath"])
global_model.generate(reduction=False)
global_model.generate_local_models()
winning_global = global_model.get_formula_winning_states()

strategy_comparer_global = StrategyComparer(global_model.model, global_model.get_actions()[global_model.get_agent()])

if params["heuristic"] == '0':
    (result_global, strategy_global) = strategy_comparer_global.domino_dfs(0, set(winning_global),
                                                                           [global_model.get_agent()],
                                                                           strategy_comparer_global.basic_h)
elif params["heuristic"] == '1':
    (result_global, strategy_global) = strategy_comparer_global.domino_dfs(0, set(winning_global),
                                                                           [global_model.get_agent()],
                                                                           strategy_comparer_global.control_h)
elif params["heuristic"] == '2':
    (result_global, strategy_global) = strategy_comparer_global.domino_dfs(0, set(winning_global),
                                                                           [global_model.get_agent()],
                                                                           strategy_comparer_global.epistemic_h)
elif params["heuristic"] == '3':
    (result_global, strategy_global) = strategy_comparer_global.domino_dfs(0, set(winning_global),
                                                                           [global_model.get_agent()],
                                                                           strategy_comparer_global.visited_states_h)

reduced_model = None
if params["mode"] == "reduced":
    if(params["filePath"]=="raw"):
        reduced_model = GlobalModelParser().parseFromString(params["fileContent"])
    else:
        reduced_model = GlobalModelParser().parse(params["filePath"])
    reduced_model.generate(reduction=True)
    winning_reduced = reduced_model.get_formula_winning_states()

    strategy_comparer_reduced = StrategyComparer(reduced_model.model,
                                                 reduced_model.get_actions()[reduced_model.get_agent()])

    if params["heuristic"] == 0:
        (result_reduced, strategy_reduced) = strategy_comparer_reduced.domino_dfs(0, set(winning_reduced),
                                                                                  [reduced_model.get_agent()],
                                                                                  strategy_comparer_reduced.basic_h)
    elif params["heuristic"] == 1:
        (result_reduced, strategy_reduced) = strategy_comparer_reduced.domino_dfs(0, set(winning_reduced),
                                                                                  [reduced_model.get_agent()],
                                                                                  strategy_comparer_reduced.control_h)
    elif params["heuristic"] == 2:
        (result_reduced, strategy_reduced) = strategy_comparer_reduced.domino_dfs(0, set(winning_reduced),
                                                                                  [reduced_model.get_agent()],
                                                                                  strategy_comparer_reduced.epistemic_h)
    elif params["heuristic"] == 3:
        (result_reduced, strategy_reduced) = strategy_comparer_reduced.domino_dfs(0, set(winning_reduced),
                                                                                  [reduced_model.get_agent()],
                                                                                  strategy_comparer_reduced.visited_states_h)

localModels = []
localModelNames = []
for localModel in global_model._local_models:
    localModels.append(localModel._model.js_dump_model(winning=[], epistemic=True))
    localModelNames.append(localModel._agent_name)

print(json.dumps({
    "localModels": localModels,
    "localModelNames": localModelNames,
    "globalModel": global_model.model.js_dump_strategy_objective(strategy_global),
    "reducedModel": reduced_model.model.js_dump_strategy_objective(strategy_reduced) if reduced_model else None,
    "globalResult": result_global,
    "reducedResult": result_reduced if reduced_model else None,
    "formula": global_model.formula,
}))
