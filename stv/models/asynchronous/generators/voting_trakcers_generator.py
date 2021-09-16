import itertools


class VotingTrackersGenerator:
    def __init__(self, voter_count: int, coerced_voter_count: int, cand_count: int):
        self._voter_count = voter_count
        self._coerced_voter_count = coerced_voter_count
        self._cand_count = cand_count
        self._trackers_count = self._voter_count + self._coerced_voter_count

    def generate(self):
        model = ""
        model += self._generate_ea()
        model += "\n"
        model += self._generate_voter()
        model += "\n"
        model += self._generate_coerced_voter()
        model += "\n"
        model += self._generate_coercer()
        model += "\n"
        model += self._generate_reduction()
        model += self._generate_persistent()
        model += self._generate_coalition()
        model += self._generate_formula()
        return model

    def _generate_ea(self):
        ea = "Agent EA[1]:\n"
        ea += "init: start\n"
        trackers = [i for i in range(1, self._voter_count + self._coerced_voter_count + 1)]
        perm = itertools.permutations(trackers)
        num = 0
        for p in list(perm):
            num += 1
            ea += f"generateTrackers_{num}: start -> generate [aID_tracker1={p[0]}"
            for tr_id in range(1, len(p)):
                ea += f", aID_tracker{tr_id + 1}={p[tr_id]}"
            ea += "]\n"
        ea += "shared startVoting: generate -> voting\n"
        ea += "shared finishVoting: voting -> finish\n"
        ea += "shared finishSendingTrackers: finish -> check\n"
        for voter_id in range(1, self._voter_count + 1):
            for tr_id in range(1, self._voter_count + self._coerced_voter_count + 1):
                ea += f"shared sendVote_Voter{voter_id}: voting -[aID_tracker{tr_id}=={voter_id}]> voting [aID_tracker{tr_id}_vote=?Voter{voter_id}_vote]\n"

        for voter_id in range(1, self._coerced_voter_count + 1):
            for tr_id in range(1, self._voter_count + self._coerced_voter_count + 1):
                ea += f"shared sendVote_VoterC{voter_id}: voting -[aID_tracker{tr_id}=={voter_id+self._voter_count}]> voting [aID_tracker{tr_id}_vote=?VoterC{voter_id}_vote]\n"

        ea += "shared allTrackerSend: ea_pub_v -> ea_send\n"
        return ea

    def _generate_voter(self):
        voter = f"Agent Voter[{self._voter_count}]:\n"
        voter += "init: v_init\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"shared requestVoteFor{cand_id}_aID: v_init -> v_request [aID_req={cand_id}]\n"
        voter += "shared leave_aID: v_init -> v_request\n"
        voter += "shared startVoting: v_request -> v_start\n"
        voter += "createCommitment: v_start -> v_commit\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"fillVote{cand_id}: v_commit -> v_fill [aID_vote={cand_id}]\n"
        voter += "encryptVote: v_fill -> v_encrypt\n"
        voter += "shared sendVote_aID: v_encrypt -> v_send ["
        for teller_id in range(1, self._teller_count + 1):
            voter += f"Teller{teller_id}_vote_aID=?aID_vote,"
        voter = voter.rstrip(",")
        voter += "]\n"
        voter += "shared finishVoting: v_send -> v_finish\n"
        voter += "shared publishVotes: v_finish -> v_publish\n"
        voter += f"computeFalseAlphaTerm: v_publish -> v_false_a\n"
        # voter += "verifyElectionResults: v_publish -> v_publish\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"computeFalseTracker{cand_id}: v_false_a -> v_false_tr [aID_false_tr={cand_id}]\n"
        voter += "dontComputeFalseAlphaTerm: v_publish -> v_false_tr\n"
        voter += "shared sendTracker_aID: v_false_tr -> v_send_tr\n"
        voter += "shared allTrackerSend: v_send_tr -> v_wbb\n"
        # for tr_id in range(1, self._voter_count + 1):
        #     voter += f"shared aID_WBB{tr_id}: v_wbb -> v_wbb2\n"
        voter += "verifyVote: v_wbb -> v_wbb2\n"
        voter += "wait: v_wbb -> v_wbb2\n"

        for tracker_id in range(1, self._voter_count + 1):
            voter += f"shared showTracker{tracker_id}_aID: v_wbb2 -[aID_true_tr=={tracker_id}]> v_show [aID_true_tr=0, aID_false_tr=0]\n"
            voter += f"shared showTracker{tracker_id}_aID: v_wbb2 -[aID_false_tr=={tracker_id}]> v_show [aID_true_tr=0, aID_false_tr=0]\n"

        voter += "shared punish_aID: v_show -> v_end\n"
        voter += "shared not_punish_aID: v_show -> v_end\n"

        voter += "PROTOCOL: [[leave_aID"
        for cand_id in range(1, self._cand_count + 1):
            voter += f",requestVoteFor{cand_id}_aID"

        voter += "],[punish_aID,not_punish_aID]]\n"
        return voter

    def _generate_coercer(self):
        coercer = "Agent Coercer[1]:\n"
        coercer += "init: c_init\n"
        coercer += "shared publishTrackers: c_init -> c_req\n"
        coercer += "shared startVoting: c_req -> c_voting\n"
        coercer += "shared finishVoting: c_voting -> c_finish\n"
        coercer += "shared publishVotes: c_finish -> c_pub [aID_end=true]\n"
        for voter_id in range(1, self._voter_count + 1):
            coercer += f"shared leave_Voter{voter_id}: c_req -> c_req [aID_req{voter_id}=0]\n"
            coercer += f"shared punish_Voter{voter_id}: c_pub -> c_pub [aID_pun{voter_id}=true]\n"
            coercer += f"shared not_punish_Voter{voter_id}: c_pub -> c_pub [aID_npun{voter_id}=true]\n"
            coercer += f"shared coercerWBB{voter_id}: c_pub -> c_pub\n"

            for cand_id in range(1, self._cand_count + 1):
                coercer += f"shared requestVoteFor{cand_id}_Voter{voter_id}: c_req -> c_req [aID_req{voter_id}={cand_id}]\n"

            for tracker_id in range(1, self._voter_count + 1):
                coercer += f"shared showTracker{tracker_id}_Voter{voter_id}: c_pub -> c_pub [aID_tr{voter_id}={tracker_id}]\n"
        coercer += "PROTOCOL: ["
        for voter_id in range(1, self._voter_count + 1):
            coercer += "["
            for tracker_id in range(1, self._voter_count + 1):
                coercer += f"showTracker{tracker_id}_Voter{voter_id},"
            coercer = coercer.rstrip(",")
            coercer += "],"
        coercer = coercer.rstrip(",")
        coercer += "]\n"
        return coercer

    def _generate_reduction(self):
        if self._formula == 0:
            reduction = "REDUCTION: [Coercer1_pun1]\n"
        elif self._formula == 1:
            reduction = "REDUCTION: [Coercer1_pun1]\n"
        elif self._formula == 2 or self._formula == 3:
            reduction = "REDUCTION: ["
            for voter_id in range(1, self._voter_count + 1):
                reduction += f"Voter{voter_id}_vote, "
            reduction += "Coercer1_end]\n"
        elif self._formula == 4:
            reduction = "REDUCTION: [Coercer1_end, Voter1_vote]\n"
        return reduction

    def _generate_persistent(self):
        persistent = "PERSISTENT: ["
        for voter_id in range(1, self._voter_count + 1):
            persistent += f"ElectionAuthority1_t{voter_id}, WBB1_t{voter_id}, WBB1_vote{voter_id}, Voter{voter_id}_true_tr, Voter{voter_id}_false_tr, Voter{voter_id}_vote, " #Coercer1_tr{voter_id}, "
            for teller_id in range(1, self._teller_count + 1):
                persistent += f"Teller{teller_id}_vote_Voter{voter_id}, "
        persistent += "Coercer1_end]\n"
        return persistent

    def _generate_coalition(self):
        if self._formula == 2:
            coalition = "COALITION: [Voter1]\n"
        else:
            coalition = "COALITION: [Coercer1]\n"
        return coalition

    def _generate_formula(self):
        formula = "FORMULA: <<Coercer1>>F(Coercer1_pun1=True)\n"
        return formula


if __name__ == "__main__":
    teller_count = 1  # int(input("Teller Count: "))
    voter_count = 1  # int(input("Voter Count: "))
    cand_count = 2  # int(input("Candidates Count: "))
    formula = 2  # int(input("Formula: "))
    selene_model_generator = SeleneModelGenerator(teller_count, voter_count, cand_count, formula)
    model = selene_model_generator.generate()
    file = open(f"Selene_{teller_count}_{voter_count}_{cand_count}_{formula}.txt", "w")
    file.write(model)
    file.close()
