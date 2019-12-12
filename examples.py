# This file contains examples for running desired experiments
# Uncomment desired lines to see how this works


# from experiments.domino_dfs.bridge_dfs_exp import BridgeDfsExp
#
# bridge_dfs_exp = BridgeDfsExp(1, True)
# bridge_dfs_exp.run_experiments()

# from experiments.domino_dfs.castle_dfs_exp import CastleDfsExp
#
# castle_dfs_test = CastleDfsExp(castle_sizes=[1, 1, 1], castle_lifes=[3, 3, 3], DEBUG=False)
# castle_dfs_test.run_experiments()

# from experiments.domino_dfs.drone_dfs_exp import DroneDfsExp
#
# drone_dfs_exp = DroneDfsExp(no_drones=1, energies=[3], DEBUG=True)
# drone_dfs_exp.run_experiments()

# from experiments.approximations.bridge_model_experiments import BridgeModelExperiments
#
# bridge_model_experiments = BridgeModelExperiments(1)
# bridge_model_experiments.run_experiments()

from experiments.approximations.castle_model_experiments import CastleModelExperiments

castle_model_experiments = CastleModelExperiments([1, 1, 1])
castle_model_experiments.run_experiments()

# from experiments.approximations.dining_cryptographers_experiments import DiningCryptographersExperiments
#
# dining_cryptographers_experiments = DiningCryptographersExperiments(5)
# dining_cryptographers_experiments.run_experiments()

# from experiments.approximations.drone_model_experiments import DroneModelExperiments
# from models.drone_model import CracowMap
#
# drone_model_experiments = DroneModelExperiments(1, [1], CracowMap())
# drone_model_experiments.run_experiments()

# from experiments.approximations.machines_model_exp import MachineModelExp
#
# machine_model_exp = MachineModelExp(1, 1, 1)
# machine_model_exp.run_experiments()

# from experiments.approximations.machines_model_security_exp import MachineModelSecurityExp
#
# machine_model_security_exp = MachineModelSecurityExp(1, 1, 1)
# machine_model_security_exp.run_experiments()

# from experiments.approximations.simple_voting_model_experiments import SimpleVotingModelExperiments
#
# simple_voting_model_experiments = SimpleVotingModelExperiments(2, 2)
# simple_voting_model_experiments.run_experiments()

# from experiments.approximations.tian_ji_model_experiments import TianJiModelExperiments
#
# tian_ji_model_experiments = TianJiModelExperiments(4)
# tian_ji_model_experiments.run_experiments()

# from experiments.approximations.multi_valued.cracow_pollution_model_exp import CracowPollutionModelExp
#
# cracow_pollution_model_exp = CracowPollutionModelExp(1, 1, 1, 7, 5)
# cracow_pollution_model_exp.run_experiments()

# from experiments.approximations.multi_valued.president_model_exp import PresidentModelExp
#
# president_model_exp = PresidentModelExp(5,1,5)
# president_model_exp.run_experiments()

# from experiments.approximations.strategy_logic.simple_voting_2_model_experiments import SimpleVoting2ModelExperiments
#
# simple_voting2_model_experiments = SimpleVoting2ModelExperiments(2, 5)
# simple_voting2_model_experiments.run_experiments()

# from experiments.strategy_simpl.random_model_exp import RandomModelExp

# data = [10, 100, 1000, 10000, 100000]
# data = [100, 1000]
# for model_size in data:
#     random_model_exp = RandomModelExp(model_size=model_size, exp_count=10, filename=f"random_results_{model_size}_v5.txt", timeout=60)
#     random_model_exp.run_experiments()

# random_model_exp = RandomModelExp(model_size=10, exp_count=1, filename=f"random_results_tt_v2.txt", timeout=60)
# random_model_exp.run_experiments()

# from experiments.strategy_simpl.drone_model_exp import DroneModelExp
#
# # data = [10, 100, 1000, 10000, 100000]
# data = [10]
# for model_size in data:
#     random_model_exp = DroneModelExp(model_size=model_size, exp_count=10, filename=f"drone_results_{model_size}_v4.txt", timeout=60, energy=model_size * 2)
#     random_model_exp.run_experiments()

# from experiments.strategy_simpl.drone_model_exp2 import DroneModelExp2
#
# # data = [10, 100, 1000, 10000, 100000]
# data = [3, 5]
# for model_size in data:
#     random_model_exp = DroneModelExp2(model_size=model_size, exp_count=5, filename=f"drone2_results_{model_size}_v1.txt", timeout=60, energy=model_size*2)
#     random_model_exp.run_experiments()