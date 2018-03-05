from tools.number_tools import NumberTools
from tools.array_tools import ArrayTools
from typing import List, Set
import itertools

class ATLIrModel:
    """Class for creating ATL models with perfect information and imperfect recall"""
    number_of_agents: int = 0
    transitions: List[List] = []
    reverse_transitions: List[List] = []
    agents_actions: List[Set] = []
    pre_states: List[Set] = []
    number_of_states: int = 0

    def __init__(self, number_of_agents: int):
        self.number_of_agents = number_of_agents
        self.number_of_states = 0
        self.init_transitions()
        self.init_agent_actions()
        self.init_states()

    def init_transitions(self):
        self.transitions = []
        self.reverse_transitions = []

    def init_agent_actions(self):
        self.agents_actions = ArrayTools.create_array_of_size(self.number_of_agents, set())

    def init_states(self):
        self.pre_states = []

    def add_action(self, agent_number: int, action: str):
        self.agents_actions[agent_number].add(action)

    def enlarge_transitions(self, new_size: int):
        if len(self.transitions) >= new_size:
            return
        diff = new_size - len(self.transitions) + 1
        for _ in range(0, diff):
            self.transitions.append([])
            self.reverse_transitions.append([])
            self.pre_states.append(set())

    def add_transition(self, from_state: int, to_state: int, actions: List[str]):
        self.enlarge_transitions(to_state + 1) # TODO This is slow. Better idea?
        self.number_of_states = NumberTools.max(self.number_of_states, to_state + 1)
        self.transitions[from_state].append({'next_state': to_state, 'actions': actions[:]})
        self.reverse_transitions[to_state].append({'next_state': from_state, 'actions': actions[:]})
        self.pre_states[to_state].add(from_state)

    def minimum_formula_one_agent(self, agent_number: int, winning_states: Set[int]) -> Set[int]:
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = ArrayTools.create_value_array_of_size(self.number_of_states, False)
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_one_agent(agent_number, current_states, is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def basic_formula_one_agent(self, agent_number: int, current_states: Set[int], is_winning_state: List[bool]) -> Set[int]:
        result_states = set()
        pre_image = set()
        for state_number in current_states:
            pre_image.update(self.pre_states[state_number])

        for state_number in pre_image:
            for action in self.agents_actions[agent_number]:
                if self.is_reachable_by_agent(agent_number, state_number, action, is_winning_state):
                    result_states.add(state_number)
                    is_winning_state[state_number] = True

        return result_states

    def is_reachable_by_agent(self, agent_number: int, state_number: int, action: str, is_winning_state: List[bool]):
        result = False
        for transition in self.transitions[state_number]:
            if transition['actions'][agent_number] == action:
                result = True
                if not is_winning_state[transition['next_state']]:
                    return False

        return result

    def minimum_formula_many_agents(self, agent_numbers: List[int], winning_states: Set[int]) -> Set[int]:
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = ArrayTools.create_value_array_of_size(self.number_of_states, False)
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_many_agents(agent_numbers, current_states, is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def basic_formula_many_agents(self, agent_numbers: List[int], current_states: Set[int], is_winning_state: List[bool]) -> Set[int]:
        result_states = set()
        pre_image = set()
        for state_number in current_states:
            pre_image.update(self.pre_states[state_number])

        actions = []
        for agent_number in agent_numbers:
            actions.append(self.agents_actions[agent_number])

        for state_number in pre_image:
            for action in itertools.product(*actions):
                if self.is_reachable_by_agents(agent_numbers, state_number, action, is_winning_state):
                    result_states.add(state_number)
                    is_winning_state[state_number] = True

        return result_states

    def is_reachable_by_agents(self, agent_numbers: List[int], state_number: int, actions: List[str], is_winning_state: List[bool]):
        result = False
        for transition in self.transitions[state_number]:
            is_good_transition = True
            for agent_number, action in zip(agent_numbers, actions):
                if transition['actions'][agent_number] != action:
                    is_good_transition = False
                    break
            if is_good_transition:
                result = True
                if not is_winning_state[transition['next_state']]:
                    return False

        return result

    def minimum_formula_no_agents(self, winning_states: Set[int]) -> Set[int]:
        result_states = set()
        result_states.update(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = ArrayTools.create_value_array_of_size(self.number_of_states, False)
        for state_number in winning_states:
            is_winning_state[state_number] = True

        while True:
            current_states = self.basic_formula_no_agents(current_states, is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def basic_formula_no_agents(self, current_states: Set[int], is_winning_state: List[bool]) -> Set[int]:
        result_states = set()
        pre_image = set()
        for state_number in current_states:
            pre_image.update(self.pre_states[state_number])

        for state_number in pre_image:
            if self.is_reachable_in_model(state_number, is_winning_state):
                result_states.add(state_number)
                is_winning_state[state_number] = True

        return result_states

    def is_reachable_in_model(self, state_number: int, is_winning_state: List[bool]):
        result = False
        for transition in self.transitions[state_number]:
            result = True
            if not is_winning_state[transition['next_state']]:
                return False

        return result

class ATLirModel(ATLIrModel):
    """Class for creating ATL models with imperfect information and imperfect recall"""
    epistemic_class_membership: List[List[int]] = []
    imperfect_information: List[List] = []

    def __init__(self, number_of_agents):
        super().__init__(number_of_agents)
        self.init_epistemic_relation()

    def init_epistemic_relation(self):
        self.epistemic_class_membership = ArrayTools.create_array_of_size(self.number_of_agents, [])
        self.imperfect_information = ArrayTools.create_array_of_size(self.number_of_agents, [])

    def finish_model(self):
        self.epistemic_class_membership = ArrayTools.create_array_of_size(self.number_of_agents, ArrayTools.create_value_array_of_size(self.number_of_states, -1))

    def add_epistemic_class(self, agent_number: int, epistemic_class: Set[int]):
        """Must be called after creating the whole model"""
        self.imperfect_information[agent_number].append(epistemic_class)
        epistemic_class_number = len(self.imperfect_information[agent_number]) - 1
        for state_number in epistemic_class:
            self.epistemic_class_membership[agent_number][state_number] = epistemic_class_number