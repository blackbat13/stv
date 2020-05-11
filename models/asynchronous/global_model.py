from typing import List, Dict
from tools import StringTools
from models.asynchronous.global_state import GlobalState
from models.asynchronous.local_model import LocalModel
from models.asynchronous.local_transition import LocalTransition, SharedTransition
import time


class GlobalModel:
    def __init__(self):
        self._local_models: List[LocalModel] = []
        self._states: List[GlobalState] = []
        self._transitions = []
        self._dependent: List[List[List[int]]] = []
        self._pre: List[List[List[LocalTransition]]] = []
        self._agents_count: int = 0
        self._reduction: List[str] = []
        self._states_dict: Dict[str, int] = dict()
        self._stack1 = []
        self._stack2 = []
        self._G = []
        self.coalition = []
        self._stack1_dict: Dict[str, int] = dict()
        self._transitions_count = 0

    @property
    def states_count(self):
        return len(self._states)

    @property
    def transitions_count(self):
        return self._transitions_count

    def parse(self, file_name: str):
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()

        i = 0
        while i < len(lines):
            if StringTools.is_blank_line(lines[i]):
                i += 1
                continue
            if self._is_agent_header(lines[i]):
                line_from = i
                i = self._find_agent_end(lines, i + 1)
                line_to = i
                agent_max = self._parse_agent_max(lines[line_from])
                for agent_id in range(1, agent_max + 1):
                    local_model = LocalModel(len(self._local_models))
                    local_model.parse("".join(lines[line_from:line_to]), agent_id)
                    self._local_models.append(local_model)
            elif self._is_reduction_header(lines[i]):
                self._reduction = self._parse_reduction(lines[i])
                i += 1

        self._agents_count = len(self._local_models)
        self._add_to_stack(GlobalState.initial_state(self._agents_count))
        self._add_index_to_transitions()
        self._compute_dependent_transitions()
        self._compute_shared_transitions()

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

                    shared_transition = SharedTransition(transition)
                    for agent_id2 in range(self._agents_count):
                        if agent_id == agent_id2:
                            continue
                        if self._local_models[agent_id2].has_action(transition.action):
                            for tr in self._local_models[agent_id2].get_transitions():
                                if tr.action == transition.action:
                                    shared_transition.add_transition(tr)
                                    break

                    shared_transition.transition_list.sort(key=lambda tr: tr.agent_id)

                    replace.append((agent_id, i, j, shared_transition))
        for r in replace:
            agent_id, i, j, shared_transition = r
            self._local_models[agent_id].transitions[i][j] = shared_transition

    def _find_agent_end(self, lines: List[str], line_index: int):
        while line_index < len(lines) and not StringTools.is_blank_line(
                lines[line_index]) and not self._is_agent_header(lines[line_index]):
            line_index += 1
        return line_index

    def _is_agent_header(self, line: str):
        return line[0:5] == "Agent"

    def _is_reduction_header(self, line: str):
        return line[0:9] == "REDUCTION"

    def _parse_reduction(self, line: str) -> List[str]:
        line = line.split(":")[1]
        line = line.strip().strip("[").strip("]")
        red = []
        for el in line.split(","):
            red.append(el.strip())
        return red

    def _parse_agent_max(self, line: str):
        if len(line.split("[")) > 1:
            return int(line.split("[")[1].split("]")[0])
        return 1

    def _enabled_transitions_in_state_for_agent(self, state: GlobalState, agent_id: int) -> List[LocalTransition]:
        agent_state_id = state.local_states[agent_id]
        all_transitions = self._local_models[agent_id].private_transitions_from_state(agent_state_id)
        all_transitions += self._local_models[agent_id].shared_transitions_from_state(agent_state_id)
        result = []
        for transition in all_transitions:
            ok = True
            if transition.conditions:
                for cond in transition.conditions:
                    if cond[2] == "==" and ((cond[0] not in state.props) or (state.props[cond[0]] != cond[1])):
                        ok = False
                        break
                    elif cond[2] == "!=" and cond[0] in state.props and state.props[cond[0]] == cond[1]:
                        ok = False
                        break

            if ok:
                result.append(transition)
        return result

    def _enabled_transitions_in_state(self, state: GlobalState) -> List[List[LocalTransition]]:
        all_transitions = []
        for agent_id in range(len(self._local_models)):
            all_transitions.append(self._enabled_transitions_in_state_for_agent(state, agent_id))

        result = []
        for agent_id in range(self._agents_count):
            result.append([])
            for transition in all_transitions[agent_id]:
                if not transition.shared:
                    result[agent_id].append(transition)
                    continue
                ok = True
                for a_id in range(len(self._local_models)):
                    if a_id == agent_id:
                        continue
                    if self._local_models[a_id].has_action(transition.action):
                        ok = False
                        for tr in all_transitions[a_id]:
                            if tr.shared and tr.action == transition.action:
                                ok = True
                                break
                    if not ok:
                        break
                if ok:
                    result[agent_id].append(transition)
        return result

    def _enabled_transitions_in_state_single_list(self, state: GlobalState):
        enabled = self._enabled_transitions_in_state(state)
        result = []
        for agent_id in range(self._agents_count):
            for transition in enabled[agent_id]:
                result.append([transition])
                if not transition.shared:
                    continue
                for agent_id2 in range(agent_id + 1, self._agents_count):
                    i = 0
                    for transition2 in enabled[agent_id2]:
                        if transition2.shared and transition2.action == transition.action:
                            result[-1].append(transition2)
                            enabled[agent_id2].pop(i)
                            break
                        i += 1
        return result

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
        new_state = GlobalState.copy_state(state)
        new_state.set_local_state(agent_id, self._local_models[agent_id].get_state_id(transition.state_to))
        new_state.increment_counter(agent_id)
        new_state = self._copy_props_to_state(new_state, transition)
        return new_state

    def _new_state_after_shared_transition(self, state: GlobalState, actual_transition):
        new_state = GlobalState.copy_state(state)
        agents = []
        for act_tran in actual_transition:
            new_state.increment_counter(act_tran[0])
            new_state.set_local_state(act_tran[0], self._local_models[act_tran[0]].get_state_id(
                act_tran[1].state_to))
            new_state = self._copy_props_to_state(new_state, act_tran[1])
            agents.append(act_tran[0])
        return new_state, agents

    def _new_state_after_shared_transitions_list(self, state: GlobalState, transitions: List[LocalTransition]):
        new_state = GlobalState.copy_state(state)
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

    def _compute_pre_transitions(self):
        for agent_id in range(0, len(self._local_models)):
            self._pre.append([])
            agent_transitions = self._local_models[agent_id].get_transitions()
            for i in range(0, len(agent_transitions)):
                transition = agent_transitions[i]
                self._pre[agent_id].append([])
                self._pre[agent_id][i].extend(self._local_models[agent_id].pre_transitions(transition))
                if not transition.shared:
                    continue

                for agent_id2 in range(0, len(self._local_models)):
                    if agent_id == agent_id2:
                        continue

                    if not self._local_models[agent_id2].has_action(transition.action):
                        continue

                    transition2 = self._local_models[agent_id2].find_transition(transition.action)
                    self._pre[agent_id][i].extend(self._local_models[agent_id2].pre_transitions(transition2))

    def _check1(self, agent_id: int, current: List[LocalTransition], state: GlobalState):
        for agent2_id in range(0, len(self._local_models)):
            if agent_id == agent2_id:
                continue

            transitions = self._local_models[agent_id].transitions_from_state(state.local_states[agent_id])

            for tr in transitions:
                if agent2_id in self._dependent[tr.agent_id][tr.id]:
                    return False

            all_pre = set()
            for tr in current:
                all_pre.update(set(self._pre[tr.agent_id][tr.id]))

            all_transitions = self._local_models[agent_id].get_transitions()
            all_pre.difference_update(set(all_transitions))
            # TODO check for correctness:
            all_pre.intersection_update(self._local_models[agent2_id].get_transitions())

            if len(all_pre) > 0:
                return False
        return True

    def _check2(self, agent_id: int, transition_candidates: List[LocalTransition], coalition: List[int]) -> bool:
        if agent_id in coalition:
            return False

        for transition in transition_candidates:
            for prop in transition.props:
                if prop in self._reduction:
                    return False

        return True

    def _check3(self, current_state_id: int, state: GlobalState) -> bool:
        for i in range(current_state_id + 1, len(self._states)):
            if self._states[i].equal(state):
                return False
        return True

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

    def dfs_por(self):
        g = self._stack1[-1]  # 1. g = Top(Stack1)
        reexplore = False  # 1. reexplore = false

        i = self._find_state_on_stack1(g)

        if i != -1 and i != len(self._stack1) - 1:
            if len(self._stack2) == 0:
                depth = 0
            else:
                depth = self._stack2[-1]  # 3. depth = Top(Stack2)
            if i > depth:  # 4. if i > depth then
                reexplore = True  # 4. reexplore = true
            else:  # 4. else
                self._pop_from_stack()
                # self._stack1.pop()  # 4. Pop(Stack1)
                return  # 4. return

        if not reexplore and self._is_in_G(g):  # 6. if reexplore = false and g in G
            # self._stack1.pop()  # 6. Pop(Stack1)
            self._pop_from_stack()
            return  # 6. return
        self._G.append(g)  # 7. G = G u g
        g_state_id = self._add_state(g)
        E_g = []  # 7. E(g) = empty
        en_g = self._enabled_transitions_in_state_single_item_set(g)
        if len(en_g) > 0:  # 8. if en(g) not empty
            if not reexplore:  # 9. if reexplore = false
                E_g = self._ample(g)
                # print("E_g:")
                # for tup in E_g:
                #     a = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
                #     a.print()
                # print()
                # print(E_g)
                # for a in en_g:  # 10. for all a in en(g)
                #     if not self._is_visible(a) and self._is_independent(a[0], en_g):  # 11. if a not in Vis and...
                #         E_g = [a]  # 11. E(g) = {a}
                #         # E_g.append(a)  # 11. E(g) = E(g)u {a}
                #         print(a[0].print())
                #         break
            if len(E_g) == 0:  # 14. if E(g) is empty
            # if len(E_g) != 1:  # 14. if |E(g)| != 1
                E_g = en_g  # 14. E(g) = en(g)
            if E_g == en_g:  # 15. if E(g) = en(g)
                self._stack2.append(len(self._stack1))  # 15. Push(Stack2,Depth(Stack1))
            for tup in E_g:  # 16. for all a in E(g)
                a = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
                g_p = self._successor(g, a)  # 16. g' = Successor(g,a)
                g_p_state_id = self._add_state(g_p)
                self._add_transition(g_state_id, g_p_state_id, a.action, [a.agent_id])  # TODO agents ids
                # self._stack1.append(g_p)  # 16. Push(Stack1, g')
                if self._add_to_stack(g_p):
                    self.dfs_por()  # 16. DFS-POR()
        if len(self._stack2) == 0:
            depth = 0
        else:
            depth = self._stack2[-1]  # 18. depth = Top(Stack2)
        if depth == len(self._stack1):  # 19. if depth = Depth(Stack1)
            self._stack2.pop()  # 19. Pop(Stack2)
        self._pop_from_stack()
        # self._stack1.pop()  # 20. Pop(Stack1)

    def iter_por(self):
        dfs_stack = [1]
        while len(dfs_stack) > 0:
            dfs = dfs_stack.pop()
            if dfs == 1:
                g = self._stack1[-1]  # 1. g = Top(Stack1)
                reexplore = False  # 1. reexplore = false

                i = self._find_state_on_stack1(g)

                if i != -1 and i != len(self._stack1) - 1:
                    if len(self._stack2) == 0:
                        depth = 0
                    else:
                        depth = self._stack2[-1]  # 3. depth = Top(Stack2)
                    if i > depth:  # 4. if i > depth then
                        reexplore = True  # 4. reexplore = true
                    else:  # 4. else
                        self._pop_from_stack()
                        # self._stack1.pop()  # 4. Pop(Stack1)
                        return  # 4. return

                if not reexplore and self._is_in_G(g):  # 6. if reexplore = false and g in G
                    # self._stack1.pop()  # 6. Pop(Stack1)
                    self._pop_from_stack()
                    return  # 6. return
                self._G.append(g)  # 7. G = G u g
                g_state_id = self._add_state(g)
                E_g = []  # 7. E(g) = empty
                en_g = self._enabled_transitions_in_state_single_item_set(g)
                if len(en_g) > 0:  # 8. if en(g) not empty
                    if not reexplore:  # 9. if reexplore = false
                        E_g = self._ample(g)
                    if len(E_g) == 0:  # 14. if E(g) is empty
                        E_g = en_g  # 14. E(g) = en(g)
                    if E_g == en_g:  # 15. if E(g) = en(g)
                        self._stack2.append(len(self._stack1))  # 15. Push(Stack2,Depth(Stack1))
                    dfs_stack.append(-1)
                    for tup in E_g:  # 16. for all a in E(g)
                        a = self._local_models[tup[0]].transitions[tup[1]][tup[2]]
                        g_p = self._successor(g, a)  # 16. g' = Successor(g,a)
                        g_p_state_id = self._add_state(g_p)
                        self._add_transition(g_state_id, g_p_state_id, a.action, [a.agent_id])
                        if self._add_to_stack(g_p):
                            dfs_stack.append(1)
            elif dfs == -1:
                if len(self._stack2) == 0:
                    depth = 0
                else:
                    depth = self._stack2[-1]  # 18. depth = Top(Stack2)
                if depth == len(self._stack1):  # 19. if depth = Depth(Stack1)
                    self._stack2.pop()  # 19. Pop(Stack2)
                self._pop_from_stack()

    def _ample(self, s: GlobalState):
        V = self._enabled_transitions_in_state_single_item_set(s)
        while len(V) > 0:
            alpha = V.pop()  # choose some alpha in V
            V.add(alpha)
            X = {alpha}
            U = {alpha}
            DIS = set()
            while len(X) > 0 and len(X.difference(V)) == 0:
                # DIS = DIS.union(self._enabled_for_x(X))
                DIS.update(self._enabled_for_x(X))
                X = self._dependent_for_x(X, DIS, U)
                # U = U.union(X)
                U.update(X)
            if len(X) == 0 and not self._check_for_cycle(s, U):
                return U
            V.difference_update(U)
            # V = V.difference(U)
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

    def _is_independent(self, transition: LocalTransition, en_g: List[List[LocalTransition]]):
        for tr_list in en_g:
            if transition == tr_list[0]:
                continue
            if tr_list[0].agent_id in self._dependent[transition.agent_id][transition.id]:
                return False

        return True

    def _is_visible(self, transitions: [LocalTransition]):
        for tr in transitions:
            if tr.agent_id in self.coalition:
                return True
            for prop in tr.props:
                if prop in self._reduction:
                    return True
        return False

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

    def compute(self):
        state = GlobalState.initial_state(len(self._local_models))
        self._states.append(state)
        i = 0
        while i < len(self._states):
            state = self._states[i]
            current_state_id = i
            i += 1

            self._compute_next_for_state(state, current_state_id)

    def compute_reduced(self, coalition: List[int]):
        self._compute_dependent_transitions()
        self._compute_pre_transitions()

        state = GlobalState.initial_state(len(self._local_models))
        self._states.append(state)
        i = 0
        while i < len(self._states):
            state = self._states[i]
            current_state_id = i
            i += 1

            ok = False
            enabled_transitions = self._enabled_transitions_in_state(state)

            for agent_id in range(0, len(self._local_models)):
                transition_candidates = enabled_transitions[agent_id]

                if not self._check2(agent_id, transition_candidates, coalition):
                    continue

                current = transition_candidates[:]
                current.extend(self._local_models[agent_id].current_transitions(state.local_states[agent_id],
                                                                                state.counters[agent_id]))

                if not self._check1(agent_id, current, state):
                    continue

                if not self._check3(current_state_id, state):
                    continue

                ok = True
                self._compute_next_for_state_for_agent(state, current_state_id, agent_id, [], enabled_transitions)

                break

            if not ok:
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
                print(f"{i}: {self._transitions[current_state_id][i]}")

            id = int(input("Select transition: "))
            current_state_id = self._transitions[current_state_id][id]['to']

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
    model = GlobalModel()
    # model.parse("train_controller.txt")
    model.parse("voting_4_2.txt")
    # model.parse("selene.txt")
    # model.print()
    coalition = ["Coercer1"]
    model.set_coalition(coalition)
    print(f"Coalition: {coalition}")
    start = time.process_time()
    # model.compute_reduced(coalition)
    # model.compute()
    # model.dfs_por()
    model.iter_por()
    end = time.process_time()
    print()
    print(f"Model generated in {end - start} seconds.")
    print(f"Model has {model.states_count} states.")
    print(f"Model has {model.transitions_count} transitions.")
    print()
    # model.walk()
