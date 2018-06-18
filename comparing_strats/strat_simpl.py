from comparing_strats.simple_model import SimpleModel
from comparing_strats.strategy_generator import *
import itertools
from typing import List, Set


class StrategyComparer:
    model = None
    possible_actions = []
    winning_states = []
    current_heuristic = None
    dfs_visited_states = []

    def __init__(self, model: SimpleModel, possible_actions: list):
        self.clear_all()
        self.model = model
        self.possible_actions = possible_actions

    def clear_all(self):
        self.model = None
        self.possible_actions = []
        self.winning_states = []
        self.current_heuristic = None
        self.dfs_visited_states = []

    def generate_strategy_dfs(self, initial_state: int, winning_states: Set[int], heuristic):
        self.winning_states = winning_states
        winning_strategy = []
        for i in range(0, len(self.model.states)):
            winning_strategy.append(None)
            self.dfs_visited_states.append(False)

        self.current_heuristic = heuristic
        return self.strategy_dfs(current_state=initial_state, winning_strategy=winning_strategy)

    def strategy_dfs(self, current_state: int, winning_strategy: List) -> (bool, List):
        """Recursive DFS algorithm"""
        if current_state in self.winning_states:
            return True, winning_strategy

        if self.dfs_visited_states[current_state]:
            return False, winning_strategy

        self.dfs_visited_states[current_state] = True

        possible_actions = set()
        for transition in self.model.graph[current_state]:
            possible_actions.add(tuple(transition['actions']))

        strategies = list(possible_actions)
        strategies = self.sort_strategies(current_state, strategies)
        epistemic_strategy = self.check_epistemic_strategy(current_state, winning_strategy)
        if epistemic_strategy is not None:
            strategies = [epistemic_strategy]
        for strategy in strategies:
            next_states = self.get_actions_result(current_state, list(strategy))
            result = False
            new_winning_strategy = self.copy_strategy(winning_strategy)
            new_winning_strategy[current_state] = list(strategy)
            for state in next_states:
                (result, next_winning_strategy) = self.strategy_dfs(state, self.copy_strategy(new_winning_strategy))
                if not result:
                    break
                else:
                    self.join_strategies(new_winning_strategy, next_winning_strategy)

            if result:
                winning_strategy = new_winning_strategy
                self.dfs_visited_states[current_state] = False
                return True, winning_strategy

        self.dfs_visited_states[current_state] = False
        return False, winning_strategy

    def check_epistemic_strategy(self, state: int, strategy: List[List]):
        epistemic_class = self.model.epistemic_class_for_state(state, 0)
        for epistemic_state in epistemic_class:
            if strategy[epistemic_state] is not None:
                return strategy[epistemic_state]

        return None

    def sort_strategies(self, state: int, strategies: List) -> List:
        """Bubble sort strategies"""
        strat_groups = []
        strat_chosen = []

        for i in range(0, len(strategies)):
            strat_chosen.append(False)

        for i in range(0, len(strategies)):
            if strat_chosen[i]:
                continue

            strat_groups.append([i])
            strat_chosen[i] = True
            for j in range(i+1, len(strategies)):
                if strat_chosen[j]:
                    continue

                compare_result = self.basic_h(state, strategies[i], strategies[j])
                if compare_result != -1:
                    strat_groups[-1].append(j)
                    strat_chosen[j] = True

        for k in range(0, len(strat_groups)):
            for i in range(1, len(strat_groups[k])):
                for j in range(0, len(strat_groups[k]) - i):
                    # compare_result = self.basic_h(state, strategies[strat_groups[k][j]], strategies[strat_groups[k][j + 1]])
                    compare_result = self.current_heuristic(state, strategies[strat_groups[k][j]],
                                                            strategies[strat_groups[k][j + 1]])
                    if compare_result == 1:
                        tmp = strat_groups[k][j]
                        strat_groups[k][j] = strat_groups[k][j+1]
                        strat_groups[k][j+1] = tmp

        sorted_strat = []
        for k in range(0, len(strat_groups)):
            for i in strat_groups[k]:
                sorted_strat.append(strategies[i][:])

        return sorted_strat

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

                if compare_result == -1:
                    continue

                # Do additional heuristics

                if compare_result == 1 and heuristic is not None:
                    compare_result = heuristic(state, current_strategy, actions)
                elif compare_result == 1 and heuristic is None:
                    compare_result = self.basic_h(state, current_strategy, actions)

                if compare_result != 1:
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
            if transition["actions"][0] == action:
                result.append(transition["next_state"])

        return sorted(result)

    def get_actions_result(self, state: int, actions: list) -> list:
        result = []
        for transition in self.model.graph[state]:
            if transition["actions"] == actions:
                result.append(transition["next_state"])

        return sorted(result)

    def basic_h(self, state: int, strategy1: list, strategy2: list) -> int:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)

        if len(strategy1_result) == 0 or len(strategy2_result) == 0:
            return -1

        result = 1

        for state in strategy2_result:
            if not (state in strategy1_result):
                result = -1
                break

        if result == 1:
            if len(strategy2_result) < len(strategy1_result):
                return 1  # strategy2 is better
            else:
                return 2  # strategy 2 is equal to strategy1

        for state in strategy1_result:
            if state not in strategy2_result:
                return -1  # strategies are not comparable

        return 0  # strategy1 is better

    def epistemic_h(self, state: int, strategy1: list, strategy2: list) -> int:
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
            return 1
        elif strategy2_epistemic_h > strategy1_epistemic_h:
            return 0
        else:
            return 2

    def control_h(self, state: int, strategy1: list, strategy2: list) -> int:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)
        strategy1_control_h = 0
        strategy2_control_h = 0
        for state in strategy1_result:
            strategy1_control_h += len(self.get_actions_result(state, self.strategy[state]))

        for state in strategy2_result:
            strategy2_control_h += len(self.get_actions_result(state, self.strategy[state]))

        if strategy2_control_h < strategy1_control_h:
            return 1
        elif strategy2_control_h > strategy1_control_h:
            return 0
        else:
            return 2

    def visited_states_h(self, state: int, strategy1: list, strategy2: list) -> int:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)
        if len(strategy2_result) < len(strategy1_result):
            return 1
        elif len(strategy2_result) > len(strategy1_result):
            return 0
        else:
            return 2

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
