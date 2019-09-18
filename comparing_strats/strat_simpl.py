from comparing_strats.strategy_generator import *
import itertools
from typing import List, Set
from enum import Enum
from tools.array_tools import ArrayTools


class StrategyComparer:
    class CompareResult(Enum):
        NOT_COMPARABLE = -1
        EQUAL = 0
        FIRST_BETTER = 1
        SECOND_BETTER = 2

    @property
    def model(self) -> SimpleModel:
        return self.__model

    @model.setter
    def model(self, val: SimpleModel):
        self.__model = val

    @property
    def possible_actions(self) -> List:
        return self.__possible_actions

    @possible_actions.setter
    def possible_actions(self, val: List):
        self.__possible_actions = val

    @property
    def winning_states(self) -> List[int]:
        return self.__winning_states

    @winning_states.setter
    def winning_states(self, val: List[int]):
        self.__winning_states = val

    @property
    def current_heuristic(self):
        return self.__current_heuristic

    @current_heuristic.setter
    def current_heuristic(self, val):
        self.__current_heuristic = val

    @property
    def current_coalition(self) -> List[int]:
        return self.__current_coalition

    @current_coalition.setter
    def current_coalition(self, val: List[int]):
        self.__current_coalition = val

    @property
    def dfs_visited_states(self) -> List[bool]:
        return self.__dfs_visited_states

    @dfs_visited_states.setter
    def dfs_visited_states(self, val: List[bool]):
        self.__dfs_visited_states = val

    def __init__(self, model: SimpleModel, possible_actions: list):
        self.set_defaults()
        self.model = model
        self.possible_actions = possible_actions

    def set_defaults(self):
        self.model = None
        self.possible_actions = []
        self.winning_states = []
        self.current_heuristic = None
        self.dfs_visited_states = []

    def domino_dfs(self, initial_state: int, winning_states: Set[int], coalition: List[int], heuristic) -> (
            bool, List):
        self.winning_states = winning_states
        self.dfs_visited_states = []
        winning_strategy = []
        for i in range(0, len(self.model.states)):
            winning_strategy.append(None)
            self.dfs_visited_states.append(False)

        self.current_heuristic = heuristic
        self.current_coalition = coalition
        # TODO precompute perfect information strategy for enemy coalition for formula <<A>>G !p
        return self.strategy_dfs([initial_state], winning_strategy)

    def strategy_dfs(self, epistemic_class: List[int], winning_strategy: List) -> (bool, List):
        """
        Recursive DFS algorithm

        Parameters
        ----------
        epistemic_class: List
            List of states in the epistemic class
        winning_strategy: List
            Currently found strategy
        """
        if self.is_winning(epistemic_class):
            return True, winning_strategy

        if self.is_already_visited(epistemic_class):
            return False, winning_strategy

        if self.already_has_strategy(epistemic_class, winning_strategy):
            return True, winning_strategy

        self.mark_state(epistemic_class[0], visited=True)

        strategies = self.get_strategies(epistemic_class[0], winning_strategy)
        for strategy in strategies:
            new_winning_strategy = self.copy_strategy(winning_strategy)
            new_winning_strategy[epistemic_class[0]] = list(strategy)

            if len(epistemic_class) > 1:
                result = self.dfs_check_epistemic_class(epistemic_class, new_winning_strategy)
            else:
                result = self.dfs_check_single_state(epistemic_class[0], list(strategy), new_winning_strategy)

            if result:
                winning_strategy = new_winning_strategy
                self.mark_state(epistemic_class[0], visited=False)
                return True, winning_strategy

        self.mark_state(epistemic_class[0], visited=False)
        return False, winning_strategy

    def mark_state(self, state: int, visited: bool):
        self.dfs_visited_states[state] = visited

    def already_has_strategy(self, epistemic_class: List[int], winning_strategy: List) -> bool:
        for state in epistemic_class:
            if winning_strategy[state] is None:
                return False
        return True

    def dfs_check_epistemic_class(self, epistemic_class: List[int], winning_strategy: List) -> bool:
        for state in epistemic_class:
            (result, next_winning_strategy) = self.strategy_dfs([state],
                                                                self.copy_strategy(winning_strategy))
            if not result:
                return False
            else:
                self.join_strategies(winning_strategy, next_winning_strategy)

        return True

    def dfs_check_single_state(self, current_state: int, strategy: List, winning_strategy: List) -> bool:
        next_states = self.get_coalition_actions_result(current_state, strategy)
        epistemic_classes = self.group_by_epistemic_classes(next_states)
        for i in range(0, len(epistemic_classes)):
            (result, next_winning_strategy) = self.strategy_dfs(epistemic_classes[i],
                                                                self.copy_strategy(winning_strategy))
            if not result:
                return False
            else:
                self.join_strategies(winning_strategy, next_winning_strategy)

        return True

    def is_winning(self, epistemic_class: List[int]) -> bool:
        for state in epistemic_class:
            if state not in self.winning_states:
                return False

        return True

    def is_already_visited(self, epistemic_class: List[int]) -> bool:
        for state in epistemic_class:
            if self.dfs_visited_states[state]:
                return True

        return False

    def get_strategies(self, current_state, winning_strategy):
        epistemic_strategy = self.check_epistemic_strategy(current_state, winning_strategy)
        if epistemic_strategy is not None:
            return [epistemic_strategy]

        strategies = self.model.get_possible_strategies_for_coalition(current_state, self.current_coalition)
        strategies = self.eliminate_dominated_strategies(current_state, strategies)
        strategies = self.sort_strategies(current_state, strategies)
        return strategies

    def check_epistemic_strategy(self, state: int, strategy: List[List]):
        epistemic_class = self.model.epistemic_class_for_state_and_coalition(state, self.current_coalition)
        for epistemic_state in epistemic_class:
            if strategy[epistemic_state] is not None:
                return strategy[epistemic_state]

        return None

    def eliminate_dominated_strategies(self, state: int, strategies: List) -> List:
        """Eliminates dominated strategies"""
        strat_chosen = []
        remaining_strat = []
        for i in range(0, len(strategies)):
            strat_chosen.append(True)

        for i in range(0, len(strategies)):
            if not strat_chosen[i]:
                continue

            for j in range(i + 1, len(strategies)):
                compare_result = self.basic_h(state, strategies[i], strategies[j])
                if compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.FIRST_BETTER:
                    strat_chosen[j] = False
                elif compare_result == self.CompareResult.SECOND_BETTER:
                    strat_chosen[i] = False
                    break

            if strat_chosen[i]:
                remaining_strat.append(strategies[i])

        return remaining_strat

    def sort_strategies(self, state: int, strategies: List) -> List:
        """Sort strategies using some heuristics"""
        for i in range(0, len(strategies)):
            for j in range(i, len(strategies) - 1):
                compare_result = self.current_heuristic(state, strategies[j], strategies[j + 1])
                if compare_result == self.CompareResult.SECOND_BETTER:
                    strategies[j], strategies[j + 1] = strategies[j + 1], strategies[j]
        return strategies

    def simplify_strategy(self, strategy: list, heuristic):
        """
        Simplifies given strategy in specified model using given heuristic

        Parameters
        ----------
        strategy: [[String]]
            Strategy to simplify in form:
            [state_id] = [Actions for coalition]
        heuristic: function(state, strategy1, strategy2) -> Bool
            Heuristic function for comparing two strategies defined in one state
        """

        self.strategy = strategy
        drone_actions = []
        for _ in range(0, self.model.no_agents):
            drone_actions.append(self.possible_actions[:])

        for state in range(0, self.model.no_states):
            # skip if state is in the epistemic class
            if len(self.model.epistemic_class_for_state(state, 0)) > 1:
                continue

            # skip if strategy not defined for state
            if len(strategy[state]) == 0:
                continue

            current_strategy = strategy[state][:]
            for actions in itertools.product(*drone_actions):
                actions = list(actions)
                if actions == strategy[state]:
                    continue

                # Maybe always compare with basic strategy? Or check for all better?
                # compare_result = self.basic_h(state, current_strategy, actions)
                compare_result = self.basic_h(state, strategy[state], actions)

                if compare_result == self.CompareResult.NOT_COMPARABLE:
                    continue

                # Do additional heuristics

                if compare_result == self.CompareResult.SECOND_BETTER and heuristic is not None:
                    compare_result = heuristic(state, current_strategy, actions)
                elif compare_result == self.CompareResult.SECOND_BETTER and heuristic is None:
                    compare_result = self.basic_h(state, current_strategy, actions)

                if compare_result != self.CompareResult.SECOND_BETTER:
                    continue

                current_strategy = actions[:]

            if current_strategy != strategy[state]:
                self.strategy[state] = current_strategy[:]

        strategy_generator = StrategyGenerator(self.model)
        # return strategy
        return strategy_generator.cut_to_reachable(self.strategy)

    def get_action_result(self, state: int, action: str) -> list:
        result = []
        for transition in self.model.graph[state]:
            if transition.actions[0] == action:
                result.append(transition.next_state)

        return sorted(result)

    def get_actions_result(self, state: int, actions: list) -> list:
        result = []
        for transition in self.model.graph[state]:
            if transition.actions == actions:
                result.append(transition.next_state)

        return sorted(result)

    def get_coalition_actions_result(self, state: int, actions: List[str]) -> list:
        result = []
        for transition in self.model.graph[state]:
            is_ok = True
            i = 0
            for agent_id in self.current_coalition:
                if actions[i] != transition.actions[agent_id]:
                    is_ok = False
                    break

                i += 1

            if is_ok:
                result.append(transition.next_state)

        return sorted(result)

    def group_by_epistemic_classes(self, states: List[int]) -> List[List[int]]:
        new_states = []
        added = ArrayTools.create_value_array_of_size(len(states), False)
        for i in range(0, len(states)):
            if added[i]:
                continue
            state_id = states[i]
            new_states.append([state_id])
            added[i] = True
            epistemic_class = self.model.epistemic_class_for_state_and_coalition(state_id, self.current_coalition)
            for j in range(i + 1, len(states)):
                if not added[j] and states[j] in epistemic_class:
                    new_states[-1].append(states[j])
                    added[j] = True

        return new_states

    def basic_h(self, state: int, strategy1: list, strategy2: list) -> CompareResult:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)

        if len(strategy1_result) == 0 or len(strategy2_result) == 0:
            return self.CompareResult.NOT_COMPARABLE

        result = 1

        for state in strategy2_result:
            if not (state in strategy1_result):
                result = -1
                break

        if result == 1:
            if len(strategy2_result) < len(strategy1_result):
                return self.CompareResult.SECOND_BETTER
            else:
                return self.CompareResult.EQUAL

        for state in strategy1_result:
            if state not in strategy2_result:
                return self.CompareResult.NOT_COMPARABLE

        return self.CompareResult.FIRST_BETTER

    def epistemic_h(self, state: int, strategy1: list, strategy2: list) -> CompareResult:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)
        strategy1_epistemic_h = set()
        strategy2_epistemic_h = set()
        for state in strategy1_result:
            strategy1_epistemic_h.update(self.model.epistemic_class_for_state(state, 0))
        for state in strategy2_result:
            strategy2_epistemic_h.update(self.model.epistemic_class_for_state(state, 0))

        strategy1_epistemic_h = len(strategy1_epistemic_h)
        strategy2_epistemic_h = len(strategy2_epistemic_h)

        if strategy2_epistemic_h < strategy1_epistemic_h:
            return self.CompareResult.SECOND_BETTER
        elif strategy2_epistemic_h > strategy1_epistemic_h:
            return self.CompareResult.FIRST_BETTER
        else:
            return self.CompareResult.EQUAL

    def control_h(self, state: int, strategy1: list, strategy2: list) -> CompareResult:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)
        strategy1_control_h = 0
        strategy2_control_h = 0
        for state in strategy1_result:
            strategy1_control_h += len(self.get_actions_result(state, self.strategy[state]))

        for state in strategy2_result:
            strategy2_control_h += len(self.get_actions_result(state, self.strategy[state]))

        if strategy2_control_h < strategy1_control_h:
            return self.CompareResult.SECOND_BETTER
        elif strategy2_control_h > strategy1_control_h:
            return self.CompareResult.FIRST_BETTER
        else:
            return self.CompareResult.EQUAL

    def visited_states_h(self, state: int, strategy1: list, strategy2: list) -> CompareResult:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)
        if len(strategy2_result) < len(strategy1_result):
            return self.CompareResult.SECOND_BETTER
        elif len(strategy2_result) > len(strategy1_result):
            return self.CompareResult.FIRST_BETTER
        else:
            return self.CompareResult.EQUAL

    def strategy_statistic_basic_h(self, strategy: list, print: bool = False) -> int:
        if print:
            return StrategyGenerator.count_no_reachable_states(strategy, self.model)
        else:
            return StrategyGenerator.count_no_reachable_states(strategy)

    def strategy_statistic_epistemic_h(self, strategy: list) -> int:
        epistemic_states = set()
        for state in range(0, self.model.no_states):
            if len(strategy[state]) > 0:
                epistemic_states.update(self.model.epistemic_class_for_state(state, 0))

        return len(epistemic_states)

    def strategy_statistic_control_h(self, strategy: list) -> int:
        """Return number of states where users lose control, i.e. their action is non deterministic"""
        result = 0
        for state in range(0, self.model.no_states):
            if len(strategy[state]) > 0:
                if len(self.get_action_result(state, strategy[state][0])) > 1:
                    result += 1

        return result

    @staticmethod
    def join_strategies(strategy1: List, strategy2: List):
        for i in range(0, len(strategy1)):
            if strategy1[i] is None and strategy2[i] is not None:
                strategy1[i] = strategy2[i][:]

    @staticmethod
    def copy_strategy(strategy):
        strategy_copy = []
        for i in range(0, len(strategy)):
            if strategy[i] is None:
                strategy_copy.append(None)
            else:
                strategy_copy.append(strategy[i][:])

        return strategy_copy
