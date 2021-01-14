from stv.comparing_strats.strategy_generator import *
from stv.tools.list_tools import ListTools
from typing import List, Set
from enum import Enum
import itertools
import random
import time


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
        self.model = None
        self.possible_actions = []
        self.winning_states = []
        self.current_heuristic = None
        self.dfs_visited_states = []
        self.current_coalition = []
        self.model = model
        self.possible_actions = possible_actions

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

        # if self.is_already_visited(epistemic_class):
        #     print(False)
        #     return False, winning_strategy

        # if self.already_has_strategy(epistemic_class, winning_strategy):
        #     # print(True)
        #     return True, winning_strategy

        self.mark_state(epistemic_class[0], visited=True)

        strategies = self.get_strategies(epistemic_class[0], winning_strategy)
        # print(strategies, epistemic_class)
        for strategy in strategies:
            new_winning_strategy = self.copy_strategy(winning_strategy)
            new_winning_strategy[epistemic_class[0]] = list(strategy)
            # print(new_winning_strategy)
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
            return [tuple(epistemic_strategy)]

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

    def generate_winning_strategy_perfect_information(self, agent_id: int, winning_states: List[int]):
        new_winning_states = set(winning_states)
        comp_states = set()
        new_comp_states = set(winning_states)
        result_strategy = [None for _ in range(self.model.no_states)]
        while comp_states != new_comp_states:
            comp_states = new_comp_states.copy()
            new_comp_states = set()
            pre_states = set()
            for state in comp_states:
                pre_states.update(self.model.pre_image[state])
            for state in pre_states:
                strategies = self.model.get_possible_strategies(state)
                winning_strategies = []
                ok = False
                mx_count = -1
                for strategy in strategies:
                    res, count = self.check_strategy(agent_id, state, strategy[agent_id], list(new_winning_states))
                    if res:
                        winning_strategies.append((strategy[agent_id], count))
                        mx_count = max(count, mx_count)
                        ok = True

                if ok:
                    new_comp_states.add(state)
                    possible_strategies = []
                    for win_str in winning_strategies:
                        if win_str[1] == mx_count:
                            # result_strategy[state] = [win_str[0]]
                            # break
                            possible_strategies.append([win_str[0]])
                    result_strategy[state] = random.choice(possible_strategies)
                    # result_strategy[state] = random.choice(winning_strategies)[0]

            new_winning_states.update(new_comp_states)

        strategy_generator = StrategyGenerator(self.model)
        return strategy_generator.cut_to_reachable(result_strategy)

    def generate_winning_strategy_perfect_information_coalition(self, winning_states: List[int]):
        new_winning_states = set(winning_states)
        comp_states = set()
        new_comp_states = set(winning_states)
        result_strategy = [None for _ in range(self.model.no_states)]
        while comp_states != new_comp_states:
            comp_states = new_comp_states.copy()
            new_comp_states = set()
            pre_states = set()
            for state in comp_states:
                pre_states.update(self.model.pre_image[state])
            for state in pre_states:
                strategies = self.model.get_possible_strategies(state)
                winning_strategies = []
                ok = False
                mx_count = -1
                for strategy in strategies:
                    res, count = self.check_strategy_coalition(state, list(strategy), list(new_winning_states))
                    if res:
                        winning_strategies.append((list(strategy), count))
                        mx_count = max(count, mx_count)
                        ok = True

                if ok:
                    new_comp_states.add(state)
                    possible_strategies = []
                    for win_str in winning_strategies:
                        if win_str[1] == mx_count:
                            # result_strategy[state] = [win_str[0]]
                            # break
                            possible_strategies.append(win_str[0])
                    result_strategy[state] = random.choice(possible_strategies)
                    # result_strategy[state] = random.choice(winning_strategies)[0]

            new_winning_states.update(new_comp_states)

        strategy_generator = StrategyGenerator(self.model)
        return strategy_generator.cut_to_reachable(result_strategy)

    def check_strategy_coalition(self, state_id: int, strategy: List[str], winning_states: List[int]) -> (bool, int):
        result = False
        count = 0
        for transition in self.model.graph[state_id]:
            if transition.actions == strategy:
                result = True
                count += 1
                if transition.next_state not in winning_states:
                    return False, 0
        return result, count

    def check_strategy(self, agent_id: int, state_id: int, action: str, winning_states: List[int]) -> (bool, int):
        result = False
        count = 0
        for transition in self.model.graph[state_id]:
            if transition.actions[agent_id] == action:
                result = True
                count += 1
                if transition.next_state not in winning_states:
                    return False, 0
        return result, count

    def count_epistemic_mismatch(self, agent_id: int, strategy: List[str]) -> int:
        result = 0
        for epistemic_class in self.model.epistemic_classes[agent_id]:
            action = None
            actions = {}
            max_a = -1
            for state in epistemic_class:
                if strategy[state] is not None:
                    if strategy[state][0] in actions:
                        actions[strategy[state][0]] += 1
                    else:
                        actions[strategy[state][0]] = 1
                    if actions[strategy[state][0]] > max_a:
                        max_a = actions[strategy[state][0]]
                        action = strategy[state]
            for state in epistemic_class:
                if strategy[state] is not None:
                    if strategy[state] != action:
                        result += 1
                    # if action is None:
                    #     action = strategy[state]
                    # else:
                    #     result += 1
        return result

    def count_non_control_states(self, agent_id: int, strategy: List[str]) -> int:
        result = 0
        for state_id in range(len(strategy)):
            if strategy[state_id] is None:
                continue
            next_states = 0
            for transition in self.model.graph[state_id]:
                if transition.actions[agent_id] == strategy[state_id][agent_id]:
                    next_states += 1
            if next_states > 1:
                result += 1
        return result

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
            if strategy[state] is None or len(strategy[state]) == 0:
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

    def simplify_strategy_coalition_imperfect_info(self, coalition: List[int], strategy: list, timeout: int):
        self.strategy = strategy
        actions = []
        for _ in range(0, self.model.no_agents):
            actions.append(self.possible_actions[:])

        start = time.process_time()
        old_strategy = strategy[:]
        while True:
            for agent_id in coalition:
                information_sets = self.generate_information_sets(agent_id, strategy)

                for i_set in information_sets:
                    conflicts = 0
                    for i in range(1, len(i_set)):
                        if strategy[i_set[i]] != strategy[i_set[0]]:
                            conflicts += 1

                    current_strategy = strategy[i_set[0]]
                    replace = False
                    good_strategies = []
                    for strat in self.model.get_possible_strategies(i_set[0]):
                        if strat == strategy[i_set[0]]:
                            continue
                        ok = True
                        for state_id in i_set:
                            compare_result = self.basic_h(state_id, current_strategy, list(strat))
                            if not (
                                    compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                                ok = False
                        if not ok:
                            for state_id in i_set:
                                compare_result = self.basic_h(state_id, current_strategy, list(strat))
                                if not (
                                        compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                                    continue
                                new_conflicts = 0
                                for i in range(0, len(i_set)):
                                    if i_set[i] == state_id:
                                        continue
                                    if strategy[i_set[i]] != strategy[state_id]:
                                        new_conflicts += 1
                                if new_conflicts < conflicts:
                                    strategy[state_id] = list(strat)
                                    conflicts = new_conflicts
                            continue
                        current_strategy = list(strat)
                        replace = True
                        conflicts = 0
                        good_strategies.append(current_strategy[:])
                    if replace:
                        for state_id in i_set:
                            strategy[state_id] = current_strategy
                    current_strategy = strategy[i_set[0]]
                    replace = False
                    for strat in good_strategies:
                        if strat == strategy[i_set[0]]:
                            continue
                        ok = True
                        better = False
                        for state_id in i_set:
                            compare_result = self.basic_h(state_id, current_strategy, list(strat))
                            if not (
                                    compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                                ok = False
                            if compare_result == self.CompareResult.SECOND_BETTER:
                                better = True

                        if not ok:
                            continue
                        if better:
                            current_strategy = list(strat)
                            replace = True
                    if replace:
                        for state_id in i_set:
                            strategy[state_id] = current_strategy
                    if len(good_strategies) > 0:
                        continue
                    current_strategy = strategy[i_set[0]]
                    for strat in self.model.get_possible_strategies(i_set[0]):
                        if strat == strategy[i_set[0]]:
                            continue
                        for state_id in i_set:
                            compare_result = self.basic_h(state_id, current_strategy, list(strat))
                            if not (compare_result == self.CompareResult.SECOND_BETTER):
                                continue
                            new_conflicts = 0
                            for i in range(0, len(i_set)):
                                if i_set[i] == state_id:
                                    continue
                                if strategy[i_set[i]] != strategy[state_id]:
                                    new_conflicts += 1
                            if new_conflicts < conflicts:
                                strategy[state_id] = list(strat)
                                conflicts = new_conflicts

            if strategy == old_strategy:
                break

            strategy_generator = StrategyGenerator(self.model)
            strategy = strategy_generator.cut_to_reachable(self.strategy)
            old_strategy = strategy[:]
            end = time.process_time()
            if (end - start) >= timeout:
                break

        self.strategy = strategy[:]
        strategy_generator = StrategyGenerator(self.model)
        return strategy_generator.cut_to_reachable(self.strategy)

    def generate_information_sets(self, agent_id: int, strategy: list):
        information_sets = []
        for state_id in range(0, self.model.no_states):
            epistemic_class = self.model.epistemic_class_for_state(state_id, agent_id)
            next = False
            i_set = []
            for epistemic_state_id in epistemic_class:
                if epistemic_state_id < state_id:
                    next = True

                if not next and strategy[epistemic_state_id] is not None:
                    i_set.append(epistemic_state_id)
            if next or len(i_set) == 0:
                continue

            information_sets.append(i_set[:])
        return information_sets

    def conflicts_in_i_set(self, i_set, strategy) -> int:
        """
        Count number of conflicts in information set for the given strategy
        :param i_set:
        :param strategy:
        :return:
        """
        conflicts = 0
        for i in range(1, len(i_set)):
            if strategy[i_set[i]] != strategy[i_set[0]]:
                conflicts += 1

        return conflicts

    def simplify_strategy_one_agent_imperfect_info_clusters(self, agent_id: int, strategy: list, timeout: int,
                                                            cluster_size: int):
        self.strategy = strategy
        actions = []
        for _ in range(0, self.model.no_agents):
            actions.append(self.possible_actions[:])

        old_strategy = strategy[:]
        information_sets = self.generate_information_sets(agent_id, strategy)
        start = time.process_time()
        while True:
            for i_set_id in range(len(information_sets), cluster_size):
                conflicts = 0
                root_states = []
                current_strategy = []
                given_strategy = []
                for j in range(cluster_size):
                    conflicts += self.conflicts_in_i_set(information_sets[i_set_id + j], strategy)
                    root_states.append(information_sets[i_set_id + j][0])
                    current_strategy.append(strategy[information_sets[i_set_id + j][0]])
                    given_strategy.append(strategy[information_sets[i_set_id + j][0]])

                # current_strategy = strategy[i_set[0]]
                replace = False
                good_strategies = []

                for strat in self.model.get_possible_strategies_for_set(root_states):
                    if strat == given_strategy:
                        continue
                    ok = True

                    strat_result = set()
                    for j in range(cluster_size):
                        for state_id in information_sets[i_set_id + j]:
                            strat_result.update(set(self.get_action_result(state_id, strat[j])))

                    current_strat_result = set()
                    for j in range(cluster_size):
                        for state_id in information_sets[i_set_id + j]:
                            current_strat_result.update(set(self.get_action_result(state_id, current_strategy[j])))

                    comp_res = self.compare_result(current_strat_result, strat_result)
                    if not (
                            comp_res == self.CompareResult.EQUAL or comp_res == self.CompareResult.SECOND_BETTER):
                        ok = False

                for strat in self.model.get_possible_strategies(i_set[0]):
                    if strat == strategy[i_set[0]]:
                        continue
                    ok = True
                    for state_id in i_set:
                        compare_result = self.basic_h(state_id, current_strategy, list(strat))
                        if not (
                                compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                            ok = False
                    if not ok:
                        for state_id in i_set:
                            compare_result = self.basic_h(state_id, current_strategy, list(strat))
                            if not (
                                    compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                                continue
                            new_conflicts = 0
                            for i in range(0, len(i_set)):
                                if i_set[i] == state_id:
                                    continue
                                if strategy[i_set[i]] != strategy[state_id]:
                                    new_conflicts += 1
                            if new_conflicts < conflicts:
                                strategy[state_id] = list(strat)
                                conflicts = new_conflicts
                        continue
                    current_strategy = list(strat)
                    replace = True
                    conflicts = 0
                    good_strategies.append(current_strategy[:])
                if replace:
                    for state_id in i_set:
                        strategy[state_id] = current_strategy
                current_strategy = strategy[i_set[0]]
                replace = False
                for strat in good_strategies:
                    if strat == strategy[i_set[0]]:
                        continue
                    ok = True
                    better = False
                    for state_id in i_set:
                        compare_result = self.basic_h(state_id, current_strategy, list(strat))
                        if not (
                                compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                            ok = False
                        if compare_result == self.CompareResult.SECOND_BETTER:
                            better = True

                    if not ok:
                        continue
                    if better:
                        current_strategy = list(strat)
                        replace = True
                if replace:
                    for state_id in i_set:
                        strategy[state_id] = current_strategy
                if len(good_strategies) > 0:
                    continue
                current_strategy = strategy[i_set[0]]
                for strat in self.model.get_possible_strategies(i_set[0]):
                    if strat == strategy[i_set[0]]:
                        continue
                    for state_id in i_set:
                        compare_result = self.basic_h(state_id, current_strategy, list(strat))
                        if not (compare_result == self.CompareResult.SECOND_BETTER):
                            continue
                        new_conflicts = 0
                        for i in range(0, len(i_set)):
                            if i_set[i] == state_id:
                                continue
                            if strategy[i_set[i]] != strategy[state_id]:
                                new_conflicts += 1
                        if new_conflicts < conflicts:
                            strategy[state_id] = list(strat)
                            conflicts = new_conflicts

            if strategy == old_strategy:
                break

            # print(strategy)
            strategy_generator = StrategyGenerator(self.model)
            strategy = strategy_generator.cut_to_reachable(self.strategy)
            old_strategy = strategy[:]
            # print(strategy)
            end = time.process_time()
            if (end - start) >= timeout:
                break

        self.strategy = strategy[:]
        strategy_generator = StrategyGenerator(self.model)
        return strategy_generator.cut_to_reachable(self.strategy)

    def simplify_strategy_one_agent_imperfect_info(self, agent_id: int, strategy: list, timeout: int):
        self.strategy = strategy
        actions = []
        for _ in range(0, self.model._no_agents):
            actions.append(self.possible_actions[:])

        old_strategy = strategy[:]
        information_sets = self.generate_information_sets(agent_id, strategy)
        start = time.process_time()
        while True:
            for i_set in information_sets:
                conflicts = 0
                for i in range(1, len(i_set)):
                    if strategy[i_set[i]] != strategy[i_set[0]]:
                        conflicts += 1

                current_strategy = strategy[i_set[0]]
                replace = False
                good_strategies = []
                for strat in self.model.get_possible_strategies(i_set[0]):
                    if strat == strategy[i_set[0]]:
                        continue
                    ok = True
                    for state_id in i_set:
                        compare_result = self.basic_h(state_id, current_strategy, list(strat))
                        if not (
                                compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                            ok = False
                    if not ok:
                        for state_id in i_set:
                            compare_result = self.basic_h(state_id, current_strategy, list(strat))
                            if not (
                                    compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                                continue
                            new_conflicts = 0
                            for i in range(0, len(i_set)):
                                if i_set[i] == state_id:
                                    continue
                                if strategy[i_set[i]] != strategy[state_id]:
                                    new_conflicts += 1
                            if new_conflicts < conflicts:
                                strategy[state_id] = list(strat)
                                conflicts = new_conflicts
                        continue
                    current_strategy = list(strat)
                    replace = True
                    conflicts = 0
                    good_strategies.append(current_strategy[:])
                if replace:
                    for state_id in i_set:
                        strategy[state_id] = current_strategy
                current_strategy = strategy[i_set[0]]
                replace = False
                for strat in good_strategies:
                    if strat == strategy[i_set[0]]:
                        continue
                    ok = True
                    better = False
                    for state_id in i_set:
                        compare_result = self.basic_h(state_id, current_strategy, list(strat))
                        if not (
                                compare_result == self.CompareResult.EQUAL or compare_result == self.CompareResult.SECOND_BETTER):
                            ok = False
                        if compare_result == self.CompareResult.SECOND_BETTER:
                            better = True

                    if not ok:
                        continue
                    if better:
                        current_strategy = list(strat)
                        replace = True
                if replace:
                    for state_id in i_set:
                        strategy[state_id] = current_strategy
                if len(good_strategies) > 0:
                    continue
                current_strategy = strategy[i_set[0]]
                for strat in self.model.get_possible_strategies(i_set[0]):
                    if strat == strategy[i_set[0]]:
                        continue
                    for state_id in i_set:
                        compare_result = self.basic_h(state_id, current_strategy, list(strat))
                        if not (compare_result == self.CompareResult.SECOND_BETTER):
                            continue
                        new_conflicts = 0
                        for i in range(0, len(i_set)):
                            if i_set[i] == state_id:
                                continue
                            if strategy[i_set[i]] != strategy[state_id]:
                                new_conflicts += 1
                        if new_conflicts < conflicts:
                            strategy[state_id] = list(strat)
                            conflicts = new_conflicts

            if strategy == old_strategy:
                break

            # print(strategy)
            strategy_generator = StrategyGenerator(self.model)
            strategy = strategy_generator.cut_to_reachable(self.strategy)
            old_strategy = strategy[:]
            # print(strategy)
            end = time.process_time()
            if (end - start) >= timeout:
                break

        self.strategy = strategy[:]
        strategy_generator = StrategyGenerator(self.model)
        return strategy_generator.cut_to_reachable(self.strategy)

    def simplify_strategy_one_agent(self, agent_id: int, strategy: list, heuristic):
        self.strategy = strategy
        actions = []
        for _ in range(0, self.model._no_agents):
            actions.append(self.possible_actions[:])

        for state in range(0, self.model.no_states):
            # skip if strategy not defined for state
            if strategy[state] is None:
                continue

            current_strategy = strategy[state]
            for strat in self.model.get_possible_strategies(state):
                if strat == strategy[state]:
                    continue

                compare_result = self.basic_h(state, strategy[state], list(strat))

                if compare_result == self.CompareResult.NOT_COMPARABLE:
                    continue

                # Do additional heuristics

                if compare_result == self.CompareResult.SECOND_BETTER and heuristic is not None:
                    compare_result = heuristic(state, current_strategy, strat)
                elif compare_result == self.CompareResult.SECOND_BETTER and heuristic is None:
                    compare_result = self.basic_h(state, current_strategy, list(strat))

                if compare_result != self.CompareResult.SECOND_BETTER:
                    continue

                current_strategy = list(strat)

            if current_strategy != strategy[state]:
                self.strategy[state] = current_strategy

        strategy_generator = StrategyGenerator(self.model)
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
        dif_act = set()
        for transition in self.model.graph[state]:
            for agent_id in self.current_coalition:
                dif_act.add(transition.actions[agent_id])

        for transition in self.model.graph[state]:
            is_ok = True
            i = 0
            for agent_id in self.current_coalition:
                # print(actions[i], transition.actions[agent_id])
                if actions[i] != transition.actions[agent_id]:
                    is_ok = False
                    break

                i += 1

            if is_ok:
                result.append(transition.next_state)

        # print(actions, result)
        return sorted(result)

    def group_by_epistemic_classes(self, states: List[int]) -> List[List[int]]:
        new_states = []
        added = [False for _ in range(len(states))]
        for i, state_id in enumerate(states):
            if added[i]:
                continue
            new_states.append([state_id])
            added[i] = True
            epistemic_class = self.model.epistemic_class_for_state_and_coalition(state_id, self.current_coalition)
            for j in range(i + 1, len(states)):
                if not added[j] and states[j] in epistemic_class:
                    new_states[-1].append(states[j])
                    added[j] = True

        return new_states

    def compare_result(self, result1: Set[int], result2: Set[int]) -> CompareResult:
        if len(result1) == 0 or len(result2) == 0:
            return self.CompareResult.NOT_COMPARABLE

        result = 1

        for state in result2:
            if not (state in result1):
                result = -1
                break

        if result == 1:
            if len(result2) < len(result1):
                return self.CompareResult.SECOND_BETTER
            else:
                return self.CompareResult.EQUAL

        for state in result1:
            if state not in result2:
                return self.CompareResult.NOT_COMPARABLE

        return self.CompareResult.FIRST_BETTER

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

    def basic_h2(self, state: int, strategy1: list, strategy2: list) -> CompareResult:
        strategy1_result = set(self.get_action_result(state, strategy1[0]))
        strategy2_result = set(self.get_action_result(state, strategy2[0]))

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
