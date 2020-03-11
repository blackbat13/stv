from typing import List, Dict


class GlobalState:
    def __init__(self, local_states: List[int], props: Dict, counters: List[int], id: int = -1):
        self._id = id
        self._local_states: List[int] = local_states[:]
        self._props: Dict = props.copy()
        self._counters: List[int] = counters[:]

    @classmethod
    def initial_state(cls, agent_count: int):
        return cls([0 for _ in range(agent_count)], {}, [0 for _ in range(agent_count)], 0)

    @classmethod
    def copy_state(cls, state):
        return cls(state.local_states, state.props, state.counters)

    @property
    def local_states(self):
        return self._local_states

    @property
    def props(self):
        return self._props

    @property
    def counters(self):
        return self._counters

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

    def set_counter(self, index: int, value: int):
        return
        self._counters[index] = value

    def increment_counter(self, index: int):
        return
        self._counters[index] += 1

    def equal(self, state):
        return self._local_states == state.local_states and self._props == state.props

    def to_str(self):
        return str(self._local_states) + " " + str(sorted(self._props.items()))

    def print(self):
        print(f"ID: {self._id}, Local States: {self._local_states}, Props: {self._props}, Counters: {self._counters}")
