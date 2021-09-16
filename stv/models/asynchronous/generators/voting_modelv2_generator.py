class VotingModelV2Generator:
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
        self._model += self._generate_persistent()
        self._model += "COALITION: [Coercer1]\n"
        self._model += "FORMULA: <<Coercer1>>F(Coercer1_pun1=True)\n"

    def save_to_file(self):
        """
        Saves model to file
        :return: None
        """
        if self._model == "":
            raise ValueError

        file = open(f"voting_v2_{self._voters_count}_{self._candidates_count}.txt", "w")
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
            voter += f"vote{cand_id}: q0 -> q1 [aID_vote={cand_id},Coercer1_aID_voted=true]\n"

        voter += f"shared gv_aID: q1 -> q2 [Coercer1_aID_vote=?aID_vote]\n"
        voter += f"shared ng_aID: q1 -> q2\n"
        voter += f"shared pun_aID: q2 -> q3\n"
        voter += f"shared npun_aID: q2 -> q3\n"

        voter += "PROTOCOL: [[pun_aID, npun_aID]]\n"
        return voter

    def _generate_coercer(self) -> str:
        """
        Generates coercer agent.
        :return: Coercer agent string.
        """
        coercer: str = "Agent Coercer[1]:\n"
        coercer += "init: q0\n"
        for voter_id in range(1, self._voters_count + 1):
            coercer += f"shared gv_Voter{voter_id}: q0 -> q0 [aID_Voter{voter_id}_gv=true]\n"
            coercer += f"shared ng_Voter{voter_id}: q0 -> q0 [aID_Voter{voter_id}_ng=true]\n"
            coercer += f"shared pun_Voter{voter_id}: q0 -> q0 [aID_pun{voter_id}=true]\n"
            coercer += f"shared npun_Voter{voter_id}: q0 -> q0 [aID_npun{voter_id}=true]\n"

        coercer += "PROTOCOL: ["
        for voter_id in range(1, self._voters_count + 1):
            coercer += f"[gv_Voter{voter_id},ng_Voter{voter_id}],"
        coercer = coercer.rstrip(",")
        coercer += "]\n"
        return coercer

    def _generate_reduction(self) -> str:
        """
        Generates reduction section.
        :return: Reduction section string.
        """
        reduction: str = "REDUCTION: [Coercer1_pun1]\n"
        return reduction

    def _generate_persistent(self) -> str:
        persistent: str = "PERSISTENT: ["
        for voter_id in range(1, self._voters_count + 1):
            persistent += f"Voter{voter_id}_vote, Coercer1_Voter{voter_id}_vote, Coercer1_pun{voter_id}, Coercer1_npun{voter_id}, Coercer1_Voter{voter_id}_gv, Coercer1_Voter{voter_id}_ng, Coercer1_Voter{voter_id}_voted"

        persistent = persistent.rstrip(", ")
        persistent += "]\n"
        return persistent


if __name__ == "__main__":
    CANDIDATES_COUNT = 2
    VOTERS_COUNT = 7
    voting_model_generator = VotingModelV2Generator(VOTERS_COUNT, CANDIDATES_COUNT)
    voting_model_generator.generate()
    voting_model_generator.save_to_file()
