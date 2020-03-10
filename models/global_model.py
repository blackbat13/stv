from models.local_model import LocalModel
from models.local_transition import LocalTransition
from typing import List
from tools import StringTools


class GlobalModel:
    def __init__(self):
        self._local_models: List[LocalModel] = []
        self._states = []
        self._transitions = []
        self._dependent: List[List[List[int]]] = []
        self._pre: List[List[List[LocalTransition]]] = []
        self._agents_count: int = 0
        self._reduction: List[str] = []
        self._unique_states = []

    @property
    def states_count(self):
        return len(self._states)

    def parse(self, file_name: str):
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()

        i = 0
        while i < len(lines):
            if StringTools.is_blank_line(lines[i]):
                i += 1
                continue
            # print(i)
            # print(lines[i])
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
                # print("Hello")

        self._agents_count = len(self._local_models)

    def _find_agent_end(self, lines: List[str], line_index: int):
        while line_index < len(lines) and not StringTools.is_blank_line(
                lines[line_index]) and not self._is_agent_header(
            lines[line_index]):
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

    def _enabled_transitions_in_state_for_agent(self, state: {}, agent_id: int) -> List[LocalTransition]:
        agent_state_id = state['val'][agent_id]
        all_transitions = self._local_models[agent_id].private_transitions_from_state(agent_state_id)
        all_transitions += self._local_models[agent_id].shared_transitions_from_state(agent_state_id)
        result = []
        for transition in all_transitions:
            ok = True
            if transition.conditions:
                for cond in transition.conditions:
                    if cond[2] == "==" and ((cond[0] not in state['props']) or (state['props'][cond[0]] != cond[1])):
                        ok = False
                        break
                    elif cond[2] == "!=" and cond[0] in state['props'] and state['props'][cond[0]] == cond[1]:
                        ok = False
                        break

            if ok:
                result.append(transition)
        return result

    def _enabled_transitions_in_state(self, state: {}) -> List[List[LocalTransition]]:
        all_transitions = []
        for agent_id in range(len(self._local_models)):
            all_transitions.append(self._enabled_transitions_in_state_for_agent(state, agent_id))

        result = []
        for agent_id in range(len(self._local_models)):
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
                            if tr.action == transition.action:
                                ok = True
                                break
                    if not ok:
                        break
                if ok:
                    result[agent_id].append(transition)
        return result

    def compute_reduced(self, coalition: List[int]):
        self.compute_dependent_transitions()
        self.compute_pre_transitions()

        self.print_dependent_transitions()

        state = {'val': [0 for _ in self._local_models], 'props': {}, 'counters': [0 for _ in self._local_models]}
        self._states.append(state)
        i = 0
        while i < len(self._states):
            state = self._states[i]
            # print(state)
            current_state_id = i
            i += 1

            ok = False
            enabled_transitions = self._enabled_transitions_in_state(state)

            for agent_id in range(0, len(self._local_models)):
                transition_candidates = enabled_transitions[agent_id]

                if not self.check2(agent_id, transition_candidates, coalition):
                    continue

                current = transition_candidates[:]
                current.extend(self._local_models[agent_id].current_transitions(state['val'][agent_id],
                                                                                state['counters'][agent_id]))

                if not self.check1(agent_id, current, state):
                    continue

                if not self.check3(current_state_id, state):
                    continue

                ok = True
                self.compute_next_for_state_for_agent(state, current_state_id, agent_id, [], enabled_transitions)
                # for tr in transition_candidates:
                #     new_state = {'val': state['val'][:], 'props': state['props'].copy(), 'counters': state['counters'][:]}
                #     new_state['val'][agent_id] = self._local_models[agent_id].get_state_id(tr.state_to)
                #     agents = []
                #     if tr.shared:
                #         for agent2_id in range(self._agents_count):
                #             if self._local_models[agent2_id].has_action(tr.action):
                #                 state['counters'][agent2_id] += 1
                #                 agents.append(agent2_id)
                #     else:
                #         state['counters'][agent_id] += 1
                #         agents.append(agent_id)
                #
                #     new_state = self.copy_props_to_state(new_state, tr)
                #     new_state_id = self.add_state(new_state)
                #     self.add_transition(current_state_id, new_state_id, tr.action, agents)

                break

            if not ok:
                self.compute_next_for_state(state, current_state_id)

    def private_transitions_from_state(self, state: {}):
        private_transitions = []
        for model_id in range(0, len(self._local_models)):
            private_transitions.append(
                self._local_models[model_id].private_transitions_from_state(state['val'][model_id]))
        return private_transitions

    def compute_private_next_for_state(self, state: {}, current_state_id: int):
        private_transitions = self.private_transitions_from_state(state)

        for model_id in range(0, len(self._local_models)):
            for transition in private_transitions[model_id]:
                new_state = self.new_state_after_private_transition(state, transition, model_id)
                new_state_id = self.add_state(new_state)
                self.add_transition(current_state_id, new_state_id, transition.action, [model_id])

    def new_state_after_private_transition(self, state: {}, transition: LocalTransition, agent_id: int):
        new_state = {'val': state['val'][:], 'props': state['props'].copy(), 'counters': state['counters'][:]}
        new_state['val'][agent_id] = self._local_models[agent_id].get_state_id(transition.state_to)
        new_state['counters'][agent_id] += 1
        new_state = self.copy_props_to_state(new_state, transition)
        return new_state

    def add_state(self, state: {}):
        state_id = self.state_find(state)
        if state_id == -1:
            self._states.append(state)
            self._unique_states.append({'val': state['val'], 'props': state['props']})
            state_id = len(self._states) - 1

        return state_id

    def shared_transitions_from_state(self, state: {}):
        shared_transitions = []
        for model_id in range(0, len(self._local_models)):
            shared_transitions.append(
                self._local_models[model_id].shared_transitions_from_state(state['val'][model_id]))
        return shared_transitions

    def find_shared_transitions(self, agent_id: int, transition: LocalTransition,
                                shared_transitions: List[List[LocalTransition]]):
        actual_transition = [(agent_id, transition)]
        ok = True
        for model_id2 in range(0, len(self._local_models)):
            if model_id2 == agent_id:
                continue
            if self._local_models[model_id2].has_action(transition.action):
                ok = False
                if model_id2 < agent_id:
                    break
                for transition2 in shared_transitions[model_id2]:
                    if transition2.action == transition.action:
                        actual_transition.append((model_id2, transition2))
                        ok = True
                        break
            if not ok:
                break
        return ok, actual_transition

    def new_state_after_shared_transition(self, state: {}, actual_transition):
        new_state = {'val': state['val'][:], 'props': state['props'].copy(), 'counters': state['counters'][:]}
        agents = []
        for act_tran in actual_transition:
            new_state['counters'][act_tran[0]] += 1
            new_state['val'][act_tran[0]] = self._local_models[act_tran[0]].get_state_id(
                act_tran[1].state_to)
            new_state = self.copy_props_to_state(new_state, act_tran[1])
            agents.append(act_tran[0])
        return new_state, agents

    def compute_shared_next_for_state(self, state: {}, current_state_id: int):
        shared_transitions = self.shared_transitions_from_state(state)

        for model_id in range(0, len(self._local_models)):
            for transition in shared_transitions[model_id]:
                ok, actual_transition = self.find_shared_transitions(model_id, transition, shared_transitions)
                if not ok:
                    continue

                new_state, agents = self.new_state_after_shared_transition(state, actual_transition)
                new_state_id = self.add_state(new_state)
                self.add_transition(current_state_id, new_state_id, transition.action, agents)

    def compute_next_for_state(self, state: {}, current_state_id: int):
        all_transitions = self._enabled_transitions_in_state(state)
        visited = []
        for agent_id in range(len(self._local_models)):
            self.compute_next_for_state_for_agent(state, current_state_id, agent_id, visited, all_transitions)

        # self.compute_private_next_for_state(state, current_state_id)
        # self.compute_shared_next_for_state(state, current_state_id)

    def compute_next_for_state_for_agent(self, state: {}, current_state_id: int, agent_id: int, visited: [], all_transitions: []):
        for transition in all_transitions[agent_id]:
            if transition.shared and transition.action not in visited:
                # print(transition.action)
                visited.append(transition.action)
                # print(visited)
                actual_transition = [(agent_id, transition)]
                for n_a_id in range(agent_id + 1, len(self._local_models)):
                    for n_tr in all_transitions[n_a_id]:
                        if n_tr.shared and n_tr.action == transition.action:
                            actual_transition.append((n_a_id, n_tr))
                            break
                new_state, agents = self.new_state_after_shared_transition(state, actual_transition)
                new_state_id = self.add_state(new_state)
                self.add_transition(current_state_id, new_state_id, transition.action, agents)
            elif not transition.shared:
                new_state = self.new_state_after_private_transition(state, transition, agent_id)
                new_state_id = self.add_state(new_state)
                self.add_transition(current_state_id, new_state_id, transition.action, [agent_id])

    def copy_props_to_state(self, state: {}, transition: LocalTransition):
        for prop in transition.props:
            if transition.props[prop] == "?":
                pass
            elif type(transition.props[prop]) is str:
                if transition.props[prop] in state['props']:
                    state['props'][prop] = state['props'][transition.props[prop]]
            else:
                state['props'][prop] = transition.props[prop]
            # state['props'][prop] = transition.props[prop]
        return state

    def state_find(self, state):
        # if state not in self._states:
        #     return -1
        # else:
        #     return self._states.index(state)

        for i in range(len(self._states)):
            if self._states[i]['val'] == state['val'] and self._states[i]['props'] == state['props']:
                return i

        # u_state = {'val': state['val'], 'props': state['props']}
        # if u_state not in self._unique_states:
        #     return -1
        # else:
        #     return self._unique_states.index(u_state)

        return -1

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

    def compute_dependent_transitions(self):
        for agent_id in range(self._agents_count):
            self._dependent.append([])
            agent_transitions = self._local_models[agent_id].get_transitions()
            for i in range(0, len(agent_transitions)):
                self._dependent[agent_id].append([])
                for agent2_id in range(self._agents_count):
                    if agent_id == agent2_id:
                        continue

                    if self._local_models[agent2_id].has_action(agent_transitions[i].action):
                        self._dependent[agent_id][i].append(agent2_id)

    def compute_pre_transitions(self):
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

    def check1(self, agent_id: int, current: List[LocalTransition], state: {}):
        for agent2_id in range(0, len(self._local_models)):
            if agent_id == agent2_id:
                continue

            transitions = self._local_models[agent_id].transitions_from_state(state['val'][agent_id])

            for tr in transitions:
                if agent2_id in self._dependent[tr.agent_id][tr.id]:
                    return False

            all_pre = set()
            for tr in current:
                all_pre.update(set(self._pre[tr.agent_id][tr.id]))

            all_transitions = self._local_models[agent_id].get_transitions()
            all_pre.difference_update(set(all_transitions))
            # TODO sprawdzić! pewnie nie jest do końca poprawnie:
            all_pre.intersection_update(self._local_models[agent2_id].get_transitions())

            if len(all_pre) > 0:
                return False
        return True

    def check3(self, current_state_id: int, state: {}) -> bool:
        for i in range(current_state_id + 1, len(self._states)):
            if self._states[i]['val'] == state['val']:
                return False
        return True

    def check2(self, agent_id: int, transition_candidates: List[LocalTransition], coalition: List[int]) -> bool:
        if agent_id in coalition:
            return False

        for transition in transition_candidates:
            for prop in transition.props:
                if prop in self._reduction:
                    return False
            # if len(transition.props) > 0:
            #     return False

        return True

    def shared_available_transitions(self, agent_id: int, states: List[int]) -> List[LocalTransition]:
        shared_transitions = self._local_models[agent_id].shared_transitions_from_state(states[agent_id])
        result = []
        for transition in shared_transitions:
            ok = True
            for agent2_id in range(0, len(self._local_models)):
                if agent_id == agent2_id:
                    continue

                if self._local_models[agent2_id].has_action(transition.action):
                    ok = False
                    shared_transitions2 = self._local_models[agent2_id].shared_transitions_from_state(states[agent2_id])
                    for transition2 in shared_transitions2:
                        if transition2.action == transition.action:
                            ok = True
                            break

                if not ok:
                    break

            if not ok:
                continue

            result.append(transition)

        return result

    def compute(self):
        state = {'val': [0 for _ in self._local_models], 'props': {}, 'counters': [0 for _ in self._local_models]}
        self._unique_states.append({'val': [0 for _ in self._local_models], 'props': {}})
        self._states.append(state)
        i = 0
        while i < len(self._states):
            state = self._states[i]
            current_state_id = i
            i += 1
            # print(current_state_id, state)
            # if i % 1000 == 0:
            #     print(i)
            # if state['val'] == [4, 6, 3, 13, 0]:
            #     print(state)
            self.compute_next_for_state(state, current_state_id)
            # private_transitions = []
            # for model_id in range(0, len(self._local_models)):
            #     private_transitions.append(
            #         self._local_models[model_id].private_transitions_from_state(state['val'][model_id]))
            #
            # for model_id in range(0, len(self._local_models)):
            #     for transition in private_transitions[model_id]:
            #         # new_state = self.new_state_after_private_transition(state, transition, model_id)
            #         new_state = {'val': state['val'][:], 'props': {}}
            #         new_state['val'][model_id] = self._local_models[model_id].get_state_id(transition.state_to)
            #         new_state = self.copy_props_to_state(new_state, transition)
            #
            #         new_state_id = self.add_state(new_state)
            #
            #         self.add_transition(current_state_id, new_state_id, transition.action, [model_id])
            #
            # shared_transitions = []
            # for model_id in range(0, len(self._local_models)):
            #     shared_transitions.append(
            #         self._local_models[model_id].shared_transitions_from_state(state['val'][model_id]))
            #
            # for model_id in range(0, len(self._local_models)):
            #     for transition in shared_transitions[model_id]:
            #         actual_transition = [(model_id, transition, model_id)]
            #         ok = True
            #         for model_id2 in range(0, len(self._local_models)):
            #             if model_id2 == model_id:
            #                 continue
            #             if self._local_models[model_id2].has_action(transition.action):
            #                 ok = False
            #                 if model_id2 < model_id:
            #                     break
            #                 for transition2 in shared_transitions[model_id2]:
            #                     if transition2.action == transition.action:
            #                         actual_transition.append((model_id2, transition2, model_id2))
            #                         ok = True
            #                         break
            #             if not ok:
            #                 break
            #
            #         if not ok:
            #             continue
            #
            #         new_state = {'val': state['val'][:], 'props': {}}
            #         agents = []
            #         for act_tran in actual_transition:
            #             new_state['val'][act_tran[0]] = self._local_models[act_tran[0]].get_state_id(
            #                 act_tran[1].state_to)
            #             new_state = self.copy_props_to_state(new_state, act_tran[1])
            #             agents.append(act_tran[2])
            #
            #         new_state_id = self.add_state(new_state)
            #
            #         self.add_transition(current_state_id, new_state_id, transition.action, agents)

    def add_transition(self, state_from: int, state_to: int, action: str, agents: List[int]):
        while len(self._transitions) <= state_from:
            self._transitions.append([])

        self._transitions[state_from].append({'from': state_from, 'to': state_to, 'action': action, 'agents': agents})

    def walk(self):
        print("Simulation start")
        current_state_id = 0
        while True:
            print(f"Current state: {self._states[current_state_id]}")
            print("Transitions:")
            for i in range(0, len(self._transitions[current_state_id])):
                print(f"{i}: {self._transitions[current_state_id][i]}")

            id = int(input("Select transition: "))
            current_state_id = self._transitions[current_state_id][id]['to']

    def print(self):
        for model in self._local_models:
            model.print()


model = GlobalModel()
# model.parse("train_controller.txt")
# model.parse("voting.txt")
model.parse("selene.txt")
model.print()
# model.compute()
coalition = model.agent_name_coalition_to_ids(["Coercer1"])
# coalition = model.agent_name_coalition_to_ids(["Coercer1"])
print(f"Coalition: {coalition}")
# model.compute()
model.compute_reduced(coalition)
print()
print(f"Model has {model.states_count} states.")
print()
model.walk()
