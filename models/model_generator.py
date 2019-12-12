from models.simple_model import SimpleModel
from typing import List, Dict, Set
from abc import ABC, abstractmethod


class ModelGenerator(ABC):

    def __init__(self, no_agents: int):
        self.model: SimpleModel = SimpleModel(no_agents)
        self.states_dictionary: Dict[hash, int] = {}
        self.state_number: int = 0
        self.epistemic_states_dictionaries: List[Dict[str, Set[int]]] = []
        self.no_agents: int = no_agents
        self._prepare_epistemic_dictionaries()

    @property
    def states(self) -> List[hash]:
        return self.model.states

    @property
    def model(self) -> SimpleModel:
        return self.__model

    @model.setter
    def model(self, value: SimpleModel):
        self.__model = value

    @property
    def states_dictionary(self) -> Dict[hash, int]:
        return self.__states_dictionary

    @states_dictionary.setter
    def states_dictionary(self, value: Dict[hash, int]):
        self.__states_dictionary = value

    @property
    def state_number(self) -> int:
        return self.__state_number

    @state_number.setter
    def state_number(self, value: int):
        self.__state_number = value

    @property
    def epistemic_states_dictionaries(self) -> List[Dict[str, Set[int]]]:
        return self.__epistemic_states_dictionaries

    @epistemic_states_dictionaries.setter
    def epistemic_states_dictionaries(self, value: List[Dict[str, Set[int]]]):
        self.__epistemic_states_dictionaries = value

    @property
    def no_agents(self) -> int:
        return self.__no_agents

    @no_agents.setter
    def no_agents(self, value: int):
        self.__no_agents = value

    def _prepare_epistemic_dictionaries(self):
        self.epistemic_states_dictionaries.clear()
        for _ in range(0, self.no_agents):
            self.epistemic_states_dictionaries.append({})

    def _add_state(self, state: hash) -> int:
        state['props'] = self._get_props_for_state(state)
        new_state_number = self._get_state_number(state)
        for i in range(0, self.no_agents):
            epistemic_state = self._get_epistemic_state(state, i)
            self._add_to_epistemic_dictionary(epistemic_state, new_state_number, i)
        return new_state_number

    @abstractmethod
    def _get_props_for_state(self, state: hash) -> List[str]:
        """
        Compute propositions for the given state
        :param state: State for which propositions should be computed
        """
        pass

    def _get_state_number(self, state: hash) -> int:
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.states_dictionary:
            self.states_dictionary[state_str] = self.state_number
            new_state_number = self.state_number
            self.model.states.append(state)
            self.state_number += 1
        else:
            new_state_number = self.states_dictionary[state_str]

        return new_state_number

    @abstractmethod
    def _get_epistemic_state(self, state: hash, agent_number: int) -> hash:
        pass

    def _add_to_epistemic_dictionary(self, state: hash, new_state_number: int, agent_number: int):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.epistemic_states_dictionaries[agent_number]:
            self.epistemic_states_dictionaries[agent_number][state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionaries[agent_number][state_str].add(new_state_number)

    def _prepare_epistemic_relation(self):
        for i in range(0, self.no_agents):
            for state, epistemic_class in self.epistemic_states_dictionaries[i].items():
                self.model.add_epistemic_class(i, epistemic_class)

    def generate(self):
        self._generate_initial_states()
        self._generate_model()
        self._prepare_epistemic_relation()

    @abstractmethod
    def _generate_initial_states(self):
        pass

    @abstractmethod
    def _generate_model(self):
        pass

    @abstractmethod
    def get_actions(self) -> List[List[str]]:
        pass

    @abstractmethod
    def get_props_list(self) -> List[str]:
        pass

    def get_winning_states(self, prop: str) -> Set[int]:
        result = []
        state_id = -1
        for state in self.states:
            state_id += 1
            if prop in state['props']:
                result.append(state_id)
        return result

