from stv.models.asynchronous import GlobalModel,LocalModel, LocalTransition
from stv.models.asynchronous.parser import GlobalModelParser  
from typing import List,Set
from heapq import *
from itertools import product
from copy import deepcopy




# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                 # 
#           Implementation of variable abstraction                #
#                                                                 #
#   Every mention of "state" shall be understood as "locations"   #
#                                                                 #
#    Comment line 191 and 233 to only process agents using        #
#                    abstracted variable                          #
#                                                                 #
#                                                                 # 
#                                                                 #
#   Labelling of abstracted shared transitions is not handled     #
#             (Should be done around line 600)                    #
#                                                                 #
#                                                                 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Found(Exception): pass #Used to double break in self._compute_local_models

class Abstraction() :

  def __init__(self, filename : str, variable : str, enable_trace=False):
    self._filename = filename
    print(f"parsing file {filename}...") 
    self._model: GlobalModel  = GlobalModelParser().parse(filename) 
    print(f"parsing completed !") 
    print()
    self._model._compute_shared_transitions()
    self._abstracted_variable = variable
    self._templates : dict[str,int] = dict()     #templates and number of their instances
    self._abstracted_templates : dict[str,int] = dict() #abstracted templates and number of their instances
    self._count_templates()
    self._agents : dict[LocalModel,int] = dict()  #relevant agents and their position in the product agent
    self._select_agents()  
    self._product_agent: LocalModel = None   #product of such agents
    self._create_product_agent()
    self._initial_domain : Set[int] = {0}
    self._set_initial_domain()
    self._adj : List[List[bool]] = []        #adjacence matrix of product agent
    self._compute_adj()
    self._priorities : List[int] = []
    self._compute_priorities()
    self._predecessors : List[Set[int]] = [set() for _ in range(len(self.product_agent.transitions))]
    self._queue : heapq = []
    self._abstracted_agents : List[LocalModel] = []
    self._domains : List[Set[int]] =   [set() for _ in range(len(self.product_agent.transitions))]
    self._agents_domains : dict[LocalModel,List[Set[int]]] =   dict()
    self._enable_trace = enable_trace
    self._trace = f"{str(self)}\n\n"
    self._other_domains : dict = dict()


#--------------------------------- Getters ------------------------------------


  @property
  def model(self):
      """Global concrete model"""
      return self._model

  @property
  def abstracted_variable(self):
      """Abstracted variable"""
      return self._abstracted_variable

  @property
  def templates(self):
      """Templates"""
      return self._templates

  @property
  def abstracted_templates(self):
      """Abstracted templates"""
      return self._abstracted_templates

  @property
  def agents(self):
      """Relevant agents"""
      return self._agents

  @property
  def product_agent(self):
      """Product of relevant concrete agent"""
      return self._product_agent

  @property
  def abstracted_agents(self):
      """abstracted agents"""
      return self._abstracted_agents


  def _get_agent_from_name(self, agent_name : str):
    """returns an agent in self.model.local_models named agent_name"""
    for agent in self.model.local_models:
      if agent.agent_name == agent_name:
        return agent
    raise Exception(f"Can't find agent named {agent_name} ")



  def _get_abstracted_agent_from_name(self, agent_name : str):
    """returns an agent in self.abstracted_models named agent_name"""
    for agent in self.abstracted_agents:
      if agent.agent_name == agent_name:
        return agent
    raise Exception(f"Can't find agent named {agent_name} ")


  def _get_agent_from_id(self,val :int) :
    """return an agent of self.agents with given id"""
    for item in self.agents.items():
      if item[1]==val:
        return item[0]  
    raise Exception(f"Exception in _get_agent_from_id() : could not find any agent with id {val}")


  def _get_states_from_product_state(self,label:str):
    """returns the list of states labels that compose label"""
    return label.split(" x ")




  def _get_cartesian_product_label(self,state: tuple):
    """returns the cartesian product of labels of states in a given product agent's state"""
    return " x ".join([agent.get_state_label(i) for agent,i in zip(self.agents,state)])





