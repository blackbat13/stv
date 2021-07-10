from stv.models.asynchronous import GlobalModel,LocalModel, LocalTransition
from stv.models.asynchronous.parser import GlobalModelParser  
from typing import List,Set
from heapq import *
from itertools import product
from copy import deepcopy



class Abstraction() :


#-----------------------Initialization--------------------------------------------------------

  def __init__(self, filename : str, template : str, variable : str, enable_trace : bool):
    self._model: GlobalModel  = GlobalModelParser().parse(filename)
    self._template : str = template
    self._local_model: LocalModel = self._find_local_model(f"{template}1")
    self._abstracted_variable = variable
    self._initial_domain : Set[int] = {0}
    self._compute_initial_domain()
    self._adj : List[List[bool]] = []
    self._priorities : List[int] = []
    self._predecessors : List[Set[int]] = [set() for _ in range(len(self._local_model._transitions))]
    self._queue : heapq = []
    self._abstracted_model : LocalModel = None
    self._domains : List[Set[int]] = [set() for _ in range(len(self._local_model._transitions))]
    self._enable_trace = enable_trace
    self._trace = f"{str(self)}\n\n"
    self._compute_adj()
    self._compute_priorities()
    

  def _compute_initial_domain(self):
    if self._abstracted_variable in self._model._bounded_vars:
      self._inital_domain = self._parse_domain(self._abstracted_variable)



  def _compute_adj(self):
    """compute and assign self._adj, the adjacence matrix of self._local_model"""
    self._adj = [[False for _ in range(len(self._local_model._transitions))] for _ in range(len(self._local_model._transitions))]
    for lst in self._local_model._transitions:
      for transition in lst:
          self._adj[self._local_model._states[transition._state_from]][self._local_model._states[transition._state_to]] = True


  def _compute_adj_closure(self):
    """Returns the transitive closure of self._adj"""
    adj_closure = deepcopy(self._adj)
    for k in range(len(self._local_model._transitions)):
      for i in range(len(self._local_model._transitions)):
        for j in range(len(self._local_model._transitions)):
          adj_closure[i][j] = adj_closure[i][j] or (adj_closure[i][k] and adj_closure[k][j])
    return adj_closure


  def _compute_priorities(self):
    """compute and assign self._priorities, an array containing the opposites of the number of local states reachable from the states.
        [Because heapq is the implementation of a min heap]"""
    adj_closure = self._compute_adj_closure()
    self._priorities = [0 for i in range(len(self._local_model._transitions))]
    for i in range(len(self._local_model._transitions)):
      for j in range(len(self._local_model._transitions)):
        if i!=j and adj_closure[i][j]:
          self._priorities[i] -=1

  def _find_local_model(self, agent_name : str):
    """find a local model in self._model named agent_name and assign self._local_model"""
    for local_model in self._model._local_models:
      if local_model._agent_name == agent_name:
        return local_model
    raise Exception(f"Can't find agent named {agent_name} ")





