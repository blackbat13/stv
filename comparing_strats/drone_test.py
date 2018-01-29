from comparing_strats.drone_model import *
from comparing_strats.strat_simpl import StrategyComparer
from comparing_strats.strategy_generator import StrategyGenerator


test_data = []
test_data.append([1, [3]])
test_data.append([1, [5]])
test_data.append([1, [8]])
test_data.append([1, [10]])
test_data.append([1, [15]])
test_data.append([2, [2,2]])
test_data.append([2, [5,5]])
test_data.append([2, [8,8]])
test_data.append([3, [2,2,2]])
test_data.append([3, [4,4,4]])
test_data.append([3, [5,5,5]])

for data in test_data:
    no_drones = data[0]
    energies = data[1]
    print(no_drones, energies)
    drone_model = DroneModel(no_drones=no_drones, energies=energies, map=CracowMap(), is_random=False)
    no_states = len(drone_model.states)
    print(f"Model have {no_states} states")
    strategy_generator = StrategyGenerator(drone_model.model)
    strategy = strategy_generator.create_strategy()
    print(strategy)

    strategy_comparer = StrategyComparer(drone_model.model, ['N', 'S', 'W', 'E', 'Wait'])
    strategy2 = strategy_comparer.simplify_strategy(strategy[:], strategy_comparer.control_h)
    print(strategy2)

    reach_basic = strategy_comparer.strategy_statistic_basic_h(strategy, False)
    reach_simpl = strategy_comparer.strategy_statistic_basic_h(strategy2, False)
    print("Number of reachable states for basic strategy:", reach_basic)
    print("Number of reachable states for simplified strategy:", reach_simpl)
    print()

    epist_basic = strategy_comparer.strategy_statistic_epistemic_h(strategy)
    epist_simpl = strategy_comparer.strategy_statistic_epistemic_h(strategy2)
    print("Number of states in epistemic classes for basic strategy:", epist_basic)
    print("Number of states in epistemic classes for simplified strategy:", epist_simpl)
    print()

    contr_basic = strategy_comparer.strategy_statistic_control_h(strategy)
    contr_simp = strategy_comparer.strategy_statistic_control_h(strategy2)
    print("Number of states of losing control for basic strategy:", contr_basic)
    print("Number of states of losing control for simplified strategy:", contr_simp)


    file_basic = open("comp_str_basic_control.txt", "a")
    file_simpl = open("comp_str_simpl_control.txt", "a")

    file_basic.write(f'{no_drones};{energies};{no_states};{reach_basic};{epist_basic};{contr_basic}\n')
    file_simpl.write(f'{no_drones};{energies};{no_states};{reach_simpl};{epist_simpl};{contr_simp}\n')

    file_basic.close()
    file_simpl.close()