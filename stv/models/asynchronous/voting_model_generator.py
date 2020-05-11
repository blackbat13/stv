class VotingModelGenerator:
    def __init__(self, voters_count, candidates_count):
        self._voters_count = voters_count
        self._candidates_count = candidates_count
        self._model = ""

    def generate(self):
        self._model += self._generate_voter() + "\n"
        self._model += self._generate_coercer() + "\n"
        self._model += self._generate_reduction()
        return self._model

    def _generate_voter(self):
        voter = f"Agent Voter[{self._voters_count}]:\n"
        voter += "init: q0\n"
        for cand_id in range(1, self._candidates_count + 1):
            voter += f"vote{cand_id}: q0 -> v{cand_id}\n"
            voter += f"shared gv{cand_id}_aID: v{cand_id} -> gv{cand_id}  [aID_revealed{cand_id}=true]\n"
            voter += f"shared ng{cand_id}_aID: v{cand_id} -> ngv{cand_id}\n"
            voter += f"repeatG{cand_id}: gv{cand_id} -> q0\n"
            voter += f"repeatN{cand_id}: ngv{cand_id} -> q0\n"
            voter += f"shared stopG{cand_id}_aID: gv{cand_id} -> sg{cand_id} [aID_voted{cand_id}=true]\n"
            voter += f"shared stopN{cand_id}_aID: ngv{cand_id} -> sn{cand_id} [aID_voted{cand_id}=true]\n"
            voter += f"loopG{cand_id}: sg{cand_id} -> sg{cand_id}\n"
            voter += f"loopN{cand_id}: sn{cand_id} -> sn{cand_id}\n"
        return voter

    def _generate_coercer(self):
        coercer = "Agent Coercer[1]:\n"
        coercer += "init_aID: q0\n"
        for voter_id in range(1, self._voters_count + 1):
            for cand_id in range(1, self._candidates_count + 1):
                coercer += f"shared gv{cand_id}_Voter{voter_id}: q0 -> q0\n"
                coercer += f"shared ng{cand_id}_Voter{voter_id}: q0 -> q0\n"
                coercer += f"shared stopG{cand_id}_Voter{voter_id}: q0 -> q{cand_id}_Voter{voter_id}\n"
                coercer += f"shared stopN{cand_id}_Voter{voter_id}: q0 -> q{cand_id}_Voter{voter_id}\n"
                coercer += f"np{cand_id}_Voter{voter_id}: q{cand_id}_Voter{voter_id} -> q0\n"
                coercer += f"pun{cand_id}_Voter{voter_id}: q{cand_id}_Voter{voter_id} -> q{cand_id}p_Voter{voter_id} [pun{cand_id}_{voter_id}=true]\n"
                coercer += f"return{cand_id}_Voter{voter_id}: q{cand_id}p_Voter{voter_id} -> q0\n"
        return coercer

    def _generate_reduction(self):
        reduction = "REDUCTION: ["
        for voter_id in range(1, self._voters_count + 1):
            for cand_id in range(1, self._candidates_count + 1):
                reduction += f"pun{cand_id}_{voter_id}, " # Remove cand_id
                reduction += f"Voter{voter_id}_revealed{cand_id}, "
                reduction += f"Voter{voter_id}_voted{cand_id}, "
        reduction = reduction.rstrip(", ")
        reduction += "]\n"
        return reduction


if __name__ == "__main__":
    candidates_count = 4
    voters_count = 3
    voting_model_generator = VotingModelGenerator(voters_count, candidates_count)
    file = open(f"voting_{voters_count}_{candidates_count}.txt", "w")
    file.write(voting_model_generator.generate())
    file.close()