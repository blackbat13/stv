import itertools


class SeleneModelGenerator:
    def __init__(self, teller_count: int, voter_count: int, cand_count: int, formula: int):
        self._teller_count: int = teller_count
        self._voter_count: int = voter_count
        self._cand_count: int = cand_count
        self._formula: int = formula

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
        model += self._generate_coalition()
        return model

    def _generate_teller(self):
        teller = f"Agent Teller[{self._teller_count}]:\n"
        teller += "init: t_init\n"

        votes = [0 for _ in range(self._voter_count)]
        for voter_id in range(1, self._voter_count + 1):
            for cand_id in range(1, self._cand_count + 1):
                votes_copy = votes[:]
                votes_copy[voter_id - 1] = cand_id
                teller += f"shared sendVote_Voter{voter_id}_{cand_id}: t_init -> t_init{self._trackers_to_str(votes_copy)} [v_Voter{voter_id}={cand_id}]\n"
                teller += self._recursive_teller(votes_copy)

        votes = [[i + 1 for i in range(self._cand_count)] for _ in range(self._voter_count)]
        for vot in itertools.product(*votes):
            teller += f"shared finishVoting: t_init{self._trackers_to_str(vot)} -> t_finish{self._trackers_to_str(vot)}\n"
            teller += f"shared decryptVotes: t_finish{self._trackers_to_str(vot)} -> t_decrypt{self._trackers_to_str(vot)}\n"
            teller += f"shared sendToWBB{self._trackers_to_str(vot)}: t_decrypt{self._trackers_to_str(vot)} -> t_send\n"

        teller += "shared publishVotes: t_send -> t_publish\n"
        return teller

    def _recursive_teller(self, votes: list):
        result = ""
        for voter_id in range(1, self._voter_count + 1):
            if votes[voter_id - 1] != 0:
                continue
            for cand_id in range(1, self._cand_count + 1):
                votes_copy = votes[:]
                votes_copy[voter_id - 1] = cand_id
                result += f"shared sendVote_Voter{voter_id}_{cand_id}: t_init{self._trackers_to_str(votes)} -> t_init{self._trackers_to_str(votes_copy)} [v_Voter{voter_id}={cand_id}]\n"
                result += self._recursive_teller(votes_copy)
        return result

    def _generate_ea(self):
        ea = "Agent ElectionAuthority[1]:\n"
        ea += "init: ea_init\n"
        trackers = [i for i in range(1, self._voter_count + 1)]
        for perm in itertools.permutations(trackers):
            ea += f"shared generateTrackers{self._trackers_to_str(perm)}: ea_init -> ea_gen{self._trackers_to_str(perm)} {self._trackers_to_props(perm)}\n"
            ea += f"shared publishTrackers: ea_gen{self._trackers_to_str(perm)} -> ea_pub_t{self._trackers_to_str(perm)}\n"
            ea += f"shared startVoting: ea_pub_t{self._trackers_to_str(perm)} -> ea_start{self._trackers_to_str(perm)}\n"
            ea += f"shared finishVoting: ea_start{self._trackers_to_str(perm)} -> ea_finish{self._trackers_to_str(perm)}\n"
            ea += f"shared publishVotes: ea_finish{self._trackers_to_str(perm)} -> ea_pub_v{self._trackers_to_str(perm)} [published=true]\n"
            for v_id in range(1, self._voter_count + 1):
                ea += f"shared sendTracker_Voter{v_id}_{perm[v_id - 1]}: ea_pub_v{self._trackers_to_str(perm)} -> ea_pub_v{self._trackers_to_str(perm)} [t_Voter{v_id}={perm[v_id - 1]}]\n"
            ea += f"shared allTrackerSend: ea_pub_v{self._trackers_to_str(perm)} -> ea_send [end=True]\n"

        return ea

    def _generate_wbb(self):
        wbb = "Agent WBB[1]:\n"
        wbb += "init: wbb_init\n"
        trackers = [i for i in range(1, self._voter_count + 1)]
        votes = [[i + 1 for i in range(self._cand_count)] for _ in range(self._voter_count)]
        uniqe_tr = set()
        for perm in itertools.permutations(trackers):
            wbb += f"shared generateTrackers{self._trackers_to_str(perm)}: wbb_init -> wbb_gen{self._trackers_to_str(perm)} {self._trackers_to_props(list(perm))}\n"
            for vot in itertools.product(*votes):
                wbb += f"shared sendToWBB{self._trackers_to_str(vot)}: wbb_gen{self._trackers_to_str(perm)} -> wbb_send{self._tr_vote_comb_to_str(list(perm), list(vot))} {self._tr_vote_comb_to_props(list(perm), list(vot))}\n"
                for voter in range(1, self._voter_count + 1):
                    for candidate in range(1, self._cand_count + 1):
                        if vot[perm[voter - 1] - 1] == candidate:
                            uniqe_tr.add(f"shared coercerWBB_{voter}_{candidate}: wbb_send{self._tr_vote_comb_to_str(list(perm), list(vot))} -> wbb_send{self._tr_vote_comb_to_str(list(perm), list(vot))}\n")
                            for v_id in range(1, self._voter_count + 1):
                                uniqe_tr.add(f"shared Voter{v_id}_WBB_{voter}_{candidate}: wbb_send{self._tr_vote_comb_to_str(list(perm), list(vot))} -> wbb_send{self._tr_vote_comb_to_str(list(perm), list(vot))}\n")
        for tr in uniqe_tr:
            wbb += tr

        return wbb

    def _tr_vote_comb_to_str(self, trackers, votes):
        result = ""
        for i in range(len(trackers)):
            result += f"_{i + 1}_{votes[trackers[i] - 1]}"
        return result

    def _tr_vote_comb_to_props(self, trackers, votes):
        result = f"[wbb_t1={votes[trackers[0] - 1]}"
        for i in range(1, len(trackers)):
            result += f", wbb_t{i + 1}={votes[trackers[i] - 1]}"
        result += "]"
        return result

    def _trackers_to_str(self, trackers):
        result = ""
        for tr in trackers:
            result += f"_{tr}"
        return result

    def _trackers_to_props(self, trackers):
        result = f"[t1={trackers[0]}"
        for i in range(1, len(trackers)):
            result += f", t{i + 1}={trackers[i]}"
        result += "]"
        return result

    def _generate_voter(self):
        voter = f"Agent Voter[{self._voter_count}]:\n"
        voter += "init: v_init\n"

        for request in range(self._cand_count + 1):
            voter += f"shared requestVoteFor{request}_aID: v_init -> v_request_r{request} [req_aID={request}]\n"
            voter += f"shared startVoting: v_request_r{request} -> v_start_r{request}\n"
            voter += f"createCommitment: v_start_r{request} -> v_commit_r{request}\n"
            for vote in range(1, self._cand_count + 1):
                voter += f"fillVote{vote}: v_commit_r{request} -> v_fill_r{request}_v{vote} [v_aID={vote}]\n"
                voter += f"encryptVote: v_fill_r{request}_v{vote} -> v_encrypt_r{request}_v{vote}\n"
                voter += f"shared sendVote_aID_{vote}: v_encrypt_r{request}_v{vote} -> v_send_r{request}_v{vote}\n"
                voter += f"shared finishVoting: v_send_r{request}_v{vote} -> v_finish_r{request}_v{vote}\n"
                voter += f"shared publishVotes: v_finish_r{request}_v{vote} -> v_publish_r{request}_v{vote}\n"
                for false_term in range(self._voter_count + 1):
                    voter += f"computeFalseAlphaTerm_{false_term}: v_publish_r{request}_v{vote} -> v_false_a_r{request}_v{vote}_f{false_term} [false_a_aID={false_term}]\n"
                    voter += f"computeFalseTracker: v_false_a_r{request}_v{vote}_f{false_term} -> v_false_tr_r{request}_v{vote}_f{false_term} [false_tr_aID={false_term}]\n"
                    for tracker in range(1, self._voter_count + 1):
                        voter += f"shared sendTracker_aID_{tracker}: v_false_tr_r{request}_v{vote}_f{false_term} -> v_send_tr_r{request}_v{vote}_f{false_term}_t{tracker} [v_t_aID={tracker}]\n"
                        voter += f"shared allTrackerSend: v_send_tr_r{request}_v{vote}_f{false_term}_t{tracker} -> v_wbb_r{request}_v{vote}_f{false_term}_t{tracker}\n"
                        for wbb_tracker in range(1, self._voter_count + 1):
                            for wbb_vote in range(1, self._cand_count + 1):
                                voter += f"shared aID_WBB_{wbb_tracker}_{wbb_vote}: v_wbb_r{request}_v{vote}_f{false_term}_t{tracker} -> v_verif_r{request}_v{vote}_f{false_term}_t{tracker}_wt{wbb_tracker}_wv{wbb_vote}\n"
                                voter += f"verifyVote: v_verif_r{request}_v{vote}_f{false_term}_t{tracker}_wt{wbb_tracker}_wv{wbb_vote} -> v_show_r{request}_v{vote}_f{false_term}_t{tracker} [verify_aID={wbb_tracker == tracker and wbb_vote == vote}]\n"

                        if false_term != 0 and false_term != tracker:
                            voter += f"shared showTracker{false_term}_aID: v_show_r{request}_v{vote}_f{false_term}_t{tracker} -> v_punish\n"
                        voter += f"shared showTracker{tracker}_aID: v_show_r{request}_v{vote}_f{false_term}_t{tracker} -> v_punish\n"
        voter += f"shared punish_aID: v_punish -> v_end [v_pun_aID=True]\n"
        voter += f"shared not_punish_aID: v_punish -> v_end [v_pun_aID=False]\n"
        return voter

    def _recursive_coercer(self, req: list):
        result = ""
        for voter_id in range(1, self._voter_count + 1):
            if req[voter_id - 1] != -1:
                continue
            for cand_id in range(0, self._cand_count + 1):
                req_copy = req[:]
                req_copy[voter_id - 1] = cand_id
                result += f"shared requestVoteFor{cand_id}_Voter{voter_id}: c_req{self._trackers_to_str(req)} -> c_req{self._trackers_to_str(req_copy)} [c_req_Voter{voter_id}={cand_id}]\n"
                result += self._recursive_coercer(req_copy)
        return result

    def _recursive_coercer_wbb(self, wbb, req):
        result = ""
        for tracker_id in range(1, self._voter_count + 1):
            if wbb[tracker_id - 1] != 0:
                continue
            for cand_id in range(1, self._cand_count + 1):
                wbb_copy = wbb[:]
                wbb_copy[tracker_id - 1] = cand_id
                result += f"shared coercerWBB_{tracker_id}_{cand_id}: c_wbb{self._trackers_to_str(req)}{self._trackers_to_str(wbb)} -> c_wbb{self._trackers_to_str(req)}{self._trackers_to_str(wbb_copy)} [c_wbb_t{tracker_id}={cand_id}]\n"
                result += self._recursive_coercer_wbb(wbb_copy, req)

        return result

    def _generate_coercer(self):
        coercer = "Agent Coercer[1]:\n"
        coercer += "init: c_init\n"

        requests = [-1 for _ in range(self._voter_count)]
        for voter_id in range(1, self._voter_count + 1):
            for cand_id in range(0, self._cand_count + 1):
                req_copy = requests[:]
                req_copy[voter_id - 1] = cand_id
                coercer += f"shared requestVoteFor{cand_id}_Voter{voter_id}: c_init -> c_req{self._trackers_to_str(req_copy)} [c_req_Voter{voter_id}={cand_id}]\n"
                coercer += self._recursive_coercer(req_copy)

        requests = [[i for i in range(self._cand_count + 1)] for _ in range(self._voter_count)]
        for req in itertools.product(*requests):
            coercer += f"shared publishTrackers: c_req{self._trackers_to_str(req)} -> c_pubt{self._trackers_to_str(req)}\n"
            coercer += f"shared startVoting: c_pubt{self._trackers_to_str(req)} -> c_start{self._trackers_to_str(req)}\n"
            coercer += f"shared finishVoting: c_start{self._trackers_to_str(req)} -> c_finish{self._trackers_to_str(req)}\n"
            coercer += f"shared publishVotes: c_finish{self._trackers_to_str(req)} -> c_pubv{self._trackers_to_str(req)}\n"
            wbb = [0 for _ in range(self._voter_count)]
            for tracker_id in range(1, self._voter_count + 1):
                for cand_id in range(1, self._cand_count + 1):
                    wbb_copy = wbb[:]
                    wbb_copy[tracker_id - 1] = cand_id
                    coercer += f"shared coercerWBB_{tracker_id}_{cand_id}: c_pubv{self._trackers_to_str(req)} -> c_wbb{self._trackers_to_str(req)}{self._trackers_to_str(wbb_copy)} [c_wbb_t{tracker_id}={cand_id}]\n"
                    coercer += self._recursive_coercer_wbb(wbb_copy, req)

            wbb = [[i for i in range(self._cand_count + 1)] for _ in range(self._voter_count)]
            for w in itertools.product(*wbb):
                trackers = [0 for _ in range(self._voter_count)]
                for voter_id in range(1, self._voter_count + 1):
                    for tracker_id in range(1, self._voter_count + 1):
                        tr_copy = trackers[:]
                        tr_copy[voter_id - 1] = tracker_id
                        coercer += f"shared showTracker{tracker_id}_Voter{voter_id}: c_wbb{self._trackers_to_str(req)}{self._trackers_to_str(w)} -> c_show{self._trackers_to_str(req)}{self._trackers_to_str(w)}{self._trackers_to_str(tr_copy)} [c_voter{voter_id}_bad={req[voter_id - 1] != 0 and req[voter_id-1] != w[tr_copy[voter_id - 1] - 1]}, c_some_bad={tr_copy[voter_id - 1] in trackers}, c_vote_Voter{voter_id}={w[tr_copy[voter_id - 1] - 1]}]\n"
                        coercer += self._recursive_coercer_tr(tr_copy, req, w)

                trackers = [[i for i in range(1, self._voter_count + 1)] for _ in range(self._voter_count)]
                for tr in itertools.product(*trackers):
                    for voter_id in range(1, self._voter_count + 1):
                        coercer += f"shared punish_Voter{voter_id}: c_show{self._trackers_to_str(req)}{self._trackers_to_str(w)}{self._trackers_to_str(tr)} -> c_show{self._trackers_to_str(req)}{self._trackers_to_str(w)}{self._trackers_to_str(tr)} [c_pun_Voter{voter_id}=True]\n"
                        coercer += f"shared not_punish_Voter{voter_id}: c_show{self._trackers_to_str(req)}{self._trackers_to_str(w)}{self._trackers_to_str(tr)} -> c_show{self._trackers_to_str(req)}{self._trackers_to_str(w)}{self._trackers_to_str(tr)} [c_pun_Voter{voter_id}=False]\n"

        return coercer

    def _recursive_coercer_tr(self, tr, req, w):
        result = ""
        for voter_id in range(1, self._voter_count + 1):
            if tr[voter_id - 1] != 0:
                continue
            for tracker_id in range(1, self._voter_count + 1):
                tr_copy = tr[:]
                tr_copy[voter_id - 1] = tracker_id
                result += f"shared showTracker{tracker_id}_Voter{voter_id}: c_show{self._trackers_to_str(req)}{self._trackers_to_str(w)}{self._trackers_to_str(tr)} -> c_show{self._trackers_to_str(req)}{self._trackers_to_str(w)}{self._trackers_to_str(tr_copy)} [c_voter{voter_id}_bad={req[voter_id - 1] != 0 and req[voter_id-1] != w[tr_copy[voter_id - 1] - 1]}, c_some_bad={tr_copy[voter_id - 1] in tr}, c_vote_Voter{voter_id}={w[tr_copy[voter_id - 1] - 1]}]\n"
                result += self._recursive_coercer_tr(tr_copy, req, w)

        return result

    def _generate_reduction(self):
        if self._formula == 0:
            reduction = "REDUCTION: [c_pun_Voter1]\n"
        elif self._formula == 1:
            reduction = "REDUCTION: [v_Voter1, c_vote_Voter1]\n"
        elif self._formula == 2:
            reduction = "REDUCTION: [verify_Voter1]\n"
        elif self._formula == 3 or self._formula == 4:
            pass
        return reduction

    def _generate_persistent(self):
        if self._formula == 0:
            persistent = "PERSISTENT: [c_pun_Voter1]\n"
        elif self._formula == 1:
            persistent = "PERSISTENT: [v_Voter1, c_vote_Voter1]\n"
        elif self._formula == 2:
            persistent = "PERSISTENT: [verify_Voter1]\n"
        elif self._formula == 3 or self._formula == 4:
            pass
        return persistent

    def _generate_coalition(self):
        if self._formula == 2:
            coalition = "COALITION: [Voter1]\n"
        else:
            coalition = "COALITION: [Coercer1]\n"
        return coalition


if __name__ == "__main__":
    teller_count = int(input("Teller Count: "))
    voter_count = int(input("Voter Count: "))
    cand_count = int(input("Candidates Count: "))
    formula = int(input("Formula: "))
    selene_model_generator = SeleneModelGenerator(teller_count, voter_count, cand_count, formula)
    model = selene_model_generator.generate()
    file = open(f"Selene_{teller_count}_{voter_count}_{cand_count}_{formula}.txt", "w")
    file.write(model)
    file.close()
