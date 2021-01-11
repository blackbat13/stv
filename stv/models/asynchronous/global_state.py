from typing import List, Dict


class GlobalState:
    """
    Represents global state of the model.
    """

    def __init__(self, local_states: List[int], props: Dict, id: int = -1):
        self._id = id
        self._local_states: List[int] = local_states[:]
        self._props: Dict = props.copy()

    @classmethod
    def initial_state(cls, agent_count: int):
        return cls([0 for _ in range(agent_count)], {}, 0)

    @classmethod
    def copy_state(cls, state, persistent: List[str]):
        new_props = {}
        for prop in state.props:
            if prop in persistent:
                new_props[prop] = state.props[prop]
        return cls(state.local_states, new_props)

    @property
    def local_states(self):
        return self._local_states

    @property
    def props(self):
        return self._props

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    def set_local_state(self, index: int, value: int):
        self._local_states[index] = value

    def set_prop(self, key: str, value):
        self._props[key] = value

    def remove_prop(self, key: str):
        if key in self._props:
            self._props.pop(key)

    def equal(self, state):
        return self._local_states == state.local_states and self._props == state.props

    def to_str(self):
        return str(self._local_states) + " " + str(sorted(self._props.items()))

    def print(self):
        print(f"ID: {self._id}, Local States: {self._local_states}, Props: {self._props}")

    def __str__(self):
        return f"ID: {self._id}, Local States: {self._local_states}, Props: {self._props}"

    def to_obj(self):
        return {"Local States": self._local_states, "Propositions": self._props}
