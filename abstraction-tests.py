from stv.models.asynchronous.parser import GlobalModelParser
from stv.parsers import FormulaParser
from abstraction.abstraction import Abstraction


voter = 1
cand = 2
enable_trace = True
#filename_in =  f"tests_abstraction/example.txt"
filename_in =  f"tests_abstraction/Selene_{voter}_{cand}.txt"
filename_out = f"{filename_in.rstrip('.txt')}_abstracted.txt"
filename_trace = f"{filename_in.rstrip('.txt')}_trace.txt"
agent_name = "Voter"
#agent_name = "Template"	
var = "Voter1_vote"
#var = "x"
print(f"parsing file {filename_in}...")
abstraction = Abstraction(filename_in,agent_name,var,enable_trace=enable_trace)
print("parsing completed\n")
variables = abstraction.compute_variables()
print(f"closure of {{{ var}}}: {abstraction.compute_variables()}\n")
print(f"abstracting variable {var}...")
abstraction.generate()
print(f"abstraction completed")
abstraction.save_trace(filename_trace)
abstraction.save_to_file(filename_out)
#abstraction.save_concrete_local_model("concrete_lmodel_end.txt")
print(f"Local abstracted model saved in {filename_out}\n")






#------------------------------------------Chaining abstraction (TODO) ----------------------------------------------------------------------


# Computation of transitive closure of {abstracted_variable} for relation "uRv iif there exists a post-condition u=f(v)" should not be a method of Abstraction [matter of readability]




# voter = 1
# cand = 2
# i=0
# filename =  f"tests_abstraction/example_loop.txt"
# enable_trace= True
# tracefile = f"tests_abstraction/example_loop_trace.txt"
# # filename =  f"tests_abstraction/Selene_{voter}_{cand}.txt"
# # agent_name = "Voter"
# agent_name = "Template"
# # variable = "Voter1_vote"
# variable = "x"
# print("parsing file {filename}...")
# abstraction = Abstraction(filename,agent_name,variable,enable_trace=enable_trace)
# print("parsing completed\n")
# variables = abstraction.compute_variables()
# print(f"closure of {{{ variable}}}: {abstraction.compute_variables()}\n")
# print(f"abstracting variable {variable}...")
# abstraction.generate()
# print(f"abstraction completed\n")
# abstraction.save_to_file(f"{filename}_{i+1}")
# if enable_trace:
# 	abstraction.save_trace(f"{tracefile}_{i}{i+1}")
# i+=1
# for var in variables:
# 	if var!=variable:
# 		print(f"parsing file {filename}_{i}...")
# 		abstraction = Abstraction(f"{filename}_{i}",agent_name,var,enable_trace=enable_trace)
# 		print("parsing completed\n")
# 		print(f"abstracting variable {var}...")
# 		abstraction.generate()
# 		print(f"abstraction completed\n")
# 		abstraction.save_to_file(f"{filename}_{i+1}")
# 		print(f"Local abstracted model saved in {filename}_{i+1}\n")
# 		if enable_trace:
# 			abstraction.save_trace(f"{tracefile}_{i}{i+1}")
# 		i+=1
	
