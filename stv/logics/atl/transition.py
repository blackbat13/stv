from typing import List


class Transition:
    """
    Class for expressing the transitions in the model
    """

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

    @property
    def time(self) -> int:
        return self.__time

    @time.setter
    def time(self, value: int):
        if value < 0:
            raise ValueError("time cannot be negative")
        self.__time = value

    def __init__(self, next_state: int, actions: List[str], time: int = 1):
        """
        Initializes transition with next state identifier and list of actions
        :param next_state: identifier of the next state
        :param actions: list of actions
        """
        self.actions = actions[:]
        self.next_state = next_state
        self.time = time

    def to_str(self) -> str:
        """
        Creates string representation of the transition
        :return: string representation of the transition
        """
        return f"Next state: {self.next_state}; Actions: {self.actions}; Time: {self.time}"

    def __str__(self) -> str:
        """
        Creates string representation of the transition
        :return: string representation of the transition
        """
        return f"Next state: {self.next_state}; Actions: {self.actions}; Time: {self.time}"