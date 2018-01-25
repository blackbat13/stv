from comparing_strats.drone_model import DroneModel, CracowMap
from comparing_strats.strat_simpl import StrategyComparer


def create_strategy(model):
    strategy = []
    for state in range(0, model.no_states):
        strategy.append([])
        if len(model.graph[state]) == 0:
            continue

        for agent in range(0, model.no_agents):
            actions_tr = {'N': 0, 'E': 0, 'W': 0, 'S': 0, 'Wait': 0}
            max_tr = 'N'
            for transition in model.graph[state]:
                actions_tr[transition['actions'][agent]] += 1
                if actions_tr[transition['actions'][agent]] > actions_tr[max_tr] or (
                        actions_tr[transition['actions'][agent]] == actions_tr[max_tr] and transition['actions'][
                    agent] != 'Wait'):
                    max_tr = transition['actions'][agent]

            strategy[state].append(max_tr)

    return strategy


drone_model = DroneModel(1, [5], CracowMap())
print("Model have", len(drone_model.states), "states")
strategy = create_strategy(drone_model.model)
print(strategy)

strategy_comparer = StrategyComparer(drone_model.model, ['N', 'S', 'W', 'E', 'Wait'])
strategy2 = strategy_comparer.simplify_strategy(strategy[:], None)
print(strategy2)

print(strategy_comparer.strategy_statistic_basic_h(strategy))
print(strategy_comparer.strategy_statistic_basic_h(strategy2))
