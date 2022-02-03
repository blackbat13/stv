from typing import List, Tuple, Set
from stv.models.asynchronous.global_state import GlobalState
import re


class LocalTransition:
    """
    Class representing local transition.

    :ivar _id: Transition identifier.
    :ivar _agent_id: Agent identifier.
    :ivar _action: Action string.
    :ivar _shared: True if transition is a shared transition, false otherwise.
    :ivar _state_from:
    :ivar _state_to:
    :ivar _props:
    :ivar _conditions:
    :ivar i:
    :ivar j:
    """

    def __init__(self, state_from: str, state_to: str, action: str, shared: bool, cond: List, props: dict, cond_str: str):
        self._id: int = -1
        self._agent_id = -1
        self._action: str = action
        self._shared: bool = shared
        self._state_from: str = state_from
        self._state_to: str = state_to
        self._props: dict = props
        self._conditions: List = cond
        self._conditions_str: str = cond_str
        self.i: int = -1
        self.j: int = -1
        self._prot_name: str = action

    def __eq__(self, other) -> bool:
        if isinstance(other, LocalTransition):
            return self._agent_id == other._agent_id and self._action == other._action
        return False

    @property
    def prot_name(self) -> str:
        """Action name according to protocol"""
        return self._prot_name

    @prot_name.setter
    def prot_name(self, val: str):
        self._prot_name = val

    @property
    def conditions(self) -> List:
        """List of conditions."""
        return self._conditions

    @property
    def id(self) -> int:
        """Identifier of the transition."""
        return self._id

    @id.setter
    def id(self, val: int):
        self._id = val

    @property
    def agent_id(self) -> int:
        """Agent identifier."""
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
        """Dictionary of propositions modified by this transition."""
        return self._props

    @property
    def action(self) -> str:
        """Agent action assigned to this transition."""
        return self._action

    @action.setter
    def action(self, val: str):
        self._action = val

    @property
    def shared(self) -> bool:
        """True if transition is a shared transition, False otherwise."""
        return self._shared

    def check_conditions(self, state: GlobalState) -> bool:
        """
        Checks if transition conditions are met in a given state.
        :param state: Global state.
        :return: True if conditions are met, False otherwise.
        """
        if self._conditions_str == "":
            return True
        # print(self._conditions_str, state.props, eval(self._conditions_str, {}, state.props))
        return eval(self._conditions_str, {}, state.props)

    def print(self):
        """Print transition in readable form."""
        print(f"{self._action}: {self._state_from} -> {self._state_to} [{self._props}]; conditions: {self._conditions}")

    def to_tuple(self) -> Tuple[int, int, int]:
        """Converts transition to tuple."""
        return self._agent_id, self.i, self.j

    def remove_props(self, save: Set[str]):
        for key in list(self._props.keys()):
            if key not in save:
                self._props.pop(key)

        for cond in self._conditions[:]:
            if cond[0] not in save:
                self._conditions.remove(cond)

    def _conditions_to_str(self):
        result = ""
        for cond in self._conditions:
            result += f"{cond[0]}{cond[2]}{cond[1]} and "

        result = result[0:-5]
        return result

    def __str__(self):
        conditions = f"[{self._conditions_to_str()}]"
        if self._conditions_to_str() == "":
            conditions = ""

        values = f"[{', '.join([f'{key}={self._props[key][1]}' for key in self._props])}]"
        if not self._props:
            values = ""

        return f"{self._action}: {self._state_from} -{conditions}> {self._state_to} {values}"


class SharedTransition(LocalTransition):
    """
    Represents shared transition.
    """

    def __init__(self, local_transition: LocalTransition):
        super().__init__(local_transition.state_from, local_transition.state_to, local_transition.action,
                         True, local_transition.conditions, local_transition.props, local_transition._conditions_str)
        self._id: int = local_transition.id
        self._agent_id: int = local_transition.agent_id
        self._transition_list: List[local_transition] = [local_transition]
        self._agents_list: List[int] = [self._agent_id]
        self.i: int = local_transition.i
        self.j: int = local_transition.j
        self._prot_name: str = local_transition.prot_name

    def __eq__(self, other) -> bool:
        if isinstance(other, SharedTransition):
            return self._transition_list == other._transition_list
        return False

    @property
    def transition_list(self) -> List[LocalTransition]:
        """List of local transitions."""
        return self._transition_list

    @property
    def agents_list(self) -> List[int]:
        """List of agents ids"""
        return self._agents_list

    def add_transition(self, local_transition: LocalTransition):
        """
        Adds new local transition to the list.
        :param local_transition: Local transition to add.
        :return: None
        """
        self._transition_list.append(local_transition)
        self._agents_list.append(local_transition.agent_id)
        self._agents_list.sort()

    def to_tuple(self) -> Tuple[int, int, int]:
        """
        Converts transition to tuple.
        :return:
        """
        return self._transition_list[0].to_tuple()
