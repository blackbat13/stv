import itertools


class SeleneModelGenerator:
    def __init__(self, teller_count: int, voter_count: int, cand_count: int):
        self._teller_count: int = teller_count
        self._voter_count: int = voter_count
        self._cand_count: int = cand_count

    def generate(self):
        model = ""
        model += self._generate_teller()
        model += "\n"
        model += self._generate_ea()
        model += "\n"
        model += self._generate_wbb()
        model += "\n"
        model += self._generate_voter()
        model += "\n"
        model += self._generate_coercer()
        model += "\n"
        model += self._generate_reduction()
        model += self._generate_persistent()
        return model

    def _generate_teller(self):
        teller = f"Agent Teller[{self._teller_count}]:\n"
        teller += "init: t_init\n"
        for voter_id in range(1, self._voter_count + 1):
            teller += f"shared sendVote_Voter{voter_id}: t_init -> t_init [v_Voter{voter_id}?]\n"
        teller += "shared finishVoting: t_init -> t_finish\n"
        teller += "shared decryptVotes: t_finish -> t_decrypt\n"
        teller += "shared sendToWBB: t_decrypt -> t_send [v_Voter1"
        for voter_id in range(2, self._voter_count + 1):
            teller += f", v_Voter{voter_id}"
        teller += "]\n"
        teller += "shared publishVotes: t_send -> t_publish\n"
        return teller

    def _generate_ea(self):
        ea = "Agent ElectionAuthority[1]:\n"
        ea += "init: ea_init\n"
        trackers = [i for i in range(1, self._voter_count + 1)]
        perm = itertools.permutations(trackers)
        num = 0
        for p in list(perm):
            num += 1
            ea += f"shared generateTrackers_{num}: ea_init -> ea_gen [t1={p[0]}"
            for tr_id in range(1, len(p)):
                ea += f", t{tr_id + 1}={p[tr_id]}"
            ea += "]\n"
        ea += "shared publishTrackers: ea_gen -> ea_pub_t\n"
        ea += "shared startVoting: ea_pub_t -> ea_start\n"
        ea += "shared finishVoting: ea_start -> ea_finish\n"
        ea += "shared publishVotes: ea_finish -> ea_pub_v [published=true]\n"
        for voter_id in range(1, self._voter_count + 1):
            for tr_id in range(1, self._voter_count + 1):
                ea += f"shared sendTracker_Voter{voter_id}: ea_pub_v -[t{tr_id}=={voter_id}]> ea_pub_v [t_Voter{voter_id}={tr_id}]\n"
        ea += "shared allTrackerSend: ea_pub_v -> ea_send [end=true]\n"
        return ea

    def _generate_wbb(self):
        wbb = "Agent WBB[1]:\n"
        wbb += "init: wbb_init\n"
        trackers = [i for i in range(1, self._voter_count + 1)]
        perm = itertools.permutations(trackers)
        num = 0
        for p in list(perm):
            num += 1
            wbb += f"shared generateTrackers_{num}: wbb_init -> wbb_gen{num} [t1={p[0]}"
            for tr_id in range(1, len(p)):
                wbb += f", t{tr_id + 1}={p[tr_id]}"
            wbb += "]\n"
            wbb += f"shared sendToWBB: wbb_gen{num} -> wbb_send [wbb_t1=v_Voter{p[0]}"
            for tr_id in range(1, len(p)):
                wbb += f", wbb_t{tr_id + 1}=v_Voter{p[tr_id]}"
            wbb += "]\n"
        wbb += "PROTOCOL wbb_init: [[generateTrackers_1"
        for i in range(1, len(list(perm)) + 1):
            wbb += f", generateTrackers_{i}"
        wbb += "]]\n"
        for cand_id in range(1, self._cand_count + 1):
            for tr_id in range(1, self._voter_count + 1):
                wbb += f"shared coercerWBB{tr_id}{cand_id}true: wbb_send -[wbb_t{tr_id}=={cand_id}]> wbb_send\n"
                wbb += f"shared coercerWBB{tr_id}{cand_id}false: wbb_send -[wbb_t{tr_id}!={cand_id}]> wbb_send\n"
                for voter_id in range(1, self._voter_count + 1):
                    wbb += f"shared Voter{voter_id}_WBB{tr_id}{cand_id}true: wbb_send -[wbb_t{tr_id}=={cand_id}]> wbb_send\n"
                    wbb += f"shared Voter{voter_id}_WBB{tr_id}{cand_id}false: wbb_send -[wbb_t{tr_id}!={cand_id}]> wbb_send\n"
        return wbb

    def _generate_voter(self):
        voter = f"Agent Voter[{self._voter_count}]:\n"
        voter += "init: v_init\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"shared requestVoteFor{cand_id}_aID: v_init -> v_request [req_aID={cand_id}]\n"
        voter += "shared leave_aID: v_init -> v_request\n"
        voter += "PROTOCOL v_init: [[leave_aID"
        for cand_id in range(1, self._cand_count + 1):
            voter += f", requestVoteFor{cand_id}_aID"
        voter += "]]\n"
        voter += "shared startVoting: v_request -> v_start\n"
        voter += "createCommitment: v_start -> v_commit\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"fillVote{cand_id}: v_commit -> v_fill [v_aID={cand_id}]\n"
        voter += "encryptVote: v_fill -> v_encrypt\n"
        voter += "shared sendVote_aID: v_encrypt -> v_send [v_aID]\n"
        voter += "shared finishVoting: v_send -> v_finish\n"
        voter += "shared publishVotes: v_finish -> v_publish\n"
        voter += "verifyElectionResults: v_publish -> v_publish\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"computeFalseAlphaTerm_{cand_id}: v_publish -> v_false_a [false_a_aID={cand_id}]\n"
            voter += f"computeFalseTracker{cand_id}: v_false_a -> v_false_tr [false_tr_aID={cand_id}]\n"
        voter += "dontComputeFalseAlphaTerm: v_publish -> v_false_tr\n"
        voter += "shared sendTracker_aID: v_false_tr -> v_send_tr [tr_aID]\n"
        voter += "shared allTrackerSend: v_send_tr -> v_wbb\n"
        for cand_id in range(1, self._cand_count + 1):
            for tr_id in range(1, self._voter_count + 1):
                voter += f"shared aID_WBB{tr_id}{cand_id}true: v_wbb -> v_wbb [t{tr_id}_aID={cand_id}]\n"
                voter += f"shared aID_WBB{tr_id}{cand_id}false: v_wbb -> v_wbb\n"
        voter += "verifyVote: v_wbb -> v_wbb\n"
        voter += "wait: v_wbb -> v_wbb\n"
        voter += "PROTOCOL v_wbb: [[verifyVote],[wait]"
        for cand_id in range(1, self._cand_count + 1):
            for tr_id in range(1, self._voter_count + 1):
                voter += f",[aID_WBB{tr_id}{cand_id}true,aID_WBB{tr_id}{cand_id}false]"
        voter += "]\n"
        for cand_id in range(1, self._cand_count + 1):
            voter += f"shared showTrackerFor{cand_id}_aID: v_wbb -> v_show [v_show_aID={cand_id}]\n"
        voter += "shared punish_aID: v_show -> v_show\n"
        voter += "shared no_punish_aID: v_show -> v_show\n"
        return voter

    def _generate_coercer(self):
        coercer = "Agent Coercer[1]:\n"
        coercer += "init: c_init\n"
        for voter_id in range(1, self._voter_count + 1):
            coercer += f"shared leave_Voter{voter_id}: c_init -> c_init [req{voter_id}=0]\n"
            coercer += f"shared punish_Voter{voter_id}: c_init -> c_init [pun{voter_id}=true]\n"
            coercer += f"shared no_punish_Voter{voter_id}: c_init -> c_init [pun{voter_id}=false]\n"
            for cand_id in range(1, self._cand_count + 1):
                coercer += f"shared requestVoteFor{cand_id}_Voter{voter_id}: c_init -> c_init [req{voter_id}={cand_id}]\n"
                coercer += f"shared showTrackerFor{cand_id}_Voter{voter_id}: c_init -> c_init [v{voter_id}_show={cand_id}]\n"
                coercer += f"shared coercerWBB{voter_id}{cand_id}true: c_init -> c_init [t{voter_id}_c={cand_id}]\n"
                coercer += f"shared coercerWBB{voter_id}{cand_id}false: c_init -> c_init\n"
        coercer += "PROTOCOL c_init: ["
        for voter_id in range(1, self._voter_count + 1):
            coercer += f"[leave_Voter{voter_id}],[punish_Voter{voter_id}],[no_punish_Voter{voter_id}],"
            for cand_id in range(1, self._cand_count + 1):
                coercer += f"[requestVoteFor{cand_id}_Voter{voter_id}],"
            coercer += "["
            for cand_id in range(1, self._cand_count + 1):
                coercer += f"showTrackerFor{cand_id}_Voter{voter_id},"
            coercer = coercer.rstrip(",")
            coercer += "],"
            for cand_id in range(1, self._cand_count + 1):
                coercer += f"[coercerWBB{voter_id}{cand_id}true,coercerWBB{voter_id}{cand_id}false],"
        coercer = coercer.rstrip(",")
        coercer += "]\n"
        return coercer

    def _generate_reduction(self):
        reduction = "REDUCTION: [pun1]\n"
        return reduction

    def _generate_persistent(self):
        persistent = "PERSISTENT: ["
        for voter_id in range(1, self._voter_count + 1):
            persistent += f"v_Voter{voter_id}, wbb_t{voter_id}, t{voter_id}, "
        persistent = persistent.rstrip(" ,")
        persistent += "]\n"
        return persistent


if __name__ == "__main__":
    teller_count = int(input("Teller Count: "))
    voter_count = int(input("Voter Count: "))
    cand_count = int(input("Candidates Count: "))
    selene_model_generator = SeleneModelGenerator(teller_count, voter_count, cand_count)
    model = selene_model_generator.generate()
    file = open(f"Selene_{teller_count}_{voter_count}_{cand_count}.txt", "w")
    file.write(model)
    file.close()
