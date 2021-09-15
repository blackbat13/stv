from stv.models.synchronous.simple_voting_2_model import SimpleVoting2Model
import time


class SimpleVoting2ModelExperiments:
    def __init__(self, no_candidates: int, no_voters: int):
        self.no_candidates = no_candidates
        self.no_voters = no_voters
        self.model = None
        self.time_generation = 0

    def run_experiments(self):
        self.generate_model()
        quant_pref = [('Exist', 'se'), ('All', 'sc'), ('Exist', 'sv')]
        bind_pref = [('se', 0), ('sc', 1), ('sv', 2)]

        for voter_id in range(1, self.no_voters):
            quant_pref.append(('Exist', f'sv{voter_id}'))
            bind_pref.append((f'sv{voter_id}', voter_id + 2))

        formula = 'F (end_v & vote_v_0 & !punish_v)'

        winning_states = []
        state_id = -1
        voter_id = 0
        for state in self.model.states:
            state_id += 1
            if state['finish'][voter_id] and state['vote'][voter_id] == 0 and not state['pun'][voter_id]:
                winning_states.append(state_id)

        sl_model = self.model.model.to_sl_perfect(self.model.get_actions())

        start = time.perf_counter()
        result = sl_model.verify(winning_states, quant_pref, bind_pref)
        stop = time.perf_counter()

        time_verification = stop - start

        # for state_id in result:
        #     print(simple_voting.states[state_id])
        formula_result = False

        if 0 in result:
            formula_result = True
            print("True")
        else:
            print("False")

        file = open("results-sv2.txt", "a")
        file.write(f"no_candidates: {self.no_candidates}\n")
        file.write(f"no_voters: {self.no_voters}\n")
        file.write(f"no_states: {len(self.model.states)}\n")
        file.write(f"generation time: {self.time_generation}\n")
        file.write(f"verification time: {time_verification}\n")
        file.write(f"formula result: {formula_result}\n")
        file.write("\n\n")

        file.close()

    def generate_model(self):
        start = time.perf_counter()
        self.model = SimpleVoting2Model(self.no_voters, self.no_candidates)
        self.model.generate()
        stop = time.perf_counter()
        self.time_generation = stop - start

        print(self.time_generation)
        print(len(self.model.states))


if __name__ == "__main__":
    simple_voting2_model_experiments = SimpleVoting2ModelExperiments(2, 2)
    simple_voting2_model_experiments.run_experiments()
