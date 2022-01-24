from stv.experiments import AExperiment
from stv.models.asynchronous import GlobalModel
from stv.models.asynchronous.parser import GlobalModelParser
from stv.parsers import FormulaParser
import time


class RobotsExperiments(AExperiment):

    def __init__(self, robot_count: int, field_count: int, energy_count: int):
        super().__init__()
        self._file_name = f"robots_{robot_count}r_{field_count}f_{energy_count}e"

    def _open_results_file(self):
        self._results_file = open(f"{self._file_name}_results.txt", "a")

    def _write_file_header(self):
        pass

    def _generate_model(self):
        self._model = GlobalModelParser().parse(f"../../models/asynchronous/specs/generated/{self._file_name}.txt")
        start = time.process_time()
        self._model.generate(reduction=False)
        end = time.process_time()
        # self._model.model.simulate(0)
        print(f"Winning states: {self._model.get_real_formula_winning_states()}")
        print(
            f"Generation time: {end - start}, #states: {self._model.states_count}, #transitions: {self._model.transitions_count}")

    def _run_mc(self):
        atl_model = self._model.model.to_atl_imperfect()
        start = time.process_time()

        result = atl_model.run_dfs_counting_bounded_synthesis_one_agent(self._model.agent_name_to_id(self._model.coalition[0]),
                                                       set(self._model.get_real_formula_winning_states()))
        end = time.process_time()
        print(f"Verification time: {end - start}, result: {result}")
        print(atl_model.strategy)

    def _write_result(self):
        pass

    def _close_results_file(self):
        self._results_file.close()


if __name__ == "__main__":
    robots_experiments = RobotsExperiments(1, 2, 2)
    robots_experiments.run_experiments()