from typing import List, Dict, Set
from stv.models.asynchronous.local_transition import LocalTransition


class LocalModel:
    """
    Represents local model of the agent.

    :ivar _agent_id: Agent identifier.
    :ivar _agent_name: Agent name.
    :ivar _states: Dictionary of states, assigns unique identifier to each state name.
    :ivar _transition: List of local transitions in a form of a graph.
    :ivar _actions: Set of agent actions.
    :ivar _protocols:
    """

    def __init__(self, agent_id: int, agent_name: str, states: Dict[str, int], transitions: List[List[LocalTransition]],
                 protocols: Dict[str, List[List[str]]], actions: Set[str]):
        self._agent_id = agent_id
        self._agent_name: str = agent_name
        self._states: Dict[str, int] = states
        self._transitions: List[List[LocalTransition]] = transitions
        self._actions: Set[str] = actions
        self._protocols: Dict[str, List[List[str]]] = protocols

    @property
    def agent_name(self):
        """Agent name."""
        return self._agent_name

    @property
    def transitions(self):
        """Transitions."""
        return self._transitions

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

    def get_transitions(self) -> List[LocalTransition]:
        result = []
        for transition_list in self._transitions:
            for transition in transition_list:
                result.append(transition)

        result.sort(key=lambda x: x.id)
        return result

    def pre_transitions(self, transition: LocalTransition) -> List[LocalTransition]:
        result = []
        state_from = transition.state_from
        transitions_all = self.get_transitions()
        for tr in transitions_all:
            if tr == transition:
                continue
            if tr.state_to == state_from and tr.state_to != tr.state_from:
                result.append(tr)
        return result

    def find_transition(self, action: str) -> LocalTransition:
        transitions_all = self.get_transitions()
        for tr in transitions_all:
            if tr.action == action:
                return tr

        return None

    def current_transitions(self, current_state_id: int, counter: int) -> List[LocalTransition]:
        self._reachable_states = set()
        self.dfs(0, counter)
        result = set()
        for state_id in self._reachable_states:
            if state_id == current_state_id:
                continue
            for tr in self._transitions[state_id]:
                result.add(tr)

        return list(result)

    def dfs(self, state_id: int, counter: int):
        if counter == 0:
            self._reachable_states.add(state_id)
            return

        for tr in self._transitions[state_id]:
            self.dfs(self._states[tr.state_to], counter - 1)

    def print(self):
        print(self._agent_name)
        for transition_list in self._transitions:
            for transition in transition_list:
                transition.print()
