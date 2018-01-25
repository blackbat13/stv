from comparing_strats.drone_model import *
from comparing_strats.strat_simpl import StrategyComparer
from comparing_strats.strategy_generator import StrategyGenerator


drone_model = DroneModel(no_drones=1, energies=[5], map=CracowMap(), is_random=False)
print("Model have", len(drone_model.states), "states")
strategy_generator = StrategyGenerator(drone_model.model)
strategy = strategy_generator.create_strategy()
print(strategy)

strategy_comparer = StrategyComparer(drone_model.model, ['N', 'S', 'W', 'E', 'Wait'])
strategy2 = strategy_comparer.simplify_strategy(strategy[:], strategy_comparer.epistemic_h)
print(strategy2)

print("Number of reachable states for basic strategy:", strategy_comparer.strategy_statistic_basic_h(strategy))
print("Number of reachable states for simplified strategy:", strategy_comparer.strategy_statistic_basic_h(strategy2))
print()
print("Number of states in epistemic classes for basic strategy:", strategy_comparer.strategy_statistic_epistemic_h(strategy))
print("Number of states in epistemic classes for simplified strategy:", strategy_comparer.strategy_statistic_epistemic_h(strategy2))
print()
print("Number of states of losing control for basic strategy:", strategy_comparer.strategy_statistic_control_h(strategy))
print("Number of states of losing control for simplified strategy:", strategy_comparer.strategy_statistic_control_h(strategy2))
