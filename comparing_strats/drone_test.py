from comparing_strats.drone_model import DroneModel, CracowMap
from comparing_strats.strat_simpl import StrategyComparer
from comparing_strats.strategy_generator import StrategyGenerator



drone_model = DroneModel(1, [5], CracowMap())
print("Model have", len(drone_model.states), "states")
strategy_generator = StrategyGenerator(drone_model.model)
strategy = strategy_generator.create_strategy()
print(strategy)

strategy_comparer = StrategyComparer(drone_model.model, ['N', 'S', 'W', 'E', 'Wait'])
strategy2 = strategy_comparer.simplify_strategy(strategy[:], None)
print(strategy2)

print(strategy_comparer.strategy_statistic_basic_h(strategy))
print(strategy_comparer.strategy_statistic_basic_h(strategy2))
