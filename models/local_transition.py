from typing import Dict, List


class LocalTransition:
    def __init__(self):
        self._id: int = -1
        self._agent_id = -1
        self._action: str = ""
        self._shared: bool = False
        self._state_from: str = ""
        self._state_to: str = ""
        self._props: dict = {}
        self._cond: List[(str, int)] = []

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, val: int):
        self._id = val

    @property
    def agent_id(self) -> int:
        return self._agent_id

    @agent_id.setter
    def agent_id(self, val: int):
        self._agent_id = val

    @property
    def state_from(self) -> str:
        return self._state_from

    @property
    def state_to(self) -> str:
        return self._state_to

    @property
    def props(self) -> dict:
        return self._props

    @property
    def action(self) -> str:
        return self._action

    @action.setter
    def action(self, val: str):
        self._action = val

    @property
    def shared(self) -> bool:
        return self._shared

    def parse(self, transition_str: str):
        if transition_str[0:6] == "shared":
            self._shared = True
            transition_str = transition_str[7:]

        self._action, transition_str = transition_str.split(":")
        if transition_str.find("->") == -1:
            self._state_from, transition_str = transition_str.split("-[")
            conditions, transition_str = transition_str.split("]>")
            cond_var, cond_val = conditions.split("==")
            self._cond.append((cond_var, int(cond_val)))
        else:
            self._state_from, transition_str = transition_str.split("->")
        if transition_str.find("[") != -1:
            self._state_to, transition_str = transition_str.split("[")
            transition_str = transition_str.split("]")[0]
            variables = transition_str.split(",")
            for variable in variables:
                if variable.find("=") == -1:
                    self._props[variable] = "?"
                    continue
                prop, val = variable.split("=")
                if val.casefold() == "true":
                    val = True
                elif val.casefold() == "false":
                    val = False
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                self._props[prop] = val
        else:
            self._state_to = transition_str

        self._state_from = self._state_from.strip()
        self._state_to = self._state_to.strip()

    def print(self):
        print(f"{self._action}: {self._state_from} -> {self._state_to} [{self._props}]")
