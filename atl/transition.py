from typing import List


class Transition:
    @property
    def next_state(self) -> int:
        return self.__next_state

    @next_state.setter
    def next_state(self, value: int):
        if value < 0:
            raise ValueError("next_state cannot be negative")
        self.__next_state = value

    @property
    def actions(self) -> List[str]:
        return self.__actions

    @actions.setter
    def actions(self, value: List[str]):
        if len(value) == 0:
            raise ValueError("actions cannot be empty")
        self.__actions = value

    def __init__(self, next_state: int, actions: List[str]):
        self.actions = actions[:]
        self.next_state = next_state

    def to_str(self):
        return f"Next state: {self.next_state}; Actions: {self.actions}"
