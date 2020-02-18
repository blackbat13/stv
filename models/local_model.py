from models.local_transition import LocalTransition
from typing import List, Dict, Set


class LocalModel:
    def __init__(self):
        self._agent_name: str = ""
        self._states: Dict[str, int] = {}
        self._transitions: List[List[LocalTransition]] = []
        self._actions: Set[str] = set()

    def parse(self, model_str: str, agent_no: int):
        lines = model_str.splitlines()
        self._agent_name = lines[0].split(" ")[1].split("[")[0] + str(agent_no)
        init_state = lines[1].split(" ")[1]
        self._states[init_state] = 0
        state_num = 1
        for i in range(2, len(lines)):
            line = lines[i]
            line = line.replace("aID", self._agent_name)
            local_transition = LocalTransition()
            local_transition.parse(line)
            self._actions.add(local_transition.action)
            state_from = local_transition.state_from
            state_to = local_transition.state_to
            if state_from not in self._states:
                self._states[state_from] = state_num
                state_num += 1
            if state_to not in self._states:
                self._states[state_to] = state_num
                state_num += 1

            while len(self._transitions) <= self._states[state_from]:
                self._transitions.append([])

            self._transitions[self._states[state_from]].append(local_transition)

    def transitions_from_state(self, state_id: int) -> List[LocalTransition]:
        return self._transitions[state_id]

    def private_transitions_from_state(self, state_id: int) -> List[LocalTransition]:
        return [tr for tr in self._transitions[state_id] if tr.shared is False]

    def shared_transitions_from_state(self, state_id: int) -> List[LocalTransition]:
        return [tr for tr in self._transitions[state_id] if tr.shared is True]

    def has_action(self, action: str) -> bool:
        return action in self._actions

    def get_state_id(self, state_name: str) -> int:
        return self._states[state_name]

    def print(self):
        print(self._agent_name)
        for transition_list in self._transitions:
            for transition in transition_list:
                transition.print()
