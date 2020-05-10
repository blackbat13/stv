from stv.models.simple_model import SimpleModel
from abc import ABC, abstractmethod
from typing import List, Dict, Set


class ModelGenerator(ABC):
    """
    Abstract class for defining new model classes.

    :param agents_count: number of agents in the model.

    :ivar _model: SimpleModel object, used for storing generated model.
    :ivar _states_dictionary:
    :ivar _state_number:
    :ivar _epistemic_states_dictionaries:
    :ivar _agents_count:
    """

    def __init__(self, agents_count: int):
        self._model: SimpleModel = SimpleModel(agents_count)
        self._states_dictionary: Dict[hash, int] = {}
        self._state_number: int = 0
        self._agents_count: int = agents_count
        self._epistemic_states_dictionaries: List[Dict[str, Set[int]]] = [{} for _ in range(self._agents_count)]

    @property
    def states(self) -> List[hash]:
        """List of states in the model."""
        return self.model.states

    @property
    def model(self) -> SimpleModel:
        """Model object."""
        return self._model

    @model.setter
    def model(self, value: SimpleModel):
        self._model = value

    @property
    def agents_count(self) -> int:
        """Number of agents in the model."""
        return self._agents_count

    @agents_count.setter
    def agents_count(self, value: int):
        self._agents_count = value

    def _add_state(self, state: hash) -> int:
        """
        Adds new state to the model, if not already added.
        :param state: New state to add to the model.
        :return: Id of the passed state.
        """
        state['props'] = self._get_props_for_state(state)
        new_state_id = self._get_state_id(state)
        for i in range(0, self.agents_count):
            epistemic_state = self._get_epistemic_state(state, i)
            self._add_to_epistemic_dictionary(epistemic_state, new_state_id, i)
        return new_state_id

    @abstractmethod
    def _get_props_for_state(self, state: hash) -> List[str]:
        """
        Compute propositions for the given state.
        :param state: State for which propositions should be computed.
        :return: List of propositions for the given state.
        """

    def _get_state_id(self, state: hash) -> int:
        """
        Gets state id if already present, or adds it to the model and returns its new id.
        :param state: State.
        :return: Id of the given state.
        """
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self._states_dictionary:
            self._states_dictionary[state_str] = self._state_number
            new_state_number = self._state_number
            self.model.states.append(state)
            self._state_number += 1
        else:
            new_state_number = self._states_dictionary[state_str]

        return new_state_number

    @abstractmethod
    def _get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        """
        Compute epistemic representation of the given state.
        :param state: State to compute.
        :param agent_id: Id of the agent for which epistemic representation should be computed.
        :return: Epistemic representation of the given state.
        """

    def _add_to_epistemic_dictionary(self, state: hash, new_state_id: int, agent_id: int):
        """
        Adds state to the epistemic dictionary.
        :param state:
        :param new_state_id:
        :param agent_id:
        :return: None
        """
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self._epistemic_states_dictionaries[agent_id]:
            self._epistemic_states_dictionaries[agent_id][state_str] = {new_state_id}
        else:
            self._epistemic_states_dictionaries[agent_id][state_str].add(new_state_id)

    def _prepare_epistemic_relation(self):
        """
        Prepares epistemic relation for the model.
        Should be called after creating the model.
        :return: None
        """
        for i in range(0, self.agents_count):
            for _, epistemic_class in self._epistemic_states_dictionaries[i].items():
                self.model.add_epistemic_class(i, epistemic_class)

    def generate(self):
        """
        Generate model.
        :return: None
        """
        self._generate_initial_states()
        self._generate_model()
        self._prepare_epistemic_relation()

    @abstractmethod
    def _generate_initial_states(self):
        """Generates initial states of the model."""

    @abstractmethod
    def _generate_model(self):
        """Generates rest of the model."""

    @abstractmethod
    def get_actions(self) -> List[List[str]]:
        """
        Return list of actions in the model.
        :return: List of actions for each agent.
        """

    @abstractmethod
    def get_props_list(self) -> List[str]:
        """
        Returns list of propositions in the model.
        :return: List of propositions in the model.
        """

    def get_winning_states(self, prop: str) -> Set[int]:
        """
        Compute set of winning states for given proposition.
        :param prop: Proposition.
        :return: Set of states identifiers.
        """
        result = set()
        state_id = -1
        for state in self.states:
            state_id += 1
            if prop in state['props']:
                result.add(state_id)
        return result
