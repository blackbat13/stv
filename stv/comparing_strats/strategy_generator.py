from stv.models.simple_model import SimpleModel


class StrategyGenerator:
    model = None
    reachable_states = set()

    def __init__(self, model: SimpleModel):
        self.clear_all()
        self.model = model

    def clear_all(self):
        self.model = None
        self.reachable_states = set()

    def create_strategy(self):
        strategy = []
        for state in range(0, self.model.no_states):
            strategy.append([])
            for _ in range(0, self.model._no_agents):
                strategy[state].append(None)

        for state in range(0, self.model.no_states):
            if len(self.model.graph[state]) == 0:
                continue

            if strategy[state][0] is not None:
                continue
            for agent in range(0, self.model._no_agents):
                actions_tr = {'N': 0, 'E': 0, 'W': 0, 'S': 0, 'Wait': 0, 'F': 0}
                visited_tr = {'N': 0, 'E': 0, 'W': 0, 'S': 0, 'Wait': 0, 'F': 0}
                max_tr = 'F'
                max_visited = 0
                for transition in self.model.graph[state]:
                    actions_tr[transition['actions'][agent]] += 1
                    visited_tr[transition['actions'][agent]] += self.count_visited_places_for_state(
                        self.model.states[transition['next_state']])
                    # if actions_tr[transition['actions'][agent]] > actions_tr[max_tr] or (
                    #         actions_tr[transition['actions'][agent]] == actions_tr[max_tr] and transition['actions'][
                    #     agent] != 'Wait'):
                    #     max_tr = transition['actions'][agent]
                    if actions_tr[transition['actions'][agent]] >= actions_tr[max_tr]:
                        if visited_tr[transition['actions'][agent]] >= max_visited:
                            if transition['actions'][agent] != 'Wait' or visited_tr[
                                transition['actions'][agent]] > max_visited:
                                max_visited = visited_tr[transition['actions'][agent]]
                                max_tr = transition['actions'][agent]
                                # print(max_visited)

                strategy[state][agent] = max_tr

            for ep_state in self.model.epistemic_class_for_state(state, 0):
                strategy[ep_state] = strategy[state][:]

        return self.cut_to_reachable(strategy)

    def cut_to_reachable(self, strategy: list) -> list:
        """Removes states from given strategy that are not reachable in it"""
        self.reachable_states = set()
        # self.reachable_states.add(0)
        # self.dfs2(0, strategy)
        self.reachable_states.add(0)
        self.dfs(0, strategy)
        new_strategy = [None for _ in range(len(strategy))]

        for state in self.reachable_states:
            if strategy[state] is not list:
                new_strategy[state] = strategy[state]
            else:
                new_strategy[state] = strategy[state][:]

        self.reachable_states.clear()
        return new_strategy

    def dfs(self, state: int, strategy) -> None:
        for transition in self.model.graph[state]:
            if transition.actions != strategy[state]:
                continue
            next_state = transition.next_state
            if next_state not in self.reachable_states:
                self.reachable_states.add(next_state)
                self.dfs(next_state, strategy)

    def dfs2(self, state: int, strategy) -> None:
        state_stack = [state]
        while len(state_stack) > 0:
            state = state_stack.pop()
            if state in self.reachable_states:
                continue
            self.reachable_states.add(state)
            for transition in self.model.graph[state]:
                if transition.actions != strategy[state]:
                    continue
                next_state = transition.next_state
                if next_state not in self.reachable_states:
                    self.reachable_states.add(next_state)
                    state_stack.append(next_state)

    def print_strategy(self, strategy):
        for state_number in range(0, len(strategy)):
            if len(strategy[state_number]) == 0:
                continue
            print(self.model.states[state_number])
            print(strategy[state_number])
            print()

    @staticmethod
    def count_visited_places_for_state(state: dict) -> int:
        result = 0
        for vis in state["visited"]:
            result += len(vis)

        return result

    @staticmethod
    def count_no_reachable_states(strategy: list, model: SimpleModel = None):
        result = 0
        for i in range(0, len(strategy)):
            if len(strategy[i]) > 0:
                result += 1
                if model is not None:
                    print(i, model.states[i])
        return result

    @staticmethod
    def compare_list(list1: list, list2: list) -> bool:
        for x, y in zip(list1, list2):
            if x != y:
                return False

        return True
