from stv.models.asynchronous.parser import GlobalModelParser
from stv.parsers import FormulaParser
from abstraction.abstraction import Abstraction


voter = 1
cand = 2
enable_trace = True
filename_in =  f"tests_abstraction/example.txt"
#filename_in =  f"tests_abstraction/Selene_{voter}_{cand}.txt"
filename_out = f"{filename_in.rstrip('.txt')}_abstracted.txt"
filename_trace = f"{filename_in.rstrip('.txt')}_trace.txt"
#agent_name = "Voter"
agent_name = "Template"
#variable = "Voter1_vote"
variable = "x"
abstraction = Abstraction(filename_in,agent_name,variable,enable_trace=enable_trace)
abstraction.generate()
print("transition closure of relation R : ",abstraction.compute_variables())
abstraction.save_trace(filename_trace)
abstraction.save_to_file(filename_out)



