from stv.tools.number_tools import NumberTools
from stv.tools.disjoint_set import DisjointSet
from stv.logics.atl.transition import Transition
from typing import List, Set
import itertools
import copy


class ATLIrModel:
    """Class for creating ATL models with perfect information and imperfect recall"""

    @property
    def number_of_agents(self) -> int:
        return self._number_of_agents

    @number_of_agents.setter
    def number_of_agents(self, value: int):
        if value < 0:
            raise AttributeError
        self._number_of_agents = value

    @property
    def transitions(self) -> List[List[Transition]]:
        return self._transitions

    @transitions.setter
    def transitions(self, value: List[List[Transition]]):
        self._transitions = value

    @property
    def reverse_transitions(self) -> List[List[Transition]]:
        return self._reverse_transitions

    @reverse_transitions.setter
    def reverse_transitions(self, value: List[List[Transition]]):
        self._reverse_transitions = value

    @property
    def agents_actions(self) -> List[Set]:
        return self._agents_actions

    @agents_actions.setter
    def agents_actions(self, value: List[Set]):
        self._agents_actions = value

    @property
    def pre_states(self) -> List[Set]:
        return self._pre_states

    @pre_states.setter
    def pre_states(self, value: List[Set]):
        self._pre_states = value

    @property
    def number_of_states(self) -> int:
        return self._number_of_states

    @number_of_states.setter
    def number_of_states(self, value: int):
        if value < 0:
            raise AttributeError
        self._number_of_states = value

    @property
    def states(self) -> List:
        return self._states

    @states.setter
    def states(self, value: List):
        self._states = value

    @property
    def strategy(self) -> List:
        return self._strategy

    @strategy.setter
    def strategy(self, value: List):
        self._strategy = value

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
        self.agents_actions = [set() for _ in range(self.number_of_agents)]

    def init_states(self):
        self.pre_states = []

    def add_action(self, agent_id: int, action: str):
        self.agents_actions[agent_id].add(action)

    def enlarge_transitions(self, new_size: int):
        if len(self.transitions) >= new_size:
            return

        size_diff = new_size - len(self.transitions) + 1
        self.enlarge_transitions_by(size_diff)

    def enlarge_transitions_by(self, size: int):
        for _ in range(0, size):
            self.transitions.append([])
            self.reverse_transitions.append([])
            self.pre_states.append(set())

    def add_transition(self, from_state: int, to_state: int, actions: List[str]):
        self.enlarge_transitions(max(to_state, from_state) + 1)  # TODO This is slow. Better idea?
        self.number_of_states = NumberTools.max(self.number_of_states, to_state + 1)
        self.transitions[from_state].append(Transition(next_state=to_state, actions=actions))
        self.reverse_transitions[to_state].append(Transition(next_state=from_state, actions=actions))
        self.pre_states[to_state].add(from_state)

    def minimum_formula_one_agent(self, agent_id: int, winning_states: Set[int]) -> Set[int]:
        result_states = self.prepare_result_states(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = self.marked_winning_states(winning_states)
        self.strategy = [None for _ in range(self.number_of_states)]
        while True:
            current_states = self.basic_formula_one_agent(agent_id, current_states, is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def prepare_result_states(self, winning_states: Set[int]) -> Set[int]:
        result_states = set()
        result_states.update(winning_states)
        return result_states

    def marked_winning_states(self, winning_states: Set[int]) -> List[bool]:
        is_winning_state = [False for _ in range(self.number_of_states)]
        for state_id in winning_states:
            is_winning_state[state_id] = True

        return is_winning_state

    def maximum_formula_one_agent(self, agent_id: int, winning_states: Set[int]) -> Set[int]:
        result_states = self.prepare_result_states(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = self.marked_winning_states(winning_states)
        while True:
            current_states = self.basic_formula_one_agent(agent_id, current_states, is_winning_state)
            to_remove = result_states.difference(current_states)
            for state_id in to_remove:
                is_winning_state[state_id] = False
            result_states.difference_update(to_remove)

            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def basic_formula_one_agent(self, agent_id: int, current_states: Set[int], is_winning_state: List[bool]) -> Set[
        int]:
        result_states = set()
        pre_image = self.prepare_pre_image(current_states)

        for state_id in pre_image:
            for action in self.agents_actions[agent_id]:
                if self.is_reachable_by_agent(agent_id, state_id, action, is_winning_state):
                    result_states.add(state_id)
                    is_winning_state[state_id] = True
                    break

        return result_states

    def is_reachable_by_agent(self, agent_id: int, state_id: int, action: str, is_winning_state: List[bool]):
        result = False
        for transition in self.transitions[state_id]:
            if transition.actions[agent_id] == action:
                result = True
                if not is_winning_state[transition.next_state]:
                    return False

        return result

    def minimum_formula_many_agents(self, agent_ids: List[int], winning_states: Set[int]) -> Set[int]:
        result_states = self.prepare_result_states(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = self.marked_winning_states(winning_states)
        self.strategy = [None for _ in range(self.number_of_states)]
        while True:
            current_states = self.basic_formula_many_agents(agent_ids, current_states, is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def maximum_formula_many_agents(self, agent_ids: List[int], winning_states: Set[int]) -> Set[int]:
        result_states = self.prepare_result_states(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = self.marked_winning_states(winning_states)
        self.strategy = [None for _ in range(self.number_of_states)]
        while True:
            current_states = self.basic_formula_many_agents(agent_ids, current_states, is_winning_state)
            to_remove = result_states.difference(current_states)
            for state_id in to_remove:
                is_winning_state[state_id] = False
            result_states.difference_update(to_remove)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def basic_formula_many_agents(self, agent_ids: List[int], current_states: Set[int],
                                  is_winning_state: List[bool]) -> Set[int]:
        result_states = set()
        pre_image = self.prepare_pre_image(current_states)
        actions = self.get_agents_actions(agent_ids)

        for state_id in pre_image:
            for action in itertools.product(*actions):
                if self.is_reachable_by_agents(agent_ids, state_id, action, is_winning_state):
                    self.strategy[state_id] = list(action)
                    result_states.add(state_id)
                    is_winning_state[state_id] = True
                    break

        return result_states

    def prepare_pre_image(self, states: Set[int]) -> Set[int]:
        pre_image = set()
        for state_id in states:
            pre_image = pre_image.union(self.pre_states[state_id])

        return pre_image

    def get_agents_actions(self, agents_ids: List[int]) -> List[Set[str]]:
        actions = []
        for agent_id in agents_ids:
            actions.append(self.agents_actions[agent_id])

        return actions

    def is_reachable_by_agents(self, agent_ids: List[int], state_id: int, actions: List[str],
                               is_winning_state: List[bool]):
        result = False
        for transition in self.transitions[state_id]:
            is_good_transition = True
            for agent_id, action in zip(agent_ids, actions):
                if transition.actions[agent_id] != action:
                    is_good_transition = False
                    break
            if is_good_transition:
                result = True
                if not is_winning_state[transition.next_state]:
                    return False

        return result

    def minimum_formula_no_agents(self, winning_states: Set[int]) -> Set[int]:
        result_states = self.prepare_result_states(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = self.marked_winning_states(winning_states)
        self.strategy = [None for _ in range(self.number_of_states)]
        while True:
            current_states = self.basic_formula_no_agents(current_states, is_winning_state)
            result_states.update(current_states)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def maximum_formula_no_agents(self, winning_states: Set[int]) -> Set[int]:
        result_states = self.prepare_result_states(winning_states)
        result_states_length = len(result_states)
        current_states = winning_states.copy()
        is_winning_state = self.marked_winning_states(winning_states)
        while True:
            current_states = self.basic_formula_no_agents(current_states, is_winning_state)
            to_remove = result_states.difference(current_states)
            for state_id in to_remove:
                is_winning_state[state_id] = False
            result_states.difference_update(to_remove)
            if result_states_length == len(result_states):
                break

            result_states_length = len(result_states)

        return result_states

    def basic_formula_no_agents(self, current_states: Set[int], is_winning_state: List[bool]) -> Set[int]:
        result_states = set()
        pre_image = self.prepare_pre_image(current_states)

        for state_id in pre_image:
            if self.is_reachable_in_model(state_id, is_winning_state):
                result_states.add(state_id)
                is_winning_state[state_id] = True

        return result_states

    def is_reachable_in_model(self, state_id: int, is_winning_state: List[bool]):
        for transition in self.transitions[state_id]:
            if is_winning_state[transition.next_state]:
                return True

        return False

    def print_model(self):
        print("----MODEL START-----")
        for state in self.states:
            print(state)

        print("----MODEL END------")


class ATLirModel(ATLIrModel):
    """Class for creating ATL models with imperfect information and imperfect recall"""

    @property
    def epistemic_class_membership(self) -> List[List[int]]:
        return self._epistemic_class_membership

    @epistemic_class_membership.setter
    def epistemic_class_membership(self, value: List[List[int]]):
        self._epistemic_class_membership = value

    @property
    def imperfect_information(self) -> List[List]:
        return self._imperfect_information

    @imperfect_information.setter
    def imperfect_information(self, value: List[List]):
        self._imperfect_information = value

    @property
    def finish_model_called(self) -> bool:
        return self._finish_model_called

    @finish_model_called.setter
    def finish_model_called(self, value: bool):
        self._finish_model_called = value

    def __init__(self, number_of_agents):
        super().__init__(number_of_agents)
        self.init_epistemic_relation()
        self.finish_model_called = False

    def init_epistemic_relation(self):
        self.imperfect_information = [[] for _ in range(self.number_of_agents)]

    def finish_model(self):
        self.epistemic_class_membership = [[-1 for _ in range(self.number_of_states)] for _ in
                                           range(self.number_of_agents)]

    def add_epistemic_class(self, agent_id: int, epistemic_class: Set[int]):
        """Must be called after creating the whole model"""
        if not self.finish_model_called:
            self.finish_model()
            self.finish_model_called = True
        self.imperfect_information[agent_id].append(epistemic_class)
        epistemic_class_id = len(self.imperfect_information[agent_id]) - 1
        for state_id in epistemic_class:
            self.epistemic_class_membership[agent_id][state_id] = epistemic_class_id

    def basic_formula_one_agent(self, agent_id: int, current_states: Set[int], is_winning_state: List[bool]) -> Set[
        int]:
        result_states = set()
        for state_id in current_states:
            for pre_state in self.pre_states[state_id]:
                if is_winning_state[pre_state]:
                    continue

                for action in self.agents_actions[agent_id]:
                    if self.is_reachable_by_agent(agent_id, pre_state, action, is_winning_state):
                        epistemic_class = self.epistemic_class_for_state_one_agent(pre_state, agent_id)
                        result_states.update(epistemic_class)
                        for epistemic_state_id in epistemic_class:
                            self.strategy[epistemic_state_id] = list(action)
                            is_winning_state[epistemic_state_id] = True
                        break

        return result_states

    def is_reachable_by_agent(self, agent_id: int, state_id: int, action: str, is_winning_state: List[bool]):
        result = False
        epistemic_class = self.epistemic_class_for_state_one_agent(state_id, agent_id)
        for state_id in epistemic_class:
            for transition in self.transitions[state_id]:
                if transition.actions[agent_id] == action:
                    result = True
                    if not is_winning_state[transition.next_state]:
                        return False

        return result

    def basic_formula_many_agents(self, agents_ids: List[int], current_states: Set[int],
                                  is_winning_state: List[bool]) -> Set[int]:
        result_states = set()
        actions = self.get_agents_actions(agents_ids)

        for state_id in current_states:
            for pre_state in self.pre_states[state_id]:
                if is_winning_state[pre_state]:
                    continue

                for action in itertools.product(*actions):
                    res, new_epi = self.is_reachable_by_agents(agents_ids, pre_state, action, is_winning_state)
                    if res:
                        epistemic_class = new_epi # self.epistemic_class_for_state_multiple_agents(pre_state, agents_ids)
                        result_states.update(epistemic_class)
                        for epistemic_state_id in epistemic_class:
                            is_winning_state[epistemic_state_id] = True
                            self.strategy[epistemic_state_id] = list(action)
                        break

        return result_states

    def is_reachable_by_agents(self, agent_ids: List[int], state_id: int, actions: List[str],
                               is_winning_state: List[bool]):
        result = False
        epistemic_class = self.epistemic_class_for_state_multiple_agents(state_id, agent_ids)
        new_epistemic_class = []
        for state_id in epistemic_class:
            is_ok = False
            for transition in self.transitions[state_id]:
                is_good_transition = True
                for agent_id, action in zip(agent_ids, actions):
                    if transition.actions[agent_id] != action:
                        is_good_transition = False
                        break
                if is_good_transition:
                    result = True
                    is_ok = True
            if is_ok:
                new_epistemic_class.append(state_id)

        is_good = [0 for i in range(len(new_epistemic_class))]
        old_sum = sum(is_good)
        while old_sum != len(new_epistemic_class):
            for i in range(len(new_epistemic_class)):
                if is_good[i] == 1:
                    continue
                state_id = new_epistemic_class[i]
                for transition in self.transitions[state_id]:
                    is_good_transition = True
                    for agent_id, action in zip(agent_ids, actions):
                        if transition.actions[agent_id] != action:
                            is_good_transition = False
                            break
                    if is_good_transition:
                        result = True
                        if is_winning_state[transition.next_state]:
                            is_good[i] = 1
                        elif transition.next_state in new_epistemic_class:
                            next_i = new_epistemic_class.index(transition.next_state)
                            is_good[i] = is_good[next_i]
                        else:
                            return False, []
            new_sum = sum(is_good)
            if new_sum == old_sum:
                return False, []

            old_sum = new_sum

        return result, new_epistemic_class

    def epistemic_class_for_state_multiple_agents(self, state_id: int, agents_ids: List[int]) -> Set[int]:
        """Common Knowledge"""
        epistemic_class = set()
        for agent_id in agents_ids:
            epistemic_class.update(self.epistemic_class_for_state_one_agent(state_id, agent_id))

        return epistemic_class

    def epistemic_class_for_state_one_agent(self, state_id: int, agent_id: int) -> Set[int]:
        epistemic_class_id = self.epistemic_class_membership[agent_id][state_id]
        if epistemic_class_id == -1:
            return {state_id}

        epistemic_class = self.imperfect_information[agent_id][epistemic_class_id]
        return epistemic_class


class ATLirModelDisjoint(ATLIrModel):
    """Class for creating ATL models with imperfect information and imperfect recall using disjoint-union structure"""

    @property
    def epistemic_class_membership(self) -> List[List[int]]:
        return self.__epistemic_class_membership

    @epistemic_class_membership.setter
    def epistemic_class_membership(self, value: List[List[int]]):
        self.__epistemic_class_membership = value

    @property
    def epistemic_class_disjoint(self) -> List[DisjointSet]:
        return self.__epistemic_class_disjoint

    @epistemic_class_disjoint.setter
    def epistemic_class_disjoint(self, value: List[DisjointSet]):
        self.__epistemic_class_disjoint = value

    @property
    def imperfect_information(self) -> List[List]:
        return self.__imperfect_information

    @imperfect_information.setter
    def imperfect_information(self, value: List[List]):
        self.__imperfect_information = value

    @property
    def can_go_there(self) -> List[List[dict]]:
        return self.__can_go_there

    @can_go_there.setter
    def can_go_there(self, value: List[List[dict]]):
        self.__can_go_there = value

    @property
    def finish_model_called(self) -> bool:
        return self.__finish_model_called

    @finish_model_called.setter
    def finish_model_called(self, value: bool):
        self.__finish_model_called = value

    def __init__(self, number_of_agents):
        super().__init__(number_of_agents)
        self.init_epistemic_relation()
        self.finish_model_called = False

    def init_epistemic_relation(self):
        self.imperfect_information = [[] for _ in range(self.number_of_agents)]
        self.epistemic_class_disjoint = [DisjointSet(self.number_of_states) for _ in
                                         itertools.repeat(None, self.number_of_agents)]
        self.can_go_there = [[] for _ in range(self.number_of_agents)]

    def finish_model(self):
        self.epistemic_class_membership = [[-1 for _ in range(self.number_of_states)] for _ in
                                           range(self.number_of_agents)]

    def add_epistemic_class(self, agent_id: int, epistemic_class: Set[int]):
        """Must be called after creating the whole model"""
        if not self.finish_model_called:
            self.finish_model()
            self.finish_model_called = True
        self.imperfect_information[agent_id].append(epistemic_class)
        epistemic_class_id = len(self.imperfect_information[agent_id]) - 1
        first_state = next(iter(epistemic_class))
        for state_id in epistemic_class:
            self.epistemic_class_membership[agent_id][state_id] = epistemic_class_id
            self.epistemic_class_disjoint[agent_id].union(first_state, state_id)

    def find_where_can_go(self, epistemic_class, epistemic_class_id, agent_id):
        if len(self.can_go_there[agent_id]) == 0:
            self.can_go_there[agent_id] = [{} for _ in itertools.repeat(None, self.number_of_states)]

        for action in self.agents_actions[agent_id]:
            can_go_temp = set()
            is_first = True
            for state in epistemic_class:
                can_go_state_temp = set()
                for transition in self.transitions[state]:
                    if transition.actions[agent_id] == action:
                        can_go_state_temp.add(transition.next_state)

                if is_first:
                    is_first = False
                    can_go_temp = set(can_go_state_temp)
                else:
                    can_go_temp |= can_go_state_temp

                if len(can_go_state_temp) == 0:
                    can_go_temp = set()
                    break

            self.can_go_there[agent_id][epistemic_class_id][action] = can_go_temp

    def minimum_formula_one_agent(self, agent_id: int, winning_states: Set[int]) -> Set[int]:
        result_states = self.prepare_result_states(winning_states)
        current_states = winning_states.copy()
        self.strategy = [None for _ in range(self.number_of_states)]
        winning_states_disjoint = DisjointSet(0)
        winning_states_disjoint.subsets = copy.deepcopy(self.epistemic_class_disjoint[agent_id].subsets)
        first_winning = winning_states_disjoint.find(iter(next(winning_states)))
        epistemic_class_ids = set()
        for state_id in winning_states:
            epistemic_class_id = self.epistemic_class_membership[agent_id][state_id]
            epistemic_class_ids.add(epistemic_class_id)

        for epistemic_class_id in epistemic_class_ids:
            epistemic_states = self.imperfect_information[agent_id][epistemic_class_id]
            is_ok = True
            for epistemic_state in epistemic_states:
                state_id = epistemic_state
                if epistemic_state not in winning_states:
                    is_ok = False
                    break
            if is_ok:
                winning_states_disjoint.union(first_winning, state_id)

        custom_can_go_there = self.can_go_there[agent_id][:]

        while True:
            current_states, modified = self.basic_formula_one_agent(agent_id, current_states, first_winning,
                                                                    winning_states_disjoint,
                                                                    custom_can_go_there)
            result_states.update(current_states)
            if not modified:
                break

        return result_states

    def basic_formula_one_agent(self, agent_id: int, current_states: Set[int], first_winning_state_id: int,
                                winning_states: DisjointSet, custom_can_go_there: List[dict]) -> (Set[
                                                                                                      int], bool):
        result_states = set()
        first_winning_state_id = winning_states.find(first_winning_state_id)
        pre_image = set()
        actions = self.agents_actions[agent_id]
        for winning_state in current_states:
            for pre_state in self.pre_states[winning_state]:
                pre_image.add(self.epistemic_class_membership[agent_id][pre_state])

        for state_epistemic_class in pre_image:
            state = next(iter(self.imperfect_information[agent_id][state_epistemic_class]))
            state = winning_states.find(state)
            if state == first_winning_state_id:
                continue

            same_states = self.imperfect_information[agent_id][state_epistemic_class]

            for action in actions:
                states_can_go = custom_can_go_there[state_epistemic_class][action]

                if len(states_can_go) == 0:
                    continue

                is_ok = True
                new_states_can_go = set()

                for state_can in states_can_go:
                    new_state_can = winning_states.find(state_can)

                    if first_winning_state_id != new_state_can:
                        is_ok = False

                    new_states_can_go.add(new_state_can)

                custom_can_go_there[state_epistemic_class][action] = new_states_can_go

                if is_ok:
                    result_states.update(same_states)
                    winning_states.union(first_winning_state_id, state)
                    first_winning_state_id = winning_states.find(first_winning_state_id)
                    modified = True
                    break

        return result_states, modified

    def is_reachable_by_agent(self, agent_id: int, state_id: int, action: str, first_winning_state_id: int,
                              winning_states: DisjointSet):
        result = False

        for transition in self.transitions[state_id]:
            if transition.actions[agent_id] == action:
                result = True
                if not winning_states.is_in_union(first_winning_state_id, transition.next_state):
                    return False

        return result

    def epistemic_class_for_state_multiple_agents(self, state_id: int, agents_ids: List[int]) -> Set[int]:
        """Common Knowledge"""
        epistemic_class = set()
        for agent_id in agents_ids:
            epistemic_class.update(self.epistemic_class_for_state_one_agent(state_id, agent_id))

        return epistemic_class

    def epistemic_class_for_state_one_agent(self, state_id: int, agent_id: int) -> Set[int]:
        epistemic_class_id = self.epistemic_class_membership[agent_id][state_id]
        if epistemic_class_id == -1:
            return {state_id}

        epistemic_class = self.imperfect_information[agent_id][epistemic_class_id]
        return epistemic_class
