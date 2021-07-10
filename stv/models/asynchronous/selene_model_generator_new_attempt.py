import itertools


class SeleneModelGenerator:
    def __init__(self, voter_count: int, cand_count: int):
        self._voter_count: int = voter_count
        self._cand_count: int = cand_count

    def generate(self):
        model = ""
        model += self._generate_ea()
        model += "\n"
        model += self._generate_voter()
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
        ea += "init: ea_init\n"
        trackers = [i for i in range(1, self._voter_count + 1)]
        perm = itertools.permutations(trackers)
        num = 0
        for p in list(perm):
            num += 1
            ea += f"shared generateTrackers_{num}: ea_init -> ea_gen [aID_t1={p[0]}"
            for tr_id in range(1, len(p)):
                ea += f", aID_t{tr_id + 1}={p[tr_id]}"
            ea += "]\n"
        ea += "shared startVoting: ea_gen -> ea_start\n"
        for voter_id in range(1, self._voter_count + 1):
            for tracker_id in range(1, self._voter_count + 1):
                ea += f"shared sendVote_Voter{voter_id}: ea_start -[aID_t{tracker_id}=={voter_id}]> ea_start [aID_vote{tracker_id}=?Voter{voter_id}_vote]\n"

        ea += "shared finishVoting: ea_start -> ea_finish\n"
        for voter_id in range(1, self._voter_count + 1):
            for tracker_id in range(1, self._voter_count + 1):
                ea += f"shared sendTracker_Voter{voter_id}: ea_finish -[aID_t{tracker_id}=={voter_id}]> ea_finish [Voter{voter_id}_true_tracker={tracker_id}]\n"

        ea += "shared allTrackerSend: ea_finish -> ea_send\n"
        for tracker_id in range(1, self._voter_count + 1):
            ea += f"shared coercerWBB{tracker_id}: ea_send -> ea_send [Coercer1_wbb{tracker_id}=?aID_vote{tracker_id}]\n"
        return ea

    def _generate_voter(self):
        voter = f"Agent Voter[{self._voter_count}]:\n"
        voter += "init: v_init\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"shared requestVoteFor{cand_id}_aID: v_init -> v_request [aID_req={cand_id}]\n"
        voter += "shared leave_aID: v_init -> v_request [aID-req=0]\n"
        voter += "shared startVoting: v_request -> v_start\n"

        for cand_id in range(1, self._cand_count + 1):
            voter += f"fillVote{cand_id}: v_start -> v_fill [aID_vote={cand_id}]\n"

        voter += "shared sendVote_aID: v_fill -> v_send \n"
        voter += "shared finishVoting: v_send -> v_finish\n"
        for tracker_id in range(1, self._voter_count + 1):
            voter += f"computeFalseTracker{tracker_id}: v_finish -> v_false_tr [aID_false_tr={tracker_id}]\n"
        voter += "dontComputeFalseAlphaTerm: v_finish -> v_false_tr\n"
        voter += "shared sendTracker_aID: v_false_tr -> v_send_tr\n"
        voter += "shared allTrackerSend: v_send_tr -> v_wbb\n"

        for tracker_id in range(1, self._voter_count + 1):
            voter += f"shared showTracker{tracker_id}_aID: v_wbb -[aID_true_tr=={tracker_id}]> v_show\n"
            voter += f"shared showTracker{tracker_id}_aID: v_wbb -[aID_false_tr=={tracker_id}]> v_show\n"

        voter += "PROTOCOL: [[leave_aID"
        for cand_id in range(1, self._cand_count + 1):
            voter += f",requestVoteFor{cand_id}_aID"

        voter += "]]\n"
        return voter

    def _generate_coercer(self):
        coercer = "Agent Coercer[1]:\n"
        coercer += "init: c_init\n"

        for voter_id in range(1, self._voter_count + 1):
            for cand_id in range(1, self._cand_count + 1):
                coercer += f"shared requestVoteFor{cand_id}_Voter{voter_id}: c_init -> c_init [aID_req{voter_id}={cand_id}]\n"
            coercer += f"shared leave_Voter{voter_id}: c_init -> c_init [aID_req{voter_id}=0]\n"

        coercer += "shared finishVoting: c_init -> c_finish\n"

        for tracker_id in range(1, self._voter_count + 1):
            coercer += f"shared coercerWBB{tracker_id}: c_finish -> c_finish\n"

        for voter_id in range(1, self._voter_count + 1):
            for tracker_id in range(1, self._voter_count + 1):
                coercer += f"shared showTracker{tracker_id}_Voter{voter_id}: c_finish -> c_finish [aID_tr{voter_id}={tracker_id}]\n"

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
        reduction = "REDUCTION: ["
        for voter_id in range(1, self._voter_count + 1):
            reduction += f"Voter{voter_id}_vote, "
        reduction += "Coercer1_end]\n"

        return reduction

    def _generate_persistent(self):
        persistent = "PERSISTENT: ["
        for voter_id in range(1, self._voter_count + 1):
            persistent += f"EA1_t{voter_id}, EA1_vote{voter_id}, Coercer1_req{voter_id}, Coercer1_tr{voter_id}, Coercer1_wbb{voter_id}, Voter{voter_id}_true_tr, Voter{voter_id}_req, Voter{voter_id}_false_tr, Voter{voter_id}_vote, "
        persistent += "Coercer1_end]\n"
        return persistent

    def _generate_coalition(self):
        coalition = "COALITION: [Coercer1]\n"
        return coalition

    def _generate_formula(self):
        formula = "FORMULA: <<Coercer1>>F(Voter1_vote=1)\n"
        return formula


if __name__ == "__main__":
    voter_count = 5
    cand_count = 2
    selene_model_generator = SeleneModelGenerator(voter_count, cand_count)
    model = selene_model_generator.generate()
    file = open(f"Selene_{voter_count}_{cand_count}.txt", "w")
    file.write(model)
    file.close()
