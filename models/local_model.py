from .local_transition import LocalTransition
from typing import List, Dict


class LocalModel:
    def __init__(self):
        self._agent_name: str = ""
        self._states: Dict[str, int] = {}
        self._transitions: List[LocalTransition] = []

    def parse(self, model_str: str, agent_no: int):
        lines = model_str.splitlines()
        self._agent_name = lines[0].split(" ")[1].split("[")[0]
        init_state = lines[1].split(" ")[1]
        self._states[init_state] = 0
        state_num = 1
        for i in range(2, len(lines)):
            line = lines[i]
            line.replace("aID", str(agent_no))
            self._transitions.append(LocalTransition().parse(line))
            state_from = self._transitions[-1].state_from
            state_to = self._transitions[-1].state_to
            if state_from not in self._states:
                self._states[state_from] = state_num
                state_num += 1
            if state_to not in self._states:
                self._states[state_to] = state_num
                state_num += 1
