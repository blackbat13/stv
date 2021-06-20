from stv.models.synchronous.castle_model import CastleModel
from typing import List
import time
import datetime


class CastleModelExperiments:
    def __init__(self, castle_sizes: List[int], castle_life: List[int] = [3, 3, 3]):
        self.castle_sizes = castle_sizes
        self.castle_life = castle_life
        self.results_file = None
        self.coalition = []
        self.castle_model: CastleModel = None
        self.winning_states = []
        self.result: bool = None
        self.atl_model = None
        self.verification_time: int = 0
        self.result_states = []
        self.prop = 'castle3defeated'
        self.formula = f'<<c1, c2>> F {self.prop}'

    def run_experiments(self):
        print(datetime.datetime.now())
        self.results_file = open("castles_results.txt", "a")
        self.write_file_header()
        self.coalition_a_b()
        self.results_file.write(f'Coalition: {self.coalition}\n')
        print("START: generate model")
        self.generate_model()
        print("END: generate model")
        self.get_atl_model()
        self.results_file.write(f'Formula: {self.formula}\n')
        self.get_winning_states()
        print("START: verification")
        self.run_verification()
        print("END: verification")
        self.results_file.close()
        print(f"Results written in castles_results.txt")

    def write_file_header(self):
        self.results_file.write(f'----------------Castles Model----------------\n')
        self.results_file.write(f'{datetime.datetime.now()}\n')
        self.results_file.write(f'Castles size: {self.castle_sizes}\nCastles life: {self.castle_life}\n')

    def coalition_a_b(self):
        self.coalition = []
        for i in range(0, self.castle_sizes[0] + self.castle_sizes[1]):
            self.coalition.append(i)

    def generate_model(self):
        start = time.process_time()
        self.castle_model = CastleModel(self.castle_sizes, self.castle_life)
        self.castle_model.generate()
        self.castle_model.model.to_subjective(self.coalition)
        end = time.process_time()
        self.results_file.write(f'Model generated in: {end - start} seconds\n')
        no_states = len(self.castle_model.states)
        self.results_file.write(f'Number of states in the model: {no_states}\n')

    def get_winning_states(self):
        self.winning_states = self.castle_model.get_winning_states(self.prop)

    def get_atl_model(self, imperfect: bool = True):
        if imperfect:
            self.atl_model = self.castle_model.model.to_atl_imperfect(self.castle_model.get_actions())
        else:
            self.atl_model = self.castle_model.model.to_atl_perfect(self.castle_model.get_actions())

    def run_verification(self):
        start = time.process_time()
        self.result_states = self.atl_model.minimum_formula_many_agents(self.coalition, self.winning_states)
        end = time.process_time()
        self.verification_time = end - start
        self.result = 0 in self.result_states
        self.results_file.write(f'Formula verified in: {self.verification_time} seconds\n')
        self.results_file.write(f'Formula result: {self.result}\n')

    @staticmethod
    def read_castle_sizes() -> List[int]:
        workers = []
        for i in range(1, 4):
            workers.append(int(input(f'Number of workers in Castle {i}: ')))
        return workers


if __name__ == "__main__":
    castle_model_experiments = CastleModelExperiments(CastleModelExperiments.read_castle_sizes())
    castle_model_experiments.run_experiments()
