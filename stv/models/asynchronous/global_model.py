from typing import List, Dict, Any
import time
from stv.models.asynchronous.global_state import GlobalState
from stv.models.asynchronous.local_model import LocalModel
from stv.models.asynchronous.local_transition import LocalTransition, SharedTransition
from stv.models import SimpleModel


class GlobalModel:
    """
    Represents global model.

    :param local_models:
    :param reduction:

    :ivar _model:
    :ivar _local_models:
    :ivar _reduction:
    :ivar _persistent:
    :ivar _states:
    :ivar _transitions:
    :ivar _dependent:
    :ivar _pre:
    :ivar _agents_count:
    :ivar _states_dict:
    :ivar _stack1:
    :ivar _stack2:
    :ivar _G:
    :ivar coalition:
    :ivar _stack1_dict:
    :ivar _transitions_count
    """

    def __init__(self, local_models: List[LocalModel], reduction: List[str], persistent: List[str]):
        self._model: SimpleModel = None
        self._local_models: List[LocalModel] = local_models
        self._reduction: List[str] = reduction
        self._persistent: List[str] = persistent
        self._states: List[GlobalState] = []
        self._transitions: List = []
        self._dependent: List[List[List[int]]] = []
        self._pre: List[List[List[LocalTransition]]] = []
        self._agents_count: int = 0
        self._states_dict: Dict[str, int] = dict()
        self._stack1: List[Any] = []
        self._stack2: List[int] = []
        self._G: List = []
        self.coalition: List = []
        self._stack1_dict: Dict[str, int] = dict()
        self._transitions_count: int = 0

    @property
    def model(self):
        """The model."""
        return self._model

    @property
    def states_count(self):
        return len(self._states)

    @property
    def transitions_count(self):
        return self._transitions_count

    def generate(self, reduction: bool = False):
        """
        Generates model.
        :param reduction: Should reductions be used.
        :return: None.
        """
        self._agents_count = len(self._local_models)
        self._model = SimpleModel(self._agents_count)
        self._add_to_stack(GlobalState.initial_state(self._agents_count))
        self._add_index_to_transitions()
        self._compute_dependent_transitions()
        self._compute_shared_transitions()
        if reduction:
            self._iter_por()
        else:
            self._compute()

    def _add_index_to_transitions(self):
        for agent_id in range(self._agents_count):
            for i in range(len(self._local_models[agent_id].transitions)):
                for j in range(len(self._local_models[agent_id].transitions[i])):
                    self._local_models[agent_id].transitions[i][j].i = i
                    self._local_models[agent_id].transitions[i][j].j = j

    def _compute_shared_transitions(self):
        replace = []
        for agent_id in range(self._agents_count):
            for i in range(len(self._local_models[agent_id].transitions)):
                for j in range(len(self._local_models[agent_id].transitions[i])):
                    transition = self._local_models[agent_id].transitions[i][j]
                    if not transition.shared:
                        continue

                    shared_transition = self._create_shared_transition(transition, agent_id)
                    shared_transition.transition_list.sort(key=lambda tran: tran.agent_id)
                    replace.append((agent_id, i, j, shared_transition))

        for rep in replace:
            agent_id, i, j, shared_transition = rep
            self._local_models[agent_id].transitions[i][j] = shared_transition

    def _create_shared_transition(self, transition: LocalTransition, agent_id: int) -> SharedTransition:
        shared_transition = SharedTransition(transition)
        for agent_id2 in range(self._agents_count):
            if agent_id == agent_id2:
                continue

            if self._local_models[agent_id2].has_action(transition.action):
                for transition2 in self._local_models[agent_id2].get_transitions():
                    if transition2.action == transition.action:
                        shared_transition.add_transition(transition2)
                        break

        return shared_transition

    def _available_transitions_in_state_for_agent(self, state: GlobalState, agent_id: int) -> List[LocalTransition]:
        """
        Computes a list of transitions available for the specified agent in the given state.
        :param state: Global state.
        :param agent_id: Agent identifier.
        :return: List of local transitions.
        """
        agent_state_id: int = state.local_states[agent_id]
        all_transitions: List[LocalTransition] = self._local_models[agent_id].private_transitions_from_state(
            agent_state_id)
        all_transitions += self._local_models[agent_id].shared_transitions_from_state(agent_state_id)
        return list(filter(lambda transition: transition.check_conditions(state), all_transitions))

    def _enabled_transitions_in_state(self, state: GlobalState) -> List[List[LocalTransition]]:
        """
        Computes all enabled transitions for the given global state.
        :param state:
        :return:
        """
        all_transitions = []
        for agent_id in range(len(self._local_models)):
            all_transitions.append(self._available_transitions_in_state_for_agent(state, agent_id))

        result = []
        for agent_id in range(self._agents_count):
            result.append(self._enabled_transitions_for_agent(agent_id, all_transitions))

        return result

    def _enabled_transitions_for_agent(self, agent_id: int, all_transitions: List[List[LocalTransition]]):
        """
        Computes enabled transitions for given agent based on the transitions from the global state.
        :param agent_id: Agent identifier.
        :param all_transitions: List containing all of the transitions going out from specific global state.
        :return:
        """
        result = []
        for transition in all_transitions[agent_id]:
            if not transition.shared:
                result.append(transition)
                continue

            if self._check_if_shared_transition_is_enabled(transition, agent_id, all_transitions):
                result.append(transition)

        return result

    def _check_if_shared_transition_is_enabled(self, transition: LocalTransition, agent_id: int,
                                               all_transitions: List[List[LocalTransition]]) -> bool:
        is_ok = True
        for agent_id2 in range(len(self._local_models)):
            if agent_id2 == agent_id:
                continue

            if self._local_models[agent_id2].has_action(transition.action):
                is_ok = False
                for transition2 in all_transitions[agent_id2]:
                    if transition2.shared and transition2.action == transition.action:
                        is_ok = True
                        break

            if not is_ok:
                return False

        return True

    def _enabled_transitions_in_state_single_item_set(self, state: GlobalState):
        enabled = self._enabled_transitions_in_state(state)
        result = set()
        for agent_id in range(self._agents_count):
            for transition in enabled[agent_id]:
                result.add(transition.to_tuple())
                if not transition.shared:
                    continue
                for agent_id2 in range(agent_id + 1, self._agents_count):
                    i = 0
                    for transition2 in enabled[agent_id2]:
                        if transition2.shared and transition2.action == transition.action:
                            enabled[agent_id2].pop(i)
                            break
                        i += 1
        return result

    def _new_state_after_private_transition(self, state: GlobalState, transition: LocalTransition):
        agent_id = transition.agent_id
        new_state = GlobalState.copy_state(state, self._persistent)
        new_state.set_local_state(agent_id, self._local_models[agent_id].get_state_id(transition.state_to))
        new_state.increment_counter(agent_id)
        new_state = self._copy_props_to_state(new_state, transition)
        return new_state

    def _new_state_after_shared_transition(self, state: GlobalState, actual_transition):
        new_state = GlobalState.copy_state(state, self._persistent)
        agents = []
        for act_tran in actual_transition:
            new_state.increment_counter(act_tran[0])
            new_state.set_local_state(act_tran[0], self._local_models[act_tran[0]].get_state_id(
                act_tran[1].state_to))
            new_state = self._copy_props_to_state(new_state, act_tran[1])
            agents.append(act_tran[0])
        return new_state, agents

    def _new_state_after_shared_transitions_list(self, state: GlobalState, transitions: List[LocalTransition]):
        new_state = GlobalState.copy_state(state, self._persistent)
        for transition in transitions:
            new_state.set_local_state(transition.agent_id,
                                      self._local_models[transition.agent_id].get_state_id(transition.state_to))
            new_state = self._copy_props_to_state(new_state, transition)
        return new_state

    def _compute_next_for_state(self, state: GlobalState, current_state_id: int):
        all_transitions = self._enabled_transitions_in_state(state)
        visited = []
        for agent_id in range(len(self._local_models)):
            self._compute_next_for_state_for_agent(state, current_state_id, agent_id, visited, all_transitions)

    def _compute_next_for_state_for_agent(self, state: GlobalState, current_state_id: int, agent_id: int, visited: [],
                                          all_transitions: []):
        for transition in all_transitions[agent_id]:
            if transition.shared and transition.action not in visited:
                visited.append(transition.action)
                actual_transition = [(agent_id, transition)]
                for n_a_id in range(agent_id + 1, len(self._local_models)):
                    for n_tr in all_transitions[n_a_id]:
                        if n_tr.shared and n_tr.action == transition.action:
                            actual_transition.append((n_a_id, n_tr))
                            break
                new_state, agents = self._new_state_after_shared_transition(state, actual_transition)
                new_state_id = self._add_state(new_state)
                self._add_transition(current_state_id, new_state_id, transition.action, agents)
            elif not transition.shared:
                new_state = self._new_state_after_private_transition(state, transition)
                new_state_id = self._add_state(new_state)
                self._add_transition(current_state_id, new_state_id, transition.action, [agent_id])

    def _copy_props_to_state(self, state: GlobalState, transition: LocalTransition) -> GlobalState:
        for prop in transition.props:
            if transition.props[prop] == "?":
                pass
            elif type(transition.props[prop]) is str:
                if transition.props[prop] in state.props:
                    state.set_prop(prop, state.props[transition.props[prop]])
            elif type(transition.props[prop]) is bool:
                if not transition.props[prop]:
                    state.remove_prop(prop)
                else:
                    state.set_prop(prop, transition.props[prop])
            else:
                state.set_prop(prop, transition.props[prop])
        return state

    def _state_find(self, state: GlobalState):
        if state.to_str() in self._states_dict:
            return self._states_dict[state.to_str()]

        return -1

    def _compute_dependent_transitions(self):
        for agent_id in range(self._agents_count):
            self._dependent.append([])
            agent_transitions = self._local_models[agent_id].get_transitions()
            for i in range(0, len(agent_transitions)):
                self._dependent[agent_id].append([agent_id])
                for agent2_id in range(self._agents_count):
                    if agent_id == agent2_id:
                        continue

                    if self._local_models[agent2_id].has_action(agent_transitions[i].action):
                        self._dependent[agent_id][i].append(agent2_id)

    def _is_in_G(self, state: GlobalState):
        for st in self._G:
            if st.equal(state):
                return True
        return False

    def _find_state_on_stack1(self, state: GlobalState):
        str_state = state.to_str()

        if str_state in self._stack1_dict:
            return self._stack1_dict[str_state]

        return -1

    def _add_to_stack(self, state: GlobalState):
        str_state = state.to_str()

        if str_state in self._stack1_dict:
            return False
        else:
            self._stack1.append(state)
            self._stack1_dict[state.to_str()] = len(self._stack1) - 1
            return True

    def _pop_from_stack(self):
        self._stack1_dict[self._stack1[-1].to_str()] = -1
        self._stack1.pop()

    def _dfs_por(self):
        """
        Recursive partial order reductions algorithm.
        :return: None.
        """
        g = self._stack1[-1]
        reexplore = False

        i = self._find_state_on_stack1(g)

        if i != -1 and i != len(self._stack1) - 1:
            if not self._stack2:
                depth = 0
            else:
                depth = self._stack2[-1]
            if i > depth:
                reexplore = True
            else:
                self._pop_from_stack()
                return

        if not reexplore and self._is_in_G(g):
            self._pop_from_stack()
        g_state_id = self._add_state(g)
        en_g = self._enabled_transitions_in_state_single_item_set(g)
        if len(en_g) > 0:
            if not reexplore:
                E_g = self._ample(g)
            if len(E_g) == 0:
                E_g = en_g
            if E_g == en_g:
                self._stack2.append(len(self._stack1))
            for tup in E_g:
                a = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
                g_p = self._successor(g, a)
                g_p_state_id = self._add_state(g_p)
                self._add_transition(g_state_id, g_p_state_id, a.action, [a.agent_id])  # TODO agents ids
                if self._add_to_stack(g_p):
                    self._dfs_por()
        if len(self._stack2) == 0:
            depth = 0
        else:
            depth = self._stack2[-1]
        if depth == len(self._stack1):
            self._stack2.pop()
        self._pop_from_stack()

    def _iter_por(self):
        """
        Iterative partial order reduction algorithm.
        :return: None.
        """
        dfs_stack = [1]
        while len(dfs_stack) > 0:
            dfs = dfs_stack.pop()
            if dfs == 1:
                g = self._stack1[-1]
                reexplore = False
                i = self._find_state_on_stack1(g)
                if i != -1 and i != len(self._stack1) - 1:
                    if len(self._stack2) == 0:
                        depth = 0
                    else:
                        depth = self._stack2[-1]
                    if i > depth:
                        reexplore = True
                    else:
                        self._pop_from_stack()
                        return

                if not reexplore and self._is_in_G(g):
                    self._pop_from_stack()
                    return
                self._G.append(g)
                g_state_id = self._add_state(g)
                E_g = []
                en_g = self._enabled_transitions_in_state_single_item_set(g)
                if len(en_g) > 0:
                    if not reexplore:
                        E_g = self._ample(g)
                    if len(E_g) == 0:
                        E_g = en_g
                    if E_g == en_g:
                        self._stack2.append(len(self._stack1))
                    dfs_stack.append(-1)
                    for tup in E_g:
                        a = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
                        g_p = self._successor(g, a)
                        g_p_state_id = self._add_state(g_p)
                        self._add_transition(g_state_id, g_p_state_id, a.action, [a.agent_id])
                        if self._add_to_stack(g_p):
                            dfs_stack.append(1)
            elif dfs == -1:
                if len(self._stack2) == 0:
                    depth = 0
                else:
                    depth = self._stack2[-1]
                if depth == len(self._stack1):
                    self._stack2.pop()
                self._pop_from_stack()

    def _ample(self, state: GlobalState):
        """
        Computes ample set for given state.
        :param state: Global state.
        :return: Ample set.
        """
        V = self._enabled_transitions_in_state_single_item_set(state)
        while V:
            alpha = V.pop()
            V.add(alpha)
            X = {alpha}
            U = {alpha}
            DIS = set()
            while X and not X.difference(V):
                DIS.update(self._enabled_for_x(X))
                X = self._dependent_for_x(X, DIS, U)
                U.update(X)
            if not X and not self._check_for_cycle(state, U):
                return U
            V.difference_update(U)
        return {}

    def _check_for_cycle(self, state: GlobalState, X: set):
        for tup in X:
            transition = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
            successor_state = self._successor(state, transition)
            if self._find_state_on_stack1(successor_state) != -1:
                return True
        return False

    def _enabled_for_x(self, X):
        result = set()

        for tup in X:
            transition = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
            if isinstance(transition, SharedTransition):
                for transition2 in transition.transition_list:
                    for tr in self._local_models[transition2.agent_id].get_transitions():
                        if tr.state_from != transition2.state_from:
                            result.add(tr.to_tuple())
            else:
                for tr in self._local_models[transition.agent_id].get_transitions():
                    if tr.state_from != transition.state_from:
                        result.add(tr.to_tuple())

        return result

    def _dependent_for_x(self, X, DIS, U):  # !!!!
        result = set()
        for tup in X:
            transition = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
            if isinstance(transition, SharedTransition):
                for transition2 in transition.transition_list:
                    for tr in self._local_models[transition2.agent_id].get_transitions():
                        if tr.to_tuple() not in DIS and tr.to_tuple() not in U:
                            result.add(tr.to_tuple())
            else:
                for tr in self._local_models[transition.agent_id].get_transitions():
                    if tr.to_tuple() not in DIS and tr.to_tuple() not in U:
                        result.add(tr.to_tuple())

        return result

    def _successor(self, state: GlobalState, transition: LocalTransition):
        if not isinstance(transition, SharedTransition):
            return self._new_state_after_private_transition(state, transition)
        else:
            return self._new_state_after_shared_transitions_list(state, transition.transition_list)

    def _add_state(self, state: GlobalState):
        state_id = self._state_find(state)
        if state_id == -1:
            state_id = len(self._states)
            state.id = state_id
            self._states.append(state)
            self._states_dict[state.to_str()] = state_id

        state.id = state_id
        return state_id

    def _add_transition(self, state_from: int, state_to: int, action: str, agents: List[int]):
        while len(self._transitions) <= state_from:
            self._transitions.append([])

        self._transitions[state_from].append({'from': state_from, 'to': state_to, 'action': action, 'agents': agents})
        self._transitions_count += 1
        self._model.add_transition(state_from, state_to, self._create_list_of_actions(action, agents))

    def _create_list_of_actions(self, action: str, agents: List[int]):
        actions = ['' for _ in range(self._agents_count)]
        for agent_id in agents:
            actions[agent_id] = action
        return actions

    def _compute(self):
        """
        Compute global model.
        :return:
        """
        state = GlobalState.initial_state(len(self._local_models))
        self._states.append(state)
        i = 0
        while i < len(self._states):
            state = self._states[i]
            current_state_id = i
            i += 1

            self._compute_next_for_state(state, current_state_id)

    def agent_name_to_id(self, agent_name: str) -> int:
        for agent_id in range(len(self._local_models)):
            if self._local_models[agent_id].agent_name == agent_name:
                return agent_id
        return -1

    def agent_name_coalition_to_ids(self, agent_names: List[str]) -> List[int]:
        agent_ids = []
        for agent_name in agent_names:
            agent_ids.append(self.agent_name_to_id(agent_name))
        return agent_ids

    def walk(self):
        print("Simulation start")
        current_state_id = 0
        while True:
            print("Current state:")
            self._states[current_state_id].print()
            print("Transitions:")
            for i in range(0, len(self._transitions[current_state_id])):
                print(f"{i}: ", end="")
                self._pretty_print_transition(self._transitions[current_state_id][i])
                # print(f"{i}: {self._transitions[current_state_id][i]}")

            id = int(input("Select transition: "))
            current_state_id = self._transitions[current_state_id][id]['to']

    def _pretty_print_transition(self, t):
        print(f"{t['from']} -({t['action']})-> {t['to']}, agents: ", end="")
        for ag in t['agents']:
            print(f"{self._local_models[ag].agent_name}, ", end="")
        print()

    def print_dependent_transitions(self):
        for agent_id in range(self._agents_count):
            print(f"Agent {self._local_models[agent_id].agent_name}")
            agent_transitions = self._local_models[agent_id].get_transitions()
            for i in range(0, len(agent_transitions)):
                print("Transition:")
                agent_transitions[i].print()
                print("Dependent:")
                for agent2_id in self._dependent[agent_id][i]:
                    print(f"{self._local_models[agent2_id].agent_name}")
                print()
            print()

    def print(self):
        for model in self._local_models:
            model.print()

    def set_coalition(self, coalition: List[str]):
        self.coalition = self.agent_name_coalition_to_ids(coalition)


