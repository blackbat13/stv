from stv.experiments import AExperiment
from stv.models.asynchronous import GlobalModel
from stv.models.asynchronous.parser import GlobalModelParser
from stv.parsers import FormulaParser
from stv.models.simple_model import SimpleModel
import time


class CountingExperiments():
    def __init__(self):
        pass

    def _first_model(self):
        model = SimpleModel(1)
        model.add_transition(0, 1, ["A"])
        model.add_transition(0, 2, ["A"])
        model.add_transition(1, 3, ["A"])
        model.add_transition(2, 4, ["A"])
        model.add_transition(3, 5, ["A"])
        model.add_transition(4, 5, ["B"])

        model.add_epistemic_relation(3, 4, 0)
        return model.to_atl_imperfect()

    def _second_model(self):
        model = SimpleModel(1)
        model.add_transition(0, 1, ["A"], 2)
        model.add_transition(0, 2, ["A"], 7)
        model.add_transition(1, 3, ["A"], 5)
        model.add_transition(2, 4, ["A"], 1)
        model.add_transition(3, 4, ["B"], 1)

        model.add_epistemic_class(0, {1, 2, 3})

        return model.to_atl_imperfect()

    def _third_model(self):
        model = SimpleModel(1)
        model.add_transition(0, 1, ["A"], 1)
        model.add_transition(0, 2, ["A"], 2)
        model.add_transition(1, 3, ["A"], 1)
        model.add_transition(2, 3, ["B"], 1)

        model.add_epistemic_class(0, {1, 2})

        return model.to_atl_imperfect()

    def _fourth_model(self):
        model = SimpleModel(1)
        model.add_transition(0, 1, ["A"], 1)
        model.add_transition(0, 2, ["A"], 2)
        model.add_transition(1, 3, ["A"], 2)
        model.add_transition(2, 4, ["B"], 2)
        model.add_transition(3, 5, ["A"], 1)
        model.add_transition(4, 6, ["A"], 1)
        model.add_transition(5, 6, ["B"], 1)

        model.add_epistemic_class(0, {1, 2})
        model.add_epistemic_class(0, {3, 4, 5})

        return model.to_atl_imperfect()

    def _fifth_model(self):
        model = SimpleModel(1)
        model.add_transition(0, 1, ["A"], 1)
        model.add_transition(0, 2, ["A"], 2)
        model.add_transition(1, 3, ["A"], 2)
        model.add_transition(2, 4, ["B"], 1)
        model.add_transition(3, 5, ["A"], 1)
        model.add_transition(4, 5, ["B"], 1)

        model.add_epistemic_class(0, {1, 2, 3, 4})

        return model.to_atl_imperfect()

    def _sixth_model(self):
        model = SimpleModel(1)
        model.add_transition(0, 1, ["A"])
        model.add_transition(0, 2, ["A"])
        model.add_transition(1, 4, ["A"])
        model.add_transition(2, 3, ["A"])
        model.add_transition(3, 4, ["B"])

        model.add_epistemic_class(0, {1, 3})

        return model.to_atl_imperfect()

    def _seventh_model(self):
        model = SimpleModel(1)
        model.add_transition(0, 1, ["A"])
        model.add_transition(0, 2, ["A"])
        model.add_transition(1, 3, ["A"])
        model.add_transition(2, 4, ["A"])
        model.add_transition(3, 5, ["A"])
        model.add_transition(4, 5, ["B"])

        model.add_epistemic_class(0, {2, 3, 4})

        return model.to_atl_imperfect()

    def _verify_all(self, model, winning):
        result = model.run_dfs_synthesis_one_agent(0, winning)
        print(f"Imperfect recall: {result}")

        result = model.run_dfs_perfect_recall_bounded_synthesis_one_agent(0, winning)
        print(f"Perfect recall: {result}")

        result = model.run_dfs_counting_bounded_synthesis_one_agent(0, winning)
        print(f"Counting: {result}")

        result = model.run_dfs_clock_bounded_synthesis_one_agent(0, winning)
        print(f"Clock: {result}")

        result = model.run_dfs_time_bounded_synthesis_one_agent(0, winning)
        print(f"Time: {result}")

        result = model.run_dfs_time_counting_bounded_synthesis_one_agent(0, winning)
        print(f"Time + Counting: {result}")

    def verify(self):
        print("-----FIRST MODEL-----")
        self._verify_all(self._first_model(), {5})
        print()

        print("-----SECOND MODEL-----")
        self._verify_all(self._second_model(), {4})
        print()

        print("-----THIRD MODEL-----")
        self._verify_all(self._third_model(), {3})
        print()

        print("-----FOURTH MODEL-----")
        self._verify_all(self._fourth_model(), {6})
        print()

        print("-----FIFTH MODEL-----")
        self._verify_all(self._fifth_model(), {5})
        print()

        print("-----SIXTH MODEL-----")
        self._verify_all(self._sixth_model(), {4})
        print()

        print("-----SEVENTH MODEL-----")
        self._verify_all(self._seventh_model(), {5})
        print()


if __name__ == "__main__":
    counting_experiments = CountingExperiments()
    counting_experiments.verify()
