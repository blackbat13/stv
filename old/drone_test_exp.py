# DEPRECATED

from stv.models.synchronous.drone_model import *
from comparing_strats.strat_simpl import StrategyComparer
from comparing_strats.strategy_generator import StrategyGenerator

for _ in range(0, 1):
    no_drones = 2
    energies = [8,8]
    # print(no_drones, energies)
    drone_model = DroneModel(no_drones=no_drones, energies=energies, map=CracowMap(), is_random=True)
    no_states = len(drone_model.states)
    print(f"Model have {no_states} states")
    strategy_generator = StrategyGenerator(drone_model.model)
    strategy = strategy_generator.create_strategy()
    # print(strategy)

    strategy_comparer = StrategyComparer(drone_model.model, ['N', 'S', 'W', 'E', 'Wait'])
    strategy_none = strategy_comparer.simplify_strategy(strategy[:], None)
    strategy_epistemic = strategy_comparer.simplify_strategy(strategy[:], strategy_comparer.epistemic_h)
    strategy_control = strategy_comparer.simplify_strategy(strategy[:], strategy_comparer.control_h)
    # print(strategy_none)

    reach_basic = strategy_comparer.strategy_statistic_basic_h(strategy, False)
    reach_simpl_none = strategy_comparer.strategy_statistic_basic_h(strategy_none, False)
    reach_simpl_epistemic = strategy_comparer.strategy_statistic_basic_h(strategy_epistemic, False)
    reach_simpl_control = strategy_comparer.strategy_statistic_basic_h(strategy_control, False)
    # print("Number of reachable states for basic strategy:", reach_basic)
    # print("Number of reachable states for simplified strategy:", reach_simpl_none)
    # print()

    epist_basic = strategy_comparer.strategy_statistic_epistemic_h(strategy)
    epist_simpl_none = strategy_comparer.strategy_statistic_epistemic_h(strategy_none)
    epist_simpl_epistemic = strategy_comparer.strategy_statistic_epistemic_h(strategy_epistemic)
    epist_simpl_control = strategy_comparer.strategy_statistic_epistemic_h(strategy_control)
    # print("Number of states in epistemic classes for basic strategy:", epist_basic)
    # print("Number of states in epistemic classes for simplified strategy:", epist_simpl_none)
    # print()

    contr_basic = strategy_comparer.strategy_statistic_control_h(strategy)
    contr_simp_none = strategy_comparer.strategy_statistic_control_h(strategy_none)
    contr_simp_epistemic = strategy_comparer.strategy_statistic_control_h(strategy_epistemic)
    contr_simp_control = strategy_comparer.strategy_statistic_control_h(strategy_control)
    # print("Number of states of losing control for basic strategy:", contr_basic)
    # print("Number of states of losing control for simplified strategy:", contr_simp_none)


    file_basic = open("comp_str_rnd_2_8_8.txt", "a")

    file_basic.write(f'{reach_basic};{epist_basic};{contr_basic};{reach_simpl_none};{epist_simpl_none};{contr_simp_none};{reach_simpl_epistemic};{epist_simpl_epistemic};{contr_simp_epistemic};{reach_simpl_control};{epist_simpl_control};{contr_simp_control}\n')

    file_basic.close()