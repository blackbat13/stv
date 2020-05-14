class VotingModelGenerator:
    """
    Generator class for the asynchronous version of the Voting Model.

    :param voters_count: Number of voters.
    :param candidates_count: Number of candidates.

    :ivar _voters_count:
    :ivar _candidates_count:
    :ivar _model: Model string.
    """

    def __init__(self, voters_count: int, candidates_count: int):
        self._voters_count: int = voters_count
        self._candidates_count: int = candidates_count
        self._model: str = ""

    def generate(self):
        """
        Generates model.
        :return: None.
        """
        self._model += self._generate_voter() + "\n"
        self._model += self._generate_coercer() + "\n"
        self._model += self._generate_reduction()

    def save_to_file(self):
        """
        Saves model to file
        :return: None
        """
        if self._model == "":
            raise ValueError

        file = open(f"voting_{self._voters_count}_{self._candidates_count}.txt", "w")
        file.write(self._model)
        file.close()

    def _generate_voter(self) -> str:
        """
        Generates voter agent.
        :return: Voter agent string.
        """
        voter: str = f"Agent Voter[{self._voters_count}]:\n"
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

    def _generate_coercer(self) -> str:
        """
        Generates coercer agent.
        :return: Coercer agent string.
        """
        coercer: str = "Agent Coercer[1]:\n"
        coercer += "init_aID: q0\n"
        for voter_id in range(1, self._voters_count + 1):
            for cand_id in range(1, self._candidates_count + 1):
                coercer += f"shared gv{cand_id}_Voter{voter_id}: q0 -> q0\n"
                coercer += f"shared ng{cand_id}_Voter{voter_id}: q0 -> q0\n"
                coercer += f"shared stopG{cand_id}_Voter{voter_id}: q0 -> q{cand_id}_Voter{voter_id}\n"
                coercer += f"shared stopN{cand_id}_Voter{voter_id}: q0 -> q{cand_id}_Voter{voter_id}\n"
                coercer += f"np{cand_id}_Voter{voter_id}: q{cand_id}_Voter{voter_id} -> q0\n"
                coercer += f"pun{cand_id}_Voter{voter_id}: q{cand_id}_Voter{voter_id} -> q{cand_id}p_Voter{voter_id} [pun{voter_id}=true]\n"
                coercer += f"return{cand_id}_Voter{voter_id}: q{cand_id}p_Voter{voter_id} -> q0\n"

        return coercer

    def _generate_reduction(self) -> str:
        """
        Generates reduction section.
        :return: Reduction section string.
        """
        reduction: str = "REDUCTION: ["
        for voter_id in range(1, self._voters_count + 1):
            reduction += f"pun{voter_id}, "
            for cand_id in range(1, self._candidates_count + 1):
                reduction += f"Voter{voter_id}_revealed{cand_id}, "
                reduction += f"Voter{voter_id}_voted{cand_id}, "

        reduction = reduction.rstrip(", ")
        reduction += "]\n"
        return reduction


if __name__ == "__main__":
    CANDIDATES_COUNT = 4
    VOTERS_COUNT = 3
    voting_model_generator = VotingModelGenerator(VOTERS_COUNT, CANDIDATES_COUNT)
    voting_model_generator.generate()
    voting_model_generator.save_to_file()
