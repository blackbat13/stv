from stv.models.asynchronous.parser import GlobalModelParser
from stv.parsers import FormulaParser
from abstraction.abstraction import Abstraction


"""
Abstraction Tests

examples -> x

shared_variable/transitions, 2/4_agents -> x_p1

Selene_1_2 -> Voter1_Vote

"""

voter = 1
cand = 2
enable_trace = True
#filename =  f"tests_abstraction/example.txt"
#filename =  f"tests_abstraction/example-inequalities.txt"
#filename =  f"tests_abstraction/example-no-bounded-var.txt"
#filename =  f"tests_abstraction/example-redundant-transitions.txt"
#filename =  f"tests_abstraction/shared-variable.txt"
#filename =  f"tests_abstraction/2_agents.txt"
#filename =  f"tests_abstraction/4_agents.txt"
filename =  f"tests_abstraction/Selene_{voter}_{cand}.txt"
#var = "x"
#var = "x_p1"
var = "Voter1_vote"
abstraction = Abstraction(filename,var,enable_trace=enable_trace)
print(str(abstraction))
variables = abstraction.compute_variables()
print()
print(f"abstracting variable {var}...")
abstraction.compute()
print(f"abstraction completed !")
print()
abstraction.save()