#-----------------Auxiliaries------------------------------------------------------------


  def _get_state(self,state_id):
    for items in self._local_model._states.items():
      if items[1]==state_id:
        return items[0]


  def filter_sat(self,domain, transition): #For now, we ignore guards which does not contain x and cannot be met such as 1>2
    res = domain
    for cond in transition._conditions:
      if mem_cond(self._abstracted_variable,cond[1]): #Case (_ op x) are turned into (x op _)
        if cond[2] == ">=":
          cond = (cond[1],cond[0],"<=")
        elif cond[2] == "<=":
          cond = (cond[1],cond[0],">=")
        elif cond[2] == ">":
          cond = (cond[1],cond[0],"<")
        elif cond[2] == "<":
          cond = (cond[1],cond[0],">")
        else :
          cond = (cond[1],cond[0],cond[2])
      if mem_cond(self._abstracted_variable,cond[0]):   #Case (x op _)
          try:                                          #Subcase x=int
            val = int(cond[1])
            if cond[2] == "==":
              res = res.intersection({val})
            elif cond[2] == "!=":
              res = res.difference({val})
            elif cond[2] == "<=":
              res ={x for x in res if x <= val}
            elif cond[2] == ">=":
              res ={x for x in res if x >= val}
            elif cond[2] == "<":
              res ={x for x in res if x < val}
            elif cond[2] == ">":
              res ={x for x in res if x > val}
          except ValueError:                            #Subcase x=var
            if cond[1] in self._model._bounded_vars:
              res = res.intersection(self._parse_domain(cond[1]))
    return res

  def _parse_domain(self,variable):
    """return the domain of a bounded variable """
    if variable not in self._model._bounded_vars:
      raise Exception(f"Error in _compute_boundaries : variable {variable} is not bounded")
    values = self._model._bounded_vars[variable]
    lbound = int(values.split('.')[0][1:])
    ubound = int(values.split('.')[2][:-1])
    return set(range(lbound,ubound+1))


  def _evaluate(self,expr): #For now, expression is either an integer or '?var'
    """return a set of all possible evaluation of an expression.
       Precondition : Every variable of the expression (the abstracted one excepted) shall be bounded"""
    if isinstance(expr,str):
      if expr[0]!='?':
        raise Exception("Evaluation exception : Only integers or '?var' are supported")
      expr = expr[1:]
      if expr not in self._model._bounded_vars:
        raise Exception(f"Evaluation exception : variable {expr} is not bounded")
      return self._parse_domain(expr)
    return {expr}

  def _select_transitions(self,state_from : int,state_to : int):
    """Returns the list of transitions from state state_from to state state_to"""
    res = []
    for transition in self._local_model._transitions[state_from]:
      if self._local_model._states[transition._state_to]==state_to :
        res.append(transition)
    return res

  
  def _proc_loop(self,state : int):
    """process every edge looping on state until the stabilization of the domain of the abstracted variable"""
    new_domain = set()
    for looping_transition in self._select_transitions(state,state) :
      if self._enable_trace:
        self._trace += f"Processing looping transition {looping_transition._action.split(' ')[0]}\n"
      new_domain.update(self._proc_post_cond(looping_transition))
    if not(new_domain <= self._domains[state]):
      self._domains[state].update(new_domain)
      self._proc_loop(state)



  def _proc_post_cond(self,transition):
    """update the domain of target state with regard to the update of the transition and the domain of source state"""
    new_domain = deepcopy(self._domains[self._local_model._states[transition._state_from]])
    new_domain = self.filter_sat(new_domain,transition)
    for prop in transition.props :
      if mem_prop_left(self._abstracted_variable,prop) : 
        #print(f"Transition to {transition._state_to}: {prop}={transition.props[prop]}")
        if mem_prop_right(self._abstracted_variable,transition.props[prop]) : 
          buf = set()
          for value in new_domain:
            buf.update(self._evaluate(substitution(transition.props[prop],self._abstracted_variable, value)))
          new_domain = buf                                                           
        else :
          #print(transition.props[prop])
          new_domain = self._evaluate(transition.props[prop])
    return new_domain


  def _proc_inc_edges(self,state :int) :
    """process every incoming edges of the state and push successors in the queue if stabilization of the domain of the abstracted variable has not been reached"""
    for predecessor in self._predecessors[state]:
      for not_looping_transition in self._select_transitions(predecessor,state) :
        if self._enable_trace:
          self._trace += f"Processing transition {not_looping_transition._action.split(' ')[0]} from {not_looping_transition._state_from}\n"
        new_domain = self._proc_post_cond(not_looping_transition)
        if not(new_domain <= self._domains[state]):
          self._domains[state].update(new_domain)
          #print(f"domain of state {state} was updated")
          self._enqueue_successors(state)
    self._predecessors[state]=set()


  def _enqueue_successors(self,state :int):
    """push every successors of state in the queue if they were not already and append state as one of their relevant predecessors"""
    for l in range(len(self._adj[state])):
      if l!=state and self._adj[state][l]:
        self._enqueue(l)
        self._predecessors[l].add(state)

  def _enqueue(self,state : int):
    """push state in the queue if it was not already"""
    if not (self._priorities[state],state) in self._queue:
        heappush(self._queue, (self._priorities[state],state))


  def _compute_domains(self) :
    """Compute and assign self._domains"""
    self._domains[0] = self._initial_domain
    if self._enable_trace:
      self._trace +="----------------  Initial Processing  -------------------\n"
    self._proc_loop(0)
    self._enqueue_successors(0)
    if self._enable_trace:
      self._trace +="\n"
      self._save_queue()
      self._save_pred()
      self._save_domains()
    while len(self._queue) > 0:
      (_,l) = heappop(self._queue)
      if self._enable_trace:
        self._trace += f"----------------  {self._get_state(l)}  -------------------\n"
      self._proc_inc_edges(l)
      self._proc_loop(l)
      if self._enable_trace:
        self._trace +="\n"
        self._save_queue()
        self._save_pred()
        self._save_domains()





  def _reachable_states(self) :
    """returns a dictionnary of relevant states of the abstracted model"""
    return dict([(key,value) for (key,value) in self._local_model._states.items() if len(self._domains[value])>0 ]) #those with non-empty x-domain are reachable

  def _filter_cond(self,cond):
    """return true iif the abstracted variable does not appear in cond"""
    return not (mem_cond(self._abstracted_variable,cond[0]) or mem_cond(self._abstracted_variable,cond[1]))

  def _fix_transition(self,transition):
    """return a list of the transitions of the abstracted model generated by a transition of the concrete model"""
    action = transition._action.split(' ')[0]
    res = []
    conditions = list(filter(self._filter_cond,transition._conditions))
    lprops = []
    rprop_lists = []
    new_domain = self._domains[self._local_model._states[transition._state_from]]
    for prop in transition._props:
      if mem_prop_left(self._abstracted_variable,prop) : 
        if mem_prop_right(self._abstracted_variable,transition.props[prop]) : 
          buf = set()
          for value in new_domain:
            buf.update(self._evaluate(substitution(transition._props[prop],self._abstracted_variable, value)))
            new_domain = buf                                                            
        else :
          new_domain =  self._evaluate(transition.props[prop])
      elif mem_prop_right(self._abstracted_variable,transition.props[prop]):
        rprops = set()
        for value in new_domain:
          rprops.add(substitution(transition._props[prop],self._abstracted_variable, value))
        lprops.append(prop)
        rprop_lists.append(list(rprops))
      else :
        lprops.append(prop)
        rprop_lists.append([transition._props[prop]])
    rprops_product = list(product(*rprop_lists))
    all_props = []
    for items in rprops_product:
      all_props.append([(lprop,rprop) for lprop,rprop in zip(lprops,items)])
    i=0
    for props in all_props:
      res.append(LocalTransition(transition._state_from,transition._state_to,f"{action}_{i}",transition._shared,conditions,dict(props)))
      i+=1
    return res


  def _compute_transitions(self,states):
    """return a list of all transition of the abstracted model"""
    res = []
    for state in states:  
      transitions = []
      for transition in self._local_model._transitions[state]:
        if self._local_model._states[transition._state_to] in states:
          transitions.extend(self._fix_transition(transition))
      res.append(transitions)
    return res


                 
  def generate(self):
    """compute and assign local model self._abstracted_model with regard to the abstracted variable"""
    self._compute_domains()
    agent_id = self._local_model._agent_id
    actions = self._local_model._actions
    protocol = self._local_model._protocol
    agent_name = self._local_model._agent_name + f"_{self._abstracted_variable}_abstracted" 
    states = self._reachable_states()
    transitions = self._compute_transitions(states.values()) 
    self._abstracted_model = LocalModel(agent_id,agent_name,states,transitions,protocol,actions)
    if self._enable_trace:
      self.save_trace()






  #---------------------------------Printing--------------------------------------------------------------

  def __str__(self):
    return f"Abstraction on agent {self._local_model._agent_name} and variable {self._abstracted_variable}"



  def _save_pred(self):
    """save the current state of the relevant predecessors in the trace"""
    self._trace += "Relevant Predecessors :\n"
    for state in self._local_model._states.keys():
      #print(f"pi({state}) : {self._predecessors[self._local_model._states[state]]}")
      self._trace += f"{state} : {self._predecessors[self._local_model._states[state]]}\n"
    self._trace += "\n"

  def _save_queue(self):
    """save the current state of the queue in the trace"""
    self._trace +=f"queue : {self._queue}\n\n"

  def _save_domains(self):
    """save the current state of the domains of x in the trace"""
    self._trace += "Domains :\n"
    for state in self._local_model._states.keys():
      self._trace += f"{state} : {self._domains[self._local_model._states[state]]}\n"
    self._trace += "\n"
    