#----------------------------- Initialisation ---------------------------------



  def _count_templates(self):
    """binds templates with the count of their instances in self._templates"""
    for agent in self.model.local_models:
      (template,count) = parse_agent_name(agent.agent_name)
      if template not in self.templates or self.templates[template] < count:
        self._templates[template] = count



  def _compute_closure_share_relation_rec(self,agents,acc):
    """returns concatenation of acc with reflexive transitive closure of
          agents for relation 'sharing a transition'"""
    for agent in agents:
      if agent in acc:
        continue
      acc.add(agent)
      for transition in agent.get_transitions():
        if not transition.shared:
          continue
        new_agents=[self.model.local_models[tr.agent_id] for tr in transition.transition_list]
        agents_closure = self._compute_closure_share_relation_rec(new_agents,acc)
        acc.update(agents_closure)
    return acc


  def _compute_closure_share_relation(self,agents):
    """returns list of reflexive transitive closure of agents for relation 'sharing a transition'"""
    return list(self._compute_closure_share_relation_rec(agents,set()))

  def _select_agents(self):
    """assigns to self.agents the list of agents which uses the variable var [or share a transition with such agent]"""
    agents = [] 
    for agent in self.model.local_models:
      try :
        for update in agent.updates:
          if mem_update_left(self.abstracted_variable,update) or mem_update_right(self.abstracted_variable,update):
            raise Found
        for cond in agent.conditions:
          if mem_cond(self.abstracted_variable,cond):
            raise Found
      except Found:
        agents.append(agent)
    #agents = list(self._compute_closure_share_relation(agents)) #Comment this line to only process agents that use abstracted variable
    for (ident,agent) in enumerate(agents):
      self.agents[agent] = ident


  def _merge_shared_transition(self,transition: LocalTransition,state: tuple):
    """merge shared transitions. Returns product transition and target state"""
    state_to = list(state)
    for tr in transition.transition_list :
      agent = self.model.local_models[tr.agent_id]
      if agent in self.agents :
        index = self.agents[agent]
        state_to[index]=agent.get_state_id(tr.state_to)
        if tr._state_from != agent.get_state_label(state[index]):
          return None,None
        if  transition.agent_id != tr.agent_id:
          transition.conditions.extend(tr.conditions)
          transition.props.update(tr.props)
    state_to = tuple(state_to)
    transition._state_to=self._get_cartesian_product_label(state_to)
    return transition,state_to

  def _generate_outcoming_transitions(self,state:tuple):
    """generates transitions coming from a state in the product agent. Returns transitions,target states and actions labels"""
    shared_transitions = []
    transitions=[]
    states= set()
    actions = set()
    state_label=self._get_cartesian_product_label(state)
    for ident,local_state in enumerate(state):
      agent = self._get_agent_from_id(ident)
      for transition in agent.transitions[local_state]:
        tr = deepcopy(transition)
        tr._action = removesuffix(transition._action,f"_{agent.agent_name}")
        tr._state_from=state_label 
        if tr.shared:
          if tr in shared_transitions:
            continue
          tr ,state_to= self._merge_shared_transition(tr,state)
          if tr is None:
            continue
          shared_transitions.append(tr)
          #tr._shared = False  #Comment this line if self.agents is not stable by the relation "sharing a transition" in general
        else :
          state_to = list(state)
          state_to[ident]=agent.states[transition.state_to]
          state_to= tuple(state_to)
          tr._state_to=self._get_cartesian_product_label(state_to)
        states.add(state_to)
        actions.add(tr._action)
        transitions.append(tr)
    return transitions,states,actions


  def _create_product_agent(self):
    """ compute the product of concrete agents that uses the abstracted variable"""
    if len(self.agents)==0:
      raise Exception(f"ERR:No agent in {self._filename} uses variable {self.abstracted_variable}!!")
    if len(self.agents)==1:
      self._product_agent = list(self.agents.keys())[0]
      return
    agent_id=None
    agent_name=" x ".join([convert_integers_to_letters(agent._agent_name) for agent in self.agents ]) + "1"
    states_dic = dict()
    actions = set()
    transitions = []
    protocol = [lst for agent in self.agents for lst in agent._protocol]
    def _create_product_agent_rec(states,ident,transitions):
      for state in states:
        state_label = self._get_cartesian_product_label(state)
        if state_label not in states_dic:
          states_dic[state_label]= ident
          (outcoming_transitions,successors,outcoming_actions) = self._generate_outcoming_transitions(state)
          transitions = extend_transitions(transitions,ident)
          transitions[ident]=outcoming_transitions
          ident=_create_product_agent_rec(successors,ident+1,transitions)
          actions.update(outcoming_actions)
      return ident
    state = tuple([0 for _ in self.agents])
    _create_product_agent_rec({state},0,transitions)
    actions= list(actions)
    self._product_agent = LocalModel(agent_id,agent_name,states_dic,transitions,protocol,actions)

  def _set_initial_domain(self):
    """compute inial domain of abstracted variable [read the header BOUNDED VARIABLES or {0}]"""
    if self.abstracted_variable in self.model._bounded_vars:
      domain = self._get_domain_bounded(self.abstracted_variable)

  def _compute_adj(self):
    """compute and assign self._adj, the adjacence matrix of self.product_agent"""
    self._adj = [[False for _ in range(len(self.product_agent._transitions))] for _ in range(len(self.product_agent.transitions))]
    for lst in self.product_agent.transitions:
      for transition in lst:
        self._adj[self.product_agent.states[transition.state_from]][self.product_agent.states[transition.state_to]] = True


  def _compute_adj_closure(self):
    """Returns the transitive closure of self._adj"""
    adj_closure = deepcopy(self._adj)
    for k in range(len(self.product_agent.transitions)):
      for i in range(len(self.product_agent.transitions)):
        for j in range(len(self.product_agent.transitions)):
          adj_closure[i][j] = adj_closure[i][j] or (adj_closure[i][k] and adj_closure[k][j])
    return adj_closure


  def _compute_priorities(self):
    """compute and assign self._priorities, an array containing the opposites of the number of local states reachable from each state.
        [Because heapq is the implementation of a min heap]"""
    adj_closure = self._compute_adj_closure()
    self._priorities = [0 for i in range(len(self.product_agent.transitions))]
    for i in range(len(self.product_agent.transitions)):
      for j in range(len(self.product_agent.transitions)):
        if i!=j and adj_closure[i][j]:
          self._priorities[i] -=1


