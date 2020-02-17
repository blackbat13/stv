from typing import Dict


class LocalTransition:
    def __init__(self):
        self._action: str = ""
        self._shared: bool = False
        self._state_from: str = ""
        self._state_to: str = ""
        self._props: Dict[str, bool] = {}

    @property
    def state_from(self):
        return self._state_from

    @property
    def state_to(self):
        return self._state_to

    def parse(self, transition_str: str):
        if transition_str[0:6] == "shared":
            self._shared = True
            transition_str = transition_str[7:]

        self._action, transition_str = transition_str.split(":")
        self._state_from, transition_str = transition_str.split("->")
        self._state_to, transition_str = transition_str.split("[")

        self._state_from = self._state_from.strip()
        self._state_to = self._state_to.strip()

        transition_str = transition_str.split("]")[0]
        variables = transition_str.split(",")
        for variable in variables:
            prop, val = variable.split("=")
            if val.casefold() == "true":
                val = True
            else:
                val = False
            self._props[prop] = val
