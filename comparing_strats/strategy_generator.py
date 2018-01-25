from comparing_strats.simple_model import SimpleModel


class StrategyGenerator:
    model = None
    reachable_states = set()

    def __init__(self, model: SimpleModel):
        self.model = model

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
                actions_tr = {'N': 0, 'E': 0, 'W': 0, 'S': 0, 'Wait': 0}
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
        self.dfs(0)
        new_strategy = []
        for _ in range(0, len(strategy)):
            new_strategy.append([])

        for state in self.reachable_states:
            new_strategy[state] = strategy[state][:]

        self.reachable_states.clear()
        return new_strategy

    def dfs(self, state: int) -> None:
        for transition in self.model.graph[state]:
            next_state = transition['next_state']
            if next_state not in self.reachable_states:
                self.reachable_states.add(next_state)
                self.dfs(next_state)