#----------------------------- Compute domains  -------------------------------


  def _get_assigned_values(self,variable):
    """return the set of numerical values assigned to a variable in any update"""
    domain = set()
    for (var,val) in self.product_agent.updates:
      if var==variable and (isinstance(val,int) or isinstance(val,bool)):
        domain.add(val)
    return domain

  
  def _get_domain_bounded(self,variable):
    """return the domain of a bounded variable in the product model"""
    if variable not in self.model._bounded_vars:
      raise Exception(f"Error in _compute_boundaries : variable {variable} is not bounded")
    values = self.model._bounded_vars[variable]
    lbound = int(values.split('.')[0][1:])
    ubound = int(values.split('.')[2][:-1])
    return set(range(lbound,ubound+1))

  def _get_domain_not_bounded(self,variable):
    """return domain of a not-bounded variable in the product model """
    domain = set()
    for var in self.product_agent.transitive_closure_update({variable}):
      domain.update(self._get_assigned_values(var))
    if len(domain)==0:
      return {0} #Default
    return domain

  def _get_domain(self,variable):
    """return the domain of a variable and update self._other_domains dynamically """
    if variable in self._other_domains:
      return self._other_domains[variable]
    if variable in self.model._bounded_vars:
      domain = self._get_domain_bounded(variable)
    else :
      domain = self._get_domain_not_bounded(variable)
    self._other_domains[variable] = domain
    return domain



