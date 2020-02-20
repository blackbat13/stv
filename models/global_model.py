from models.local_model import LocalModel
from models.local_transition import LocalTransition
from typing import List
import itertools


class GlobalModel:
    def __init__(self):
        self._local_models: List[LocalModel] = []
        self._states = []
        self._transitions = []
        # self._dependent:List[List[List[LocalTransition]]] = []
        self._dependent: List[List[List[int]]] = []
        self._pre: List[List[List[LocalTransition]]] = []
        self._agents_count: int = 0

    def parse(self, file_name: str):
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()

        i = 0
        while i < len(lines):
            if len(lines[i].strip()) == 0:
                i += 1
                continue

            if lines[i][0:5] == "Agent":
                line_from = i
                i += 1
                while i < len(lines) and len(lines[i].strip()) != 0 and lines[i][0:5] != "Agent":
                    i += 1

                line_to = i
                agent_max = 1
                if len(lines[line_from].split("[")) > 1:
                    agent_max = int(lines[line_from].split("[")[1].split("]")[0])
                for agent_id in range(1, agent_max + 1):
                    local_model = LocalModel(len(self._local_models))
                    local_model.parse("".join(lines[line_from:line_to]), agent_id)
                    self._local_models.append(local_model)
        self._agents_count = len(self._local_models)

    def compute_reduced(self, coalition: List[int]):
        self.compute_dependent_transitions()
        self.compute_pre_transitions()

        self.print_dependent_transitions()

        state = {'val': [0 for _ in self._local_models], 'props': {}, 'counters': [0 for _ in self._local_models]}
        self._states.append(state)
        i = 0
        while i < len(self._states):
            state = self._states[i]
            current_state_id = i
            i += 1

            ok = False
            for agent_id in range(0, len(self._local_models)):
                transition_candidates = self._local_models[agent_id].private_transitions_from_state(
                    state['val'][agent_id])
                transition_candidates.extend(self.shared_available_transitions(agent_id, state['val']))

                if not self.check2(agent_id, transition_candidates, coalition):
                    continue

                current = transition_candidates[:]
                current.extend(self._local_models[agent_id].current_transitions(state['val'][agent_id],
                                                                                state['counters'][agent_id]))

                print("Hello!")
                if not self.check1(agent_id, current, state):
                    continue

                if not self.check3():
                    continue

                ok = True
                for tr in transition_candidates:
                    new_state = {'val': state['val'][:], 'props': {}, 'counters': state['counters'][:]}
                    new_state['val'][agent_id] = self._local_models[agent_id].get_state_id(tr.state_to)
                    agents = []
                    if tr.shared:
                        for agent2_id in range(self._agents_count):
                            if self._local_models[agent2_id].has_action(tr.action):
                                state['counters'][agent2_id] += 1
                                agents.append(agent2_id)
                    else:
                        state['counters'][agent_id] += 1
                        agents.append(agent_id)

                    for prop in tr.props:
                        new_state['props'][prop] = tr.props[prop]

                    new_state_id = self.state_find(new_state)
                    if new_state_id == -1:
                        self._states.append(new_state)
                        new_state_id = len(self._states) - 1

                    self.add_transition(current_state_id, new_state_id, tr.action, agents)

                break

            if not ok:
                private_transitions = []
                for model_id in range(0, len(self._local_models)):
                    private_transitions.append(
                        self._local_models[model_id].private_transitions_from_state(state['val'][model_id]))

                for model_id in range(0, len(self._local_models)):
                    for transition in private_transitions[model_id]:
                        new_state = {'val': state['val'][:], 'props': {}, 'counters': state['counters'][:]}
                        new_state['val'][model_id] = self._local_models[model_id].get_state_id(transition.state_to)
                        new_state['counters'][model_id] += 1
                        for prop in transition.props:
                            new_state['props'][prop] = transition.props[prop]

                        new_state_id = self.state_find(new_state)
                        if new_state_id == -1:
                            self._states.append(new_state)
                            new_state_id = len(self._states) - 1

                        self.add_transition(current_state_id, new_state_id, transition.action, [model_id])

                shared_transitions = []
                for model_id in range(0, len(self._local_models)):
                    shared_transitions.append(
                        self._local_models[model_id].shared_transitions_from_state(state['val'][model_id]))

                for model_id in range(0, len(self._local_models)):
                    for transition in shared_transitions[model_id]:
                        actual_transition = [(model_id, transition, model_id)]
                        ok = True
                        for model_id2 in range(0, len(self._local_models)):
                            if model_id2 == model_id:
                                continue
                            if self._local_models[model_id2].has_action(transition.action):
                                ok = False
                                if model_id2 < model_id:
                                    break
                                for transition2 in shared_transitions[model_id2]:
                                    if transition2.action == transition.action:
                                        actual_transition.append((model_id2, transition2, model_id2))
                                        ok = True
                                        break
                            if not ok:
                                break

                        if not ok:
                            continue

                        new_state = {'val': state['val'][:], 'props': {}, 'counters': state['counters'][:]}
                        agents = []
                        for act_tran in actual_transition:
                            new_state['counters'][act_tran[0]] += 1
                            new_state['val'][act_tran[0]] = self._local_models[act_tran[0]].get_state_id(
                                act_tran[1].state_to)
                            for prop in act_tran[1].props:
                                new_state['props'][prop] = act_tran[1].props[prop]
                            agents.append(act_tran[2])

                        new_state_id = self.state_find(new_state)
                        if new_state_id == -1:
                            self._states.append(new_state)
                            new_state_id = len(self._states) - 1

                        self.add_transition(current_state_id, new_state_id, transition.action, agents)

    def state_find(self, state):
        for i in range(len(self._states)):
            if self._states[i]['val'] == state['val']:
                return i
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
        # for agent_id in range(0, len(self._local_models)):
        #     self._dependent.append([])
        #     agent_transitions = self._local_models[agent_id].get_transitions()
        #     for i in range(0, len(agent_transitions)):
        #         self._dependent[agent_id].append([])
        #         for j in range(0, len(agent_transitions)):
        #             if i == j:
        #                 continue
        #             self._dependent[agent_id][i].append(agent_transitions[j])
        #
        #         if agent_transitions[i].shared:
        #             for agent_id2 in range(0, len(self._local_models)):
        #                 if agent_id == agent_id2:
        #                     continue
        #                 if self._local_models[agent_id2].has_action(agent_transitions[i].action):
        #                     self._dependent[agent_id][i].extend(self._local_models[agent_id2].get_transitions())

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

            # all_dependent = set()
            for tr in transitions:
                if agent2_id in self._dependent[tr.agent_id][tr.id]:
                    return False
                # all_dependent.update(set(self._dependent[tr.agent_id][tr.id]))
            print("Hello2", state)
            # w dependent trzymać tylko id agentów i sprawdzać, czy występuje agent2_id
            # Jeżeli tak, to false

            all_pre = set()
            for tr in current:
                all_pre.update(set(self._pre[tr.agent_id][tr.id]))

            all_transitions = self._local_models[agent_id].get_transitions()
            all_pre.difference_update(set(all_transitions))
            # TODO sprawdzić! pewnie nie jest do końca poprawnie:
            all_pre.intersection_update(self._local_models[agent2_id].get_transitions())

            print("Hello3", all_pre, len(all_pre))

            if len(all_pre) > 0:
                return False

            # (pre[current] - self._local_models[agent_id].get_transitions()) część wspólna z (self._local_models[agent2_id].get_transitions())
            # Jeżeli nie pusta, to false
        return True

    def check3(self):
        # Sprawdzamy, czy tranzycje nie prowadzą do stanu, który mamy na liście jeszcze nie przetworzony
        # TODO
        return True

    def check2(self, agent_id: int, transition_candidates: List[LocalTransition], coalition: List[int]) -> bool:
        if agent_id in coalition:
            return False

        for transition in transition_candidates:
            if len(transition.props) > 0:
                return False

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
        state = {'val': [0 for _ in self._local_models], 'props': {}}
        self._states.append(state)
        i = 0
        while i < len(self._states):
            state = self._states[i]
            current_state_id = i
            i += 1
            private_transitions = []
            for model_id in range(0, len(self._local_models)):
                private_transitions.append(
                    self._local_models[model_id].private_transitions_from_state(state['val'][model_id]))

            for model_id in range(0, len(self._local_models)):
                for transition in private_transitions[model_id]:
                    new_state = {'val': state['val'][:], 'props': {}}
                    new_state['val'][model_id] = self._local_models[model_id].get_state_id(transition.state_to)
                    for prop in transition.props:
                        new_state['props'][prop] = transition.props[prop]

                    if new_state not in self._states:
                        self._states.append(new_state)
                        new_state_id = len(self._states) - 1
                    else:
                        new_state_id = self._states.index(new_state)

                    self.add_transition(current_state_id, new_state_id, transition.action, [model_id])

            shared_transitions = []
            for model_id in range(0, len(self._local_models)):
                shared_transitions.append(
                    self._local_models[model_id].shared_transitions_from_state(state['val'][model_id]))

            for model_id in range(0, len(self._local_models)):
                for transition in shared_transitions[model_id]:
                    actual_transition = [(model_id, transition, model_id)]
                    ok = True
                    for model_id2 in range(0, len(self._local_models)):
                        if model_id2 == model_id:
                            continue
                        if self._local_models[model_id2].has_action(transition.action):
                            ok = False
                            if model_id2 < model_id:
                                break
                            for transition2 in shared_transitions[model_id2]:
                                if transition2.action == transition.action:
                                    actual_transition.append((model_id2, transition2, model_id2))
                                    ok = True
                                    break
                        if not ok:
                            break

                    if not ok:
                        continue

                    new_state = {'val': state['val'][:], 'props': {}}
                    agents = []
                    for act_tran in actual_transition:
                        new_state['val'][act_tran[0]] = self._local_models[act_tran[0]].get_state_id(
                            act_tran[1].state_to)
                        for prop in act_tran[1].props:
                            new_state['props'][prop] = act_tran[1].props[prop]
                        agents.append(act_tran[2])

                    if new_state not in self._states:
                        self._states.append(new_state)
                        new_state_id = len(self._states) - 1
                    else:
                        new_state_id = self._states.index(new_state)

                    self.add_transition(current_state_id, new_state_id, transition.action, agents)

        print(self._states)
        print(self._transitions)

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
model.parse("train_controller.txt")
# model.parse("voting.txt")
model.print()
# model.compute()
model.compute_reduced([2])
print()
model.walk()
