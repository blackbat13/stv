import json
from stv.models.asynchronous.parser import GlobalModelParser

global_model = GlobalModelParser().parse("../stv/models/asynchronous/train_controller.txt")
global_model.generate(reduction=False)

winning = []

# for state in global_model._states:
#     state.print()
# global_model.print()
print(global_model.model.js_dump_model(winning))