#------------------- Compute domains of abstracted variable -------------------



  def _evaluate(self,expr): #For now, expression is either an integer or '?var'
    """return a set of all possible values of an expression.
       pre-condition : abstracted variable does not appear in expr"""
    if isinstance(expr,str):
      if expr[0]!='?':
        raise Exception("Evaluation exception : Only integers or '?var' are supported")
      expr = expr[1:]
      return self._get_domain(expr)
    elif isinstance(expr,int):
      return {expr}
    else :
      raise Exception("Evaluation exception : Only integers or '?var' are supported")


  def filter_sat(self,domain, conditions): #For now, we ignore pre-conditions which does not contain x such as 1>2
    """return the subset of the domain which satisfies the pre-conditions of transition"""
    res = domain
    for cond in conditions:
      if mem_expr(self._abstracted_variable,cond[1]): #Case (_ op x) are turned into (x op _)
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
      if mem_expr(self._abstracted_variable,cond[0]):   #Case (x op _)
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
            if cond[1] in self.model._bounded_vars:
              res = res.intersection(self._get_domain(cond[1]))
    return res


  def _select_transitions(self,state_from : int,state_to : int):
    """Returns the list of transitions from state state_from to state state_to"""
    res = []
    for transition in self.product_agent._transitions[state_from]:
      if self.product_agent._states[transition._state_to]==state_to :
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
    new_domain = self._domains[self.product_agent._states[transition._state_from]].copy()
    new_domain = self.filter_sat(new_domain,transition.conditions)
    for update in transition.props.items() :
      if len(new_domain)==0:
        return set()
      if mem_update_left(self._abstracted_variable,update) : 
        if mem_update_right(self._abstracted_variable,update) : 
          buf = set()
          for value in new_domain:
            buf.update(self._evaluate(substitution(self.abstracted_variable,update, value)))
          new_domain = buf                                                           
        else :
          new_domain = self._evaluate(update[1])
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
    self._trace +="----------------  Initial Processing  -------------------\n"
    self._proc_loop(0)
    self._enqueue_successors(0)
    self._trace +="\n"
    self._write_queue()
    self._write_pred()
    self._write_domains()
    while len(self._queue) > 0:
      (_,l) = heappop(self._queue)
      self._trace += f"----------------  {self.product_agent.get_state_label(l)}  -------------------\n"
      self._proc_inc_edges(l)
      self._proc_loop(l)
      self._trace +="\n"
      self._write_queue()
      self._write_pred()
      self._write_domains()


#-------------------------- Create abstracted agent ---------------------------


  def _reachable_states(self) :
    """returns a dictionnary of locations of the abstracted model in which domain of abstracted variable is non-empty"""
    counter = 0
    res= dict()
    for (key,value) in self.product_agent._states.items():
      if len(self._domains[value])>0: #Getting rid of states with empty domain
        res[key]=counter
        counter +=1
    return res
    #return dict([(key,value) for (key,value) in self.product_agent._states.items() if len(self._domains[value])>0 ]) doesn't modify state identifiers

  def _generate_conditions(self,domain,conditions):
    """generate conditions of the abstracted transition based on the conditions of the inital transition"""
    res = []
    for cond in conditions:
      if mem_cond(self.abstracted_variable,cond):
        if len(self.filter_sat(domain,[cond]))==0:
          res.append(("True","False","=="))
        else :
          res.append(("True","True","=="))
      else:
        res.append(cond)
    return res




  def _generate_transitions(self,agent,transition):
    """returns a list of the transitions of the abstracted agent generated by a transition of the concrete agent [UNUSED]"""
    res = []
    action = transition.action
    left_updates = []
    right_updates_lists = []
    domain = self._agents_domains[agent][self.get_state_id(transition.state_from)]
    conditions = self._generate_conditions(domain,transition.conditions)
    suffixes = []
    for update in transition.props.items():
      if mem_update_left(self.abstracted_variable,update) : 
        if mem_update_right(self.abstracted_variable,update) : 
          buf = set()
          for value in new_domain:
            buf.update(self._evaluate(substitution(self.abstracted_variable,update, value)))
            new_domain = buf                                                            
        else :
          new_domain =  self._evaluate(update[1])
      elif mem_update_right(self.abstracted_variable,update):
        suffixes.append(update[0])
        right_updates = set()
        for value in domain:
          right_updates.add(substitution(self.abstracted_variable,update,value))
        left_updates.append(update[0])
        right_updates_lists.append(list(right_updates))
      else :
        left_updates.append(update[0])
        right_updates_lists.append([update[1]])
    right_updates_product = list(product(*right_updates_lists))
    all_props = []
    for right_updates in right_updates_product:
      all_props.append([(left_update,right_update) for left_update,right_update in zip(left_updates,right_updates)])
    for props in all_props:
      props = dict(props)
      suffix = create_suffix(props,suffixes)
      tr = LocalTransition(transition._state_from,transition._state_to,action,transition._shared,conditions,props)
      res.append(tr)
    return res


  def _generate_transitions_norm(self,agent,transition):
    """same as self._generate_transition, but initial transition verifies two assumptions :
        I. Only the last update may modify the abstracted variable
       [This assumption enables to use source state domain to duplicate transition]
        II. Each variable can be updated at most once
       [This assumption is only made to ensure the relevancy of action suffixes]
       """
    res = []
    left_updates = []
    right_updates_lists = []
    domain = self._agents_domains[agent][agent.get_state_id(transition.state_from)]
    if transition.shared : #domains of shared transitions are union of domains of source states
      for tr in transition.transition_list:
        agent2 = self.model.local_models[tr.agent_id]
        if agent2 in self.agents: #Always true when processed agents are close under the relation "sharing a transitino"
          domain.update(self._agents_domains[agent2][agent2.get_state_id(tr.state_from)])
    conditions = self._generate_conditions(domain,transition.conditions)
    suffixes = []
    for update in transition.props.items():
      if mem_update_left(self.abstracted_variable,update):
        continue
      elif mem_update_right(self.abstracted_variable,update):
        suffixes.append(update[0])
        right_updates = set()
        for value in domain:
          right_updates.add(substitution(self.abstracted_variable,update,value))
        left_updates.append(update[0])
        right_updates_lists.append(list(right_updates))
      else :
        left_updates.append(update[0])
        right_updates_lists.append([update[1]])
    all_right_updates = list(product(*right_updates_lists))
    all_props = []
    for right_updates in all_right_updates:
      all_props.append([(left_update,right_update) for left_update,right_update in zip(left_updates,right_updates)])
    for props in all_props:
      props = dict(props)
      suffix = create_suffix(props,suffixes)
      if not transition.shared: #Compatibility : unshared transition has label [action]_[agent_name] in current STV implementation
        split = transition.action.split('_') 
        action = f"{'_'.join(split[:-1])}{suffix}_{split[-1]}" 
      else:
        action = f"{transition.action}{suffix}"
      tr = LocalTransition(transition.state_from,transition.state_to,action,transition.shared,conditions,props)
      res.append(tr)
    return res

  def _check_membership(self,transition,transitions):
    """return true iif transition is not shared and as same target state,props and conds that an element of transitions"""
    if transition.shared:
      return False
    for transition2 in transitions:
      if transition._state_to !=  transition2._state_to:
        continue
      if transition._props != transition2._props:
        continue
      if set(transition._conditions) != set(transition2._conditions):
        continue
      return True
    return False



  def _compute_agents_domains(self):
    """compute domains of every state of every agent of self.agents"""
    for agent in self.agents:
      self._agents_domains[agent] = [set() for _ in range(len(agent.states))]
    for state in self.product_agent.states:
      for ident,local_state in enumerate(self._get_states_from_product_state(state)):
          agent = self._get_agent_from_id(ident)
          self._agents_domains[agent][agent.get_state_id(local_state)].update(self._domains[self.product_agent.get_state_id(state)])


  def _compute_transitions(self,agent,states):
    """return a list of all transition of the abstracted agent"""
    res = []
    for state in states:  
      transitions = []
      for old_transition in agent._transitions[agent._states[state]]:
        if old_transition._state_to in states:
          for new_transition in self._generate_transitions_norm(agent,old_transition):
            if not self._check_membership(new_transition,transitions):
              transitions.append(new_transition)
      res.append(transitions)
    return res



  def _adjust_template(self,template: str):
    """replace templates of abstracted agent with new templates"""
    self._templates[template] -= 1
    if self.templates[template] == 0:
      self.templates.pop(template)
    new_template = f"{template}_abstracted"
    if new_template in self.abstracted_templates:
      self._abstracted_templates[new_template] += 1
    else :
      self._abstracted_templates[new_template] = 1

                 
  def _compute_abstract_agent(self,agent):
    """compute and assign local agent self.abstracted_agent with regard to the abstracted variable"""
    agent_id = agent._agent_id
    actions = agent.actions
    protocol = agent._protocol
    (template,ident_) = parse_agent_name(agent.agent_name)
    self._adjust_template(template)
    new_template = f"{template}_abstracted"
    agent_name = f"{new_template}{self.abstracted_templates[new_template]}"
    states= agent.states  
    #states = self._reachable_states() #Uncomment to get rid of states with empty domain for x
    transitions = self._compute_transitions(agent,states.keys()) 
    self._abstracted_agents.append(LocalModel(agent_id,agent_name,states,transitions,protocol,actions))


  def compute(self):
    """compute the abstraction and assing self.abstracted_agents"""
    self._compute_domains()
    print(f"Warning : shared transitions are duplicated independently from linked transitions")
    print(f"Warning : redundant transitions [same props, updates and states] are not added")
    self._compute_agents_domains()
    for agent in self.agents:
      self._compute_abstract_agent(agent)




  #---------------------------------Trace----------------------------------------


  def __str__(self):
    agents = list(self.agents.keys())
    if len(agents)==0:
      return f"Abstraction of variable {self._abstracted_variable} on no agent"
    elif len(agents)==1:
      return f"Abstraction of variable {self._abstracted_variable} on agent {agents[0].agent_name}"  
    return f"Abstraction of variable {self._abstracted_variable} on agents \
{', '.join([agent._agent_name for agent in agents[:-1]])} and {agents[-1].agent_name}"


  def _get_state(self,state_id):
    """return name of state with id state_id in product model [Used for the trace]"""
    for item in self.product_agent._states.items():
      if item[1]==state_id:
        return item[0]


  def _write_pred(self):
    """save the current state of the relevant predecessors in the trace"""
    self._trace += "Relevant Predecessors :\n"
    for state in self.product_agent._states.keys():
      self._trace += f"{state} : {self._predecessors[self.product_agent._states[state]]}\n"
    self._trace += "\n"

  def _write_queue(self):
    """save the current state of the queue in the trace"""
    self._trace +=f"queue : {self._queue}\n\n"

  def _write_domains(self):
    """save the current state of the domains of x in the trace"""
    self._trace += "Domains :\n"
    for state in self.product_agent._states.keys():
      self._trace += f"{state} : {self._domains[self.product_agent._states[state]]}\n"
    self._trace += "\n"
    


#--------------------------------- Output -------------------------------------


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
      action = tr.action
    else :
      action = '_'.join(tr.action.split('_')[:-1])
    #res += f"{tr._action}: {tr._state_from} -"
    res += f"{action}: {tr._state_from} -"
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
    for (var,boundaries) in self.model._bounded_vars.items():
      if var != self._abstracted_variable:
        res += f"{var} {boundaries},"
    return res[:-1]

  def _write_coalition(self):
    """return a string encoding the coalition in the input file"""
    res = ""
    for agent in self.model._coalition:
      res += f"{agent},"
    return res[:-1]

  def _write_persistent(self):
    """return a string encoding the persistent variables in the input file"""
    res = ""
    for var in self.model._persistent:
      if var != self._abstracted_variable:
        res += f"{var},"
    return res[:-1]


  def _write_logic(self):
    """return a string encoding the persistent variables in the input file"""
    return self.model._logicType.name

  def _write_formula(self):
    """return a string encoding the formula in the input file"""
    return str(self.model._formula)


  def _write_template(self,agent,template,count):
    """return a string encoding the template in the input file"""
    res = f"Agent {template}[{count}]:\n"
    res += f"init: {agent.get_state_label(0)}\n"
    for lst in agent._transitions:
      for tr in lst:
        res += self._write_transition(tr)
    if len(agent._protocol)>0:
      res+= f"PROTOCOL: [{self._write_protocol(agent._protocol)}]\n"
    return self._to_aid(res,f"{removesuffix(template,'_abstracted')}1")

  def _write_output(self):
    """return a string encoding the model in the input file"""
    res=""
    for (template,count) in self.templates.items():
      agent = self._get_agent_from_name(f"{template}1")
      res += self._write_template(agent,template,count)
      res += "\n\n"
    for (template,count) in self.abstracted_templates.items():
      agent = self._get_abstracted_agent_from_name(f"{template}1")
      res += self._write_template(agent,template,count)
      res += "\n\n"
    if not set(self.model._bounded_vars.keys()) <= {self._abstracted_variable}:
      res+= f"BOUNDED_VARS: [{self._write_bounded_vars()}]\n"
    if not set(self.model._persistent) <= {self._abstracted_variable}:
      res+= f"PERSISTENT: [{self._write_persistent()}]\n"
    if self.model.isAtl():
      res+= f"COALITION: [{self._write_coalition()}]\n"
    if self.model._logicType!=None:
      res+= f"LOGIC: {self._write_logic()}\n"
    if len(self.model._formula)>0:
      res+= f"FORMULA: {self._write_formula()}\n"
    return res


  def _save_to_file(self, filename=""):
    """save the abstracted local model in a text file"""
    if len(filename)==0:
      filename = f"{self._filename.rstrip('.txt')}_abstracted.txt"
    model_file = open(filename, "w")
    lines = self._write_output()
    model_file.write(lines)
    model_file.close()

  def _save_product_model(self,filename=""):
    """save the product model in a text file [for debug purpose]"""
    if len(filename)==0:
      filename = f"{self._filename.rstrip('.txt')}_product_model.txt"
    model_file = open(filename, "w")
    template = parse_agent_name(self.product_agent._agent_name)[0]
    lines = self._write_template(self.product_agent,template,1)
    model_file.write(lines)
    model_file.close()




  def _save_trace(self,filename=""):
    """save the trace in a textfile"""
    if len(filename)==0:
      filename = f"{self._filename.rstrip('.txt')}_trace.txt"
    trace_file = open(filename, "w")
    trace_file.write(self._trace)
    trace_file.close()


  def save(self,filename=""):
    self._save_to_file(filename)
    print(f"abstracted model saved in {self._filename.rstrip('.txt')}_abstracted.txt")
    if self._enable_trace:
      self._save_trace()
      print(f"trace saved in {self._filename.rstrip('.txt')}_trace.txt")
      self._save_product_model()
      print(f"product model saved in {self._filename.rstrip('.txt')}_product_model.txt ")


