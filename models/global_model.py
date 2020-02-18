from models.local_model import LocalModel
from typing import List
import itertools


class GlobalModel:
    def __init__(self):
        self._local_models: List[LocalModel] = []
        self._states = []
        self._transitions = []

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
                    local_model = LocalModel()
                    local_model.parse("".join(lines[line_from:line_to]), agent_id)
                    self._local_models.append(local_model)

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

                    self.add_transition(current_state_id, new_state_id, transition.action)

            shared_transitions = []
            for model_id in range(0, len(self._local_models)):
                shared_transitions.append(
                    self._local_models[model_id].shared_transitions_from_state(state['val'][model_id]))

            for model_id in range(0, len(self._local_models)):
                for transition in shared_transitions[model_id]:
                    actual_transition = [(model_id, transition)]
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
                                    actual_transition.append((model_id2, transition2))
                                    ok = True
                                    break
                        if not ok:
                            break

                    if not ok:
                        continue

                    new_state = {'val': state['val'][:], 'props': {}}
                    for act_tran in actual_transition:
                        new_state['val'][act_tran[0]] = self._local_models[act_tran[0]].get_state_id(act_tran[1].state_to)
                        for prop in act_tran[1].props:
                            new_state['props'][prop] = act_tran[1].props[prop]

                    if new_state not in self._states:
                        self._states.append(new_state)
                        new_state_id = len(self._states) - 1
                    else:
                        new_state_id = self._states.index(new_state)

                    self.add_transition(current_state_id, new_state_id, transition.action)

        print(self._states)
        print(self._transitions)

    def add_transition(self, state_from: int, state_to: int, action: str):
        while len(self._transitions) <= state_from:
            self._transitions.append([])

        self._transitions[state_from].append({'from': state_from, 'to': state_to, 'action': action})

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
model.print()
model.compute()
print()
model.walk()
