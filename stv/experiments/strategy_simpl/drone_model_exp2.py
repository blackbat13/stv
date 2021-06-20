from stv.models.synchronous.drone_model import *
from stv.comparing_strats.strategy_comparer import StrategyComparer
import datetime
import time
import signal


class DroneModelExp2:
    def __init__(self, model_size: int, exp_count: int, filename: str, timeout: int = 60, energy: int = 10,
                 DEBUG: bool = False):
        self.__exp_count = exp_count
        self.__DEBUG = DEBUG
        self.__model_size = model_size
        self.__filename = filename
        self.__file = None
        self.__timeout = timeout
        self.__avg_upper_approx_time = 0
        self.__avg_lower_approx_time = 0
        self.__avg_model_states = 0
        self.__avg_perfect_reachable_states = 0
        self.__avg_simplified_reachable_states = 0
        self.__avg_perfect_mismatch = 0
        self.__avg_simplified_mismatch = 0
        self.__avg_perfect_time = 0
        self.__avg_simplified_time = 0
        self.__avg_model_time = 0
        self.__avg_domino_time = 0
        self.__energy = energy
        signal.signal(signal.SIGALRM, self.__timeout_handler)

    def run_experiments(self):
        self.__file = open(self.__filename, "a")

        self.__file.write(f"EXPERIMENTS START: {datetime.datetime.now()}")
        i = 0
        while i < self.__exp_count:
            self.__file.write(f"----BEGIN: EXPERIMENT {i}----\n")
            result = self._run_experiment()
            if result == False:
                continue
            self.__file.write(f"----END: EXPERIMENT {i}----\n")
            i += 1

        self.__file.write("------STATISTICS------\n")
        self.__file.write(f"Average model generation time: {self.__avg_model_time / self.__exp_count} s\n")
        self.__file.write(f"Average model states count: {self.__avg_model_states / self.__exp_count}\n")
        self.__file.write(f"Average perfect strategy generation time: {self.__avg_perfect_time / self.__exp_count} s\n")
        self.__file.write(f"Average simplified strategy time: {self.__avg_simplified_time / self.__exp_count} s\n")
        self.__file.write(f"Average domino dfs time: {self.__avg_domino_time / self.__exp_count} s\n")
        self.__file.write(f"Average lower approximation time: {self.__avg_lower_approx_time / self.__exp_count} s\n")
        self.__file.write(f"Average upper approximation time: {self.__avg_upper_approx_time / self.__exp_count} s\n")
        self.__file.write(
            f"Average approximation time: {(self.__avg_lower_approx_time + self.__avg_upper_approx_time) / self.__exp_count}\n")
        self.__file.write(
            f"Average perfect strategy reachable states: {self.__avg_perfect_reachable_states / self.__exp_count}\n")
        self.__file.write(
            f"Average simplified strategy reachable states: {self.__avg_simplified_reachable_states / self.__exp_count}\n")
        self.__file.write(
            f"Average perfect strategy epistemic mismatch: {self.__avg_perfect_mismatch / self.__exp_count}\n")
        self.__file.write(
            f"Average simplified strategy epistemic mismatch: {self.__avg_simplified_mismatch / self.__exp_count}\n")
        self.__file.write("------END STATISTICS------\n\n\n")
        self.__file.close()

    def _run_experiment(self):
        random_model = DroneModel(2, [self.__energy, self.__energy], MapGenerator(self.__model_size), is_random=True)
        start = time.process_time()
        random_model.generate()
        end = time.process_time()
        self.__file.write(f"Model generated in {end - start}s\n")
        self.__file.write(f"Model has {len(random_model.states)} states\n")
        self.__file.write("-------------------BEGIN: PERFECT INFORMATION STRATEGY-------------------\n")
        strategy = self._generate_perfect_information_strategy(random_model)
        print(strategy)
        if strategy is None:
            return False
        self.__avg_model_time += (end - start)
        self.__avg_model_states += len(random_model.states)
        self.__file.write("-------------------BEGIN: PERFECT INFORMATION STRATEGY-------------------\n")
        self.__file.write("-------------------BEGIN: SIMPLIFIED STRATEGY-------------------\n")
        simplified_strategy = self._generate_simplified_strategy(random_model, strategy)
        print(simplified_strategy)
        self.__file.write("-------------------END: SIMPLIFIED STRATEGY-------------------\n")
        self.__file.write("-------------------BEGIN: DOMINO DFS-------------------\n")
        # signal.alarm(self.__timeout+30)
        # try:
        #     self._run_domino_dfs(random_model)
        # except Exception as exc:
        #     self.__file.write(f"{exc}\n")
        #     self.__avg_domino_time += self.__timeout + 30
        # signal.alarm(0)
        # self.__file.write("-------------------END: DOMINO DFS-------------------\n")
        # self.__file.write("-------------------BEGIN: APPROXIMATIONS-------------------\n")
        # self._run_approximations(random_model)
        # self.__file.write("-------------------END: APPROXIMATIONS-------------------\n")
        return True

    def _run_domino_dfs(self, model: DroneModel):
        winning_states = model.get_winning_states("win")
        strategy_comparer = StrategyComparer(model.model, model.get_actions()[0])
        start = time.process_time()
        (result, strategy) = strategy_comparer.domino_dfs(0, set(winning_states), [0], strategy_comparer.basic_h)
        end = time.process_time()
        self.__avg_domino_time += (end - start)
        self.__file.write(f"Strategy found in: {end - start}s\n")
        self.__file.write(f'Strategy result: {result}\n')
        self.__file.write(f"{strategy}\n")
        if self.__DEBUG:
            self._print_strategy(strategy)

    def _run_approximations(self, model: DroneModel):
        winning_states = model.get_winning_states("win")
        signal.alarm(self.__timeout)
        start = time.process_time()
        try:
            result = model.model.to_atl_imperfect(model.get_actions()).minimum_formula_one_agent(0, winning_states)
        except Exception as exc:
            self.__file.write(f"{exc}\n")
            self.__avg_lower_approx_time += self.__timeout
            return
        signal.alarm(0)
        end = time.process_time()
        self.__avg_lower_approx_time += (end - start)
        self.__file.write(f"Lower approximation time: {end - start}s\n")
        self.__file.write(f"Lower approximation result: {0 in result}\n")
        new_timeout = self.__timeout - (end - start)
        if new_timeout < 1:
            self.__file.write("Timeout!\n")
            return
        signal.alarm(int(new_timeout))
        start = time.process_time()
        try:
            result = model.model.to_atl_perfect(model.get_actions()).minimum_formula_one_agent(0, winning_states)
        except Exception as exc:
            self.__file.write(f"{exc}\n")
            self.__avg_upper_approx_time += new_timeout
            return
        signal.alarm(0)
        end = time.process_time()
        self.__avg_upper_approx_time += (end - start)
        self.__file.write(f"Upper approximation time: {end - start}s\n")
        self.__file.write(f"Upper approximation result: {0 in result}\n")

    def _print_strategy(self, strategy):
        for index, value in enumerate(strategy):
            if value is not None:
                self.__file.write(f"{index}: {value}\n")

    def _generate_perfect_information_strategy(self, model: DroneModel):
        winning_states = model.get_winning_states("win")
        strategy_comparer = StrategyComparer(model.model, model.get_actions()[0])
        start = time.process_time()
        strategy = strategy_comparer.generate_winning_strategy_perfect_information_coalition(list(winning_states))
        end = time.process_time()
        defined_in = 0
        if strategy[0] is None:
            return None
        self.__avg_perfect_time += (end - start)
        self.__file.write(f"Strategy generated in: {end - start}s\n")
        self.__file.write(f"Strategy result: {strategy[0] is not None}\n")
        # self.__file.write(f"{strategy}\n")
        if self.__DEBUG:
            self._print_strategy(strategy)
        for index, value in enumerate(strategy):
            if value is not None:
                defined_in += 1
        epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0,
                                                                        strategy) + strategy_comparer.count_epistemic_mismatch(
            1, strategy)
        self.__file.write(
            f"Non control states in strategy: {strategy_comparer.count_non_control_states(0, strategy)}\n")
        self.__file.write(f"Epistemic mismatch for random strategy: {epistemic_mismatch}\n")
        self.__file.write(f"Random strategy defined in {defined_in} states\n")
        self.__avg_perfect_mismatch += epistemic_mismatch
        self.__avg_perfect_reachable_states += defined_in
        return strategy

    def _generate_simplified_strategy(self, model: DroneModel, strategy):
        strategy_comparer = StrategyComparer(model.model, model.get_actions()[0])
        start = time.process_time()
        # simplified_strategy = strategy_comparer.simplify_strategy_one_agent(0, strategy, None)
        simplified_strategy = strategy_comparer.simplify_strategy_coalition_imperfect_info([0, 1], strategy,
                                                                                           self.__timeout)
        end = time.process_time()
        self.__avg_simplified_time += (end - start)
        self.__file.write(f"Strategy simplified in: {end - start}s\n")
        # self.__file.write(f"{simplified_strategy}\n")
        if self.__DEBUG:
            self._print_strategy(simplified_strategy)
        self.__file.write(f"Different: {simplified_strategy != strategy}\n")
        defined_in = 0
        for index, value in enumerate(simplified_strategy):
            if value is not None:
                if self.__DEBUG:
                    print(f"{index}: {value}\n")
                defined_in += 1

        epistemic_mismatch = strategy_comparer.count_epistemic_mismatch(0,
                                                                        simplified_strategy) + strategy_comparer.count_epistemic_mismatch(
            1, simplified_strategy)
        self.__file.write(
            f"Non control states in strategy: {strategy_comparer.count_non_control_states(0, simplified_strategy)}\n")
        self.__file.write(f"Epistemic mismatch for simplified strategy: {epistemic_mismatch}\n")
        self.__file.write(f"Simpified strategy defined in {defined_in} states\n")
        self.__avg_simplified_mismatch += epistemic_mismatch
        self.__avg_simplified_reachable_states += defined_in
        return simplified_strategy

    def __timeout_handler(self, signum, frame):
        raise Exception("Timeout!")