#------------------------- Variable Domains to Store --------------------------




  def compute_variables(self):
    """return the reflexive transitive closure of {x}.union(vars(conds)) for relation uRv iif there exist prop and f s.t prop = (u,f(v))"""
    variables = {self._abstracted_variable}
    variables.update(self.product_agent.get_conditions_variables())
    return self.product_agent.transitive_closure_update(variables)




#-------------------------- Auxiliaries ---------------------------------------
#independent from any Abstraction's attribute


def parse_agent_name(agent_name :str):
  """return the template of agent named agent_name and its rank"""
  for i in range(len(agent_name)):
    if agent_name[i] in ['0','1','2','3','4','5','6','7','8','9']:
      try:
        return agent_name[:i],int(agent_name[i:])
      except ValueError:
        raise Exception(f"Error while parsing agent name {agent_name}: Only [a-z]* templates are supported")
  raise Exception(f"Error while parsing agent_name {agent_name} : Only template_aID names are supported")


def convert_integers_to_letters(agent_name : str):
  """write integers in letter to differentiate "single models" ID and "product model" ID [e.g p1xp2 -> p_one x p_two]"""
  conversion = ["zero","one","two","three","four","five","six","seven","eight","nine"]
  for i in range(10):
    agent_name = agent_name.replace(str(i),f"_{conversion[i]}")
  return agent_name



def mem_expr(variable : str, expr):
  """membership test for an expression [only integers or variables supported]""" 
  if isinstance(expr,str):
    return variable==expr
  return False


def mem_update_left(variable : str, update):
  """membership test for the left part of an update"""
  return variable==update[0]

def mem_update_right(variable : str, update):
  """membership test for the right part of an update"""
  expr = update[1]
  if isinstance(expr,str):
    return expr=='?' + variable
  return False

def mem_cond(variable : str, cond):
  """membership test for any part of a condition""" 
  return mem_expr(variable,cond[0]) or mem_expr(variable,cond[1])

def substitution(variable :str,update,value):
  """return expr[variable:=value] in the right part of an update"""
  if mem_update_right(variable,update):
      return value
  return expr

def removesuffix(string,suffix):
  """remove suffixe of a string. returns string otherwise"""
  i = len(string)-len(suffix)
  if string[i:]==suffix:
    return string[:i]
  return string

def extend_transitions(lst,ident):
  while len(lst)<ident+1:
    lst.append([])
  return lst


def create_suffix(props,suffixes):
  suffix = ""
  for var in suffixes:
    suffix += f"_{var}={props[var]}"
  return suffix


if __name__ == "__main__":
  from stv.models.asynchronous.parser import GlobalModelParser
  from stv.parsers import FormulaParser
  voter = 1
  cand = 2
  enable_trace = True
  filename =  f"tests_abstraction/example.txt"
  #filename =  f"tests_abstraction/shared-transitions.txt"
  #filename =  f"tests_abstraction/2_agents.txt"
  #filename =  f"tests_abstraction/Selene_{voter}_{cand}.txt"
  var = "x"
  #var = "x_p1"
  #var = "Voter1_vote"
  abstraction = Abstraction(filename,var,enable_trace=enable_trace)
  print(str(abstraction))
  variables = abstraction.compute_variables()
  print(f"closure of {{{ var}}} for relation uRv iif v appear in a guard or u=v is an update: {variables}\n")
  print(f"abstracting variable {var}...")
  abstraction.compute()
  abstraction.save()