#-------------------------------Output----------------------------------------------------------------

  def _count_instances(self):
    """count instances of template on which abstraction is computed"""
    i=1
    while f"{self._template}{i}" in [model._agent_name for model in self._model._local_models]:
      i=i+1
    return i-1

  def _parse_model(self):
    """return a dict associating templates with the number of its instances """
    res = dict()
    for agent in self._model._local_models:
      (template,count) = _parse_agent_name(agent._agent_name)
      if template!= self._template and (template not in res or res[template] < count):
        res[template] = count
    res[self._template]=self._count_instances()
    return res

  def _to_aid(self,string,substring):
    """replace substring in string by "aID" """
    return string.replace(substring,"aID")


  def _write_conds(self,conds):
    """return a string encoding the condition in the input file"""
    res = ""
    for cond in conds:
      res += cond[0] + cond[2] + cond[1] + ","
    return res[:-1]


  def _write_props(self,props):
    """return a string encoding the prop in the input file"""
    res = ""
    for prop in props:
      res += f"{prop}={props[prop]},"
    return res[:-1]

  def _write_protocol(self,protocol):
    """return a string encoding the protocol in the input file"""
    res = ""
    for lst in protocol:
      res += "["
      for var in lst:
        if var != self._abstracted_variable:
          res += f"{var},"
      res = res[:-1]
      res +="],"
    return res[:-1]


  def _write_transition(self,tr):
    """return a string encoding the transition in the input file"""
    res = ""
    if tr._shared:
      res += f"shared "
    res += f"{tr._action}: {tr._state_from} -"
    if len(tr._conditions)>0:
      res+= f"[{self._write_conds(tr._conditions)}]"
    res+=f"> {tr._state_to}" 
    if len(tr._props)>0:
       res+= f"[{self._write_props(tr._props)}]"
    res += "\n"
    return res

  def _write_bounded_vars(self):
    """return a string encoding the bounded vars in the input file"""
    res = ""
    for (var,boundaries) in self._model._bounded_vars.items():
      if var != self._abstracted_variable:
        res += f"{var} {boundaries},"
    return res[:-1]

  def _write_coalition(self):
    """return a string encoding the coalition in the input file"""
    res = ""
    for agent in self._model._coalition:
      res += f"{agent},"
    return res[:-1]

  def _write_persistent(self):
    """return a string encoding the persistent variables in the input file"""
    res = ""
    for var in self._model._persistent:
      if var != self._abstracted_variable:
        res += f"{var},"
    return res[:-1]

  def _write_formula(self):
    """return a string encoding the formula in the input file"""
    res = ""


  def _write_template(self,local_model,template,count):
    """return a string encoding the template in the input file"""
    res = f"Agent {template}[{count}]:\n"
    res += f"init: {self._get_state(0)}\n"
    for lst in local_model._transitions:
      for tr in lst:
        res += self._write_transition(tr)
    if len(local_model._protocol)>0:
      res+= f"PROTOCOL: [{self._write_protocol(local_model._protocol)}]\n"
    return self._to_aid(res,f"{template}1")

  def _write_output(self,local_model,template):
    """return a string encoding the model in the input file"""
    res=""
    for (template,count) in self._parse_model().items():
      local_model = self._find_local_model(f"{template}1")
      if template == self._template:
        local_model = self._abstracted_model
      res += self._write_template(local_model,template,count)
      res += "\n\n"
    if len(self._model._bounded_vars)>0:
      res+= f"BOUNDED_VARS: [{self._write_bounded_vars()}]\n"
    if len(self._model._persistent)>0:
      res+= f"PERSISTENT: [{self._write_persistent()}]\n"
    if len(self._model._coalition)>0:
      res+= f"COALITION: [{self._write_coalition()}]\n"
    return res


  def save_to_file(self, filename=f"default"):
    """save the abstracted model in a text file"""
    if filename=="default":
      filename = f"tests_abstraction/abstracted_{self._local_model._agent_name}.txt"
    model_file = open(filename, "w")
    lines = self._write_output(self._abstracted_model,self._local_model._agent_name)
    model_file.write(lines)
    model_file.close()

  def save_former_model(self,filename=f"default"):
    """save the abstracted local model in a text file [for debug purpose]"""
    if filename=="default":
      filename = f"tests_abstraction/former_{self._local_model._agent_name}.txt"
    model_file = open(filename, "w")
    lines = self._write_template(self._local_model,self._local_model._agent_name,1)
    model_file.write(lines)
    model_file.close()




  def save_trace(self,filename=f"default"):
    """save the trace in a textfile"""
    if filename=="default":
      filename = f"tests_abstraction/trace_{self._local_model._agent_name}.txt"
    trace_file = open(filename, "w")
    trace_file.write(self._trace)
    trace_file.close()
    



