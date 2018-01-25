from comparing_strats.simple_model import SimpleModel


class StrategyComparer:
    model = None
    possible_actions = []

    def __init__(self, model: SimpleModel, possible_actions: list):
        self.model = model
        self.possible_actions = possible_actions

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

        for state in range(0, self.model.no_states):
            # skip if state is in the epistemic class
            # skip if strategy not defined for state
            if len(strategy[state]) == 0:
                continue

            current_strategy = strategy[state][:]
            for action in self.possible_actions:
                if action == strategy[state][0]:
                    continue

                # Maybe always compare with basic strategy? Or check for all better?
                compare_result = self.basic_h(state, current_strategy, [action])
                if compare_result == -1:
                    continue

                # Do additional heuristics

                if compare_result != 1:
                    continue

                current_strategy = [action]

            if current_strategy != strategy[state]:
                strategy[state] = current_strategy

        return strategy

    def get_action_result(self, state: int, action: str) -> list:
        result = []
        for transition in self.model.graph[state]:
            if transition["actions"][0] == action:
                result.append(transition["next_state"])

        return sorted(result)

    def basic_h(self, state: int, strategy1: list, strategy2: list) -> int:
        strategy1_result = self.get_action_result(state, strategy1[0])
        strategy2_result = self.get_action_result(state, strategy2[0])

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

        return 0 # strategy1 is better

    def strategy_statistic_basic_h(self, strategy: list) -> int:
        no_result_states = 0
        for state in range(0, self.model.no_states):
            no_result_states += len(self.get_action_result(state, strategy[state][0]))

        return no_result_states
