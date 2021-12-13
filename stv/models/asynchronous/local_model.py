from typing import List, Dict, Set
from stv.models.asynchronous.local_transition import LocalTransition
from stv.models.simple_model import SimpleModel


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
                 protocol: List[List[str]], actions: Set[str]):
        self._agent_id = agent_id
        self._agent_name: str = agent_name
        self._states: Dict[str, int] = states
        self._reverse_states: Dict[int, str] = dict()
        for key in self._states:
            self._reverse_states[self._states[key]] = key

        self._transitions: List[List[LocalTransition]] = transitions
        self._actions: Set[str] = actions
        self._protocol: List[List[str]] = protocol
        self._props: List[str] = []
        self._model: SimpleModel = None
        self._compute_props()
        self._apply_protocol()

    @property
    def agent_name(self):
        """Agent name."""
        return self._agent_name

    @property
    def transitions(self):
        """Transitions."""
        return self._transitions

    @property
    def props(self):
        """Proposition variable names"""
        return self._props

    @property
    def actions(self):
        """Set of action names"""
        return self._actions

    def generate(self):
        self._model = SimpleModel(no_agents=1)
        for state_name in self._states:
            self._model.states.append({"id": self._states[state_name], "name": state_name})
        for state_id in range(len(self._transitions)):
            for transition in self._transitions[state_id]:
                self._model.add_transition(from_state_id=state_id, to_state_id=self._states[transition.state_to],
                                           actions=[transition.action])

    def _apply_protocol(self) -> None:
        p: int = 0
        for lst in self._protocol:
            p += 1
            for tr_name in lst:
                for i in range(len(self._transitions)):
                    for j in range(len(self._transitions[i])):
                        if self._transitions[i][j].action == tr_name:
                            self._transitions[i][j].prot_name = f"{self._agent_name}_prot_{p}"

    def _compute_props(self) -> None:
        props_set: Set[str] = set()
        for ls in self._transitions:
            for tr in ls:
                props_set.update(tr.props.keys())
        self._props = list(props_set)
        self._props.sort()

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

    def get_state_name(self, state_id: int) -> str:
        return self._reverse_states[state_id]

    def get_transitions(self) -> List[LocalTransition]:
        result = []
        for transition_list in self._transitions:
            for transition in transition_list:
                result.append(transition)

        result.sort(key=lambda x: x.id)
        return result

    def print(self):
        print(self._agent_name)
        for transition_list in self._transitions:
            for transition in transition_list:
                transition.print()