#-----------------Auxiliaries [not methods]------------------------------------------------------------


def _parse_agent_name(agent_name):
  """return the template of agent named agent_name and the number of its instance"""
  for i in range(len(agent_name)):
    if agent_name[i] in ['0','1','2','3','4','5','6','7','8','9']:
      try:
        return agent_name[:i],int(agent_name[i:])
      except ValueError:
        raise Exception("Error while parsing agent name {agent_name}: Only [a-z]* templates are supported")
  raise Exception("Error while parsing agent_name {agent_name} : Only template_aID names are supported")



def mem_prop_left(variable : str, expr): #For now, updates are couple (variable,value)
  """membership test for the left part of an update"""
  return variable==expr

def mem_prop_right(variable : str, expr):
  """membership test for the right part of an update"""
  if isinstance(expr,str):
    return variable in expr
  return False


def mem_cond(variable : str, expr):
  """membership test for any part of a condition""" 
  if isinstance(expr,str):
    return variable in expr
  return False



def substitution(expr,variable :str, value):
  """return expr[variable:=value]"""
  if isinstance(expr,str):
    if expr== '?' + variable:
      return value
  return expr



#-----------------------Unused ---------------------------------------------------------------------------


def extract_conditions(local_model):
  """extract conditions as a triplet (variable,value,operator)"""
  conds  = []
  for lst in local_model.transitions:
    for transition in lst:
      conds.extend(transition.conditions)
  return conds 


def extract_props(local_model):
  """extract props as a couple (variable,value)"""
  updates  = []
  for lst in local_model.transitions:
    for transition in lst:
      updates.extend(list(transtion.props.items()))
  return updates

def extract_variables_from_condition(condition):
  return condition[0]

def extract_variables_from_prop(prop):
  return prop[0]

def compute_transitive_closure():
  print("TODO")
        




if __name__ == "__main__":
  from stv.models.asynchronous.parser import GlobalModelParser
  from stv.parsers import FormulaParser
  voter = 1
  cand = 2
  enable_trace = True
  filename_in =  f"tests_abstraction/example.txt"
  #filename_in =  f"tests_abstraction/Selene_{voter}_{cand}.txt"
  filename_out = f"{filename_in.rstrip('.txt')}_abstracted.txt"
  #agent_name = "Voter"
  agent_name = "Template"
  #variable = "Voter1_vote"
  variable = "x"
  abstraction = Abstraction(filename_in,agent_name,variable,enable_trace=enable_trace)
  abstraction.generate()
  abstraction.save_to_file(filename_out)



