from typing import List, Tuple
from stv.models.asynchronous.global_state import GlobalState


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

    def __init__(self, state_from: str, state_to: str, action: str, shared: bool, cond: List, props: dict):
        self._id: int = -1
        self._agent_id = -1
        self._action: str = action
        self._shared: bool = shared
        self._state_from: str = state_from
        self._state_to: str = state_to
        self._props: dict = props
        self._conditions: List = cond
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
        for cond in self.conditions:
            if (cond[2] == "==" and ((cond[0] not in state.props) or (state.props[cond[0]] != cond[1]))) or (
                    cond[2] == "!=" and cond[0] in state.props and state.props[cond[0]] == cond[1]):
                return False

        return True

    def print(self):
        """Print transition in readable form."""
        print(f"{self._action}: {self._state_from} -> {self._state_to} [{self._props}]; conditions: {self._conditions}")

    def to_tuple(self) -> Tuple[int, int, int]:
        """Converts transition to tuple."""
        return self._agent_id, self.i, self.j


class SharedTransition(LocalTransition):
    """
    Represents shared transition.
    """

    def __init__(self, local_transition: LocalTransition):
        super().__init__(local_transition.state_from, local_transition.state_to, local_transition.action,
                         True, local_transition.conditions, local_transition.props)
        self._id: int = local_transition.id
        self._agent_id: int = local_transition.agent_id
        self._transition_list: List[local_transition] = [local_transition]
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

    def add_transition(self, local_transition: LocalTransition):
        """
        Adds new local transition to the list.
        :param local_transition: Local transition to add.
        :return: None
        """
        self._transition_list.append(local_transition)

    def to_tuple(self) -> Tuple[int, int, int]:
        """
        Converts transition to tuple.
        :return:
        """
        return self._transition_list[0].to_tuple()
