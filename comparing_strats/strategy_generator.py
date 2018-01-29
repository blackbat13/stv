from comparing_strats.simple_model import SimpleModel


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
            for _ in range(0, self.model.no_agents):
                strategy[state].append(None)

        for state in range(0, self.model.no_states):
            if len(self.model.graph[state]) == 0:
                continue

            for agent in range(0, self.model.no_agents):
                actions_tr = {'N': 0, 'E': 0, 'W': 0, 'S': 0, 'Wait': 0, 'F': 0}
                max_tr = 'N'
                for transition in self.model.graph[state]:
                    actions_tr[transition['actions'][agent]] += 1
                    if actions_tr[transition['actions'][agent]] > actions_tr[max_tr] or (
                            actions_tr[transition['actions'][agent]] == actions_tr[max_tr] and transition['actions'][
                        agent] != 'Wait'):
                        max_tr = transition['actions'][agent]

                strategy[state][agent] = max_tr

        return self.cut_to_reachable(strategy)

    def cut_to_reachable(self, strategy: list) -> list:
        """Removes states from given strategy that are not reachable in it"""
        self.reachable_states = set()
        self.reachable_states.add(0)
        self.dfs(0, strategy)
        print(self.reachable_states)
        new_strategy = []
        for _ in range(0, len(strategy)):
            new_strategy.append([])

        for state in self.reachable_states:
            new_strategy[state] = strategy[state][:]

        self.reachable_states.clear()
        return new_strategy

    def dfs(self, state: int, strategy) -> None:
        for transition in self.model.graph[state]:
            if transition['actions'] != strategy[state]:
                # print(transition['actions'], strategy[state])
                continue
            next_state = transition['next_state']
            if next_state not in self.reachable_states:
                self.reachable_states.add(next_state)
                self.dfs(next_state, strategy)

    @staticmethod
    def count_no_reachable_states(strategy: list, model: SimpleModel = None):
        result = 0
        for i in range(0, len(strategy)):
            if len(strategy[i]) > 0:
                result += 1
                if model != None:
                    print(i, model.states[i])
        return result

    @staticmethod
    def compare_list(list1: list, list2: list) -> bool:
        for x, y in zip(list1, list2):
            if x != y:
                return False

        return True
