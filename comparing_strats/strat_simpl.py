from comparing_strats.simple_model import SimpleModel
from comparing_strats.strategy_generator import *
import itertools


class StrategyComparer:
    model = None
    possible_actions = []
    strategy = []

    def __init__(self, model: SimpleModel, possible_actions: list):
        self.clear_all()
        self.model = model
        self.possible_actions = possible_actions

    def clear_all(self):
        self.model = None
        self.possible_actions = []
        self.strategy = []

    def simplify_strategy(self, strategy: list, heuristic):
        """
        Simplifies given strategy in specified model using given heuristic

        Parameters
        ----------
        model: SimpleModel
            model
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
            if not(state in strategy1_result):
                result = -1
                break

        if result == 1:
            if len(strategy2_result) < len(strategy1_result):
                return 1 # strategy2 is better
            else:
                return 2 # strategy 2 is equal to strategy1

        for state in strategy1_result:
            if state not in strategy2_result:
                return -1 # strategies are not comparable

        return 0  # strategy1 is better

    def epistemic_h(self, state: int, strategy1: list, strategy2: list) -> int:
        strategy1_result = self.get_actions_result(state, strategy1)
        strategy2_result = self.get_actions_result(state, strategy2)
        strategy1_epistemic_h = 0
        strategy2_epistemic_h = 0
        for state in strategy1_result:
            strategy1_epistemic_h += len(self.model.epistemic_class_for_state(state, 0))
        for state in strategy2_result:
            strategy2_epistemic_h += len(self.model.epistemic_class_for_state(state, 0))

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