if __name__ == "__main__":
    from stv.models.asynchronous.parser import GlobalModelParser

    results_file = open("selene_results.txt", "a")

    teller_count = int(input("Teller Count: "))
    voter_count = int(input("Voter Count: "))
    cand_count = int(input("Candidates Count: "))
    reduction = int(input("Reduction: "))

    file_name = f"Selene_{teller_count}_{voter_count}_{cand_count}.txt"
    model = GlobalModelParser().parse(file_name)
    # coalition = ["Coercer1"]
    # model.set_coalition(coalition)
    start = time.process_time()
    model.generate(reduction=(reduction == 1))
    end = time.process_time()
    print(f"Model generated in {end - start} seconds.")
    print(f"Model has {model.states_count} states.")
    print(f"Model has {model.transitions_count} transitions.")

    results_file.write(f"Teller Count: {teller_count}\n")
    results_file.write(f"Voter Count: {voter_count}\n")
    results_file.write(f"Candidates Count: {cand_count}\n")
    results_file.write(f"Reduction: {reduction == 1}\n")
    results_file.write(f"Model generated in {end - start} seconds.\n")
    results_file.write(f"Model has {model.states_count} states.\n")
    results_file.write(f"Model has {model.transitions_count} transitions.\n")
    results_file.write("\n\n")
    results_file.close()

    # model.walk()

    # model.print()
    # model.parse("train_controller.txt")
    # model.parse("selene.txt")
    # model.print()
    # coalition = ["Coercer1"]
    # model.set_coalition(coalition)
    # print(f"Coalition: {coalition}")

    # model.generate(reduction=True)

    # print()
    #
    # print(f"Model has {model.states_count} states.")
    # print(f"Model has {model.transitions_count} transitions.")
    # print()
    # model.walk()
