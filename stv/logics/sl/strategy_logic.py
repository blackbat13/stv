from stv.logics.atl.atl_ir_model import ATLIrModel
from stv.tools.list_tools import ListTools


class SLIr(ATLIrModel):
    """
    Class for handling Strategy Logic with perfect information and imperfect recall
    """

    def __init__(self, number_of_agents):
        """
        Initializes class based on a number of agents
        :param number_of_agents: number of agents in the model
        """
        super().__init__(number_of_agents)
        self._strat_bind = dict()

    def verify(self, winning_states, quant_pref, bind_pref):
        current_states = set(winning_states)
        current_states_len = len(current_states)
        next_states = set(winning_states)
        next_current_len = -1
        all_quant_ids = set()
        self._strat_bind = dict()
        for el in bind_pref:
            all_quant_ids.add(el[1])
            self._strat_bind[el[0]] = el[1]

        while current_states_len != next_current_len:
            next_current_len = len(current_states)
            pre_states = self.get_pre_states(next_states)
            next_states = set(self.pre(quant_pref, 0, bind_pref, pre_states, next_states,
                                       ['' for _ in range(self.number_of_agents)], all_quant_ids))
            current_states.update(next_states)
            current_states_len = len(current_states)

        return current_states

    def get_pre_states(self, states):
        pre_states = set()
        for state_id in states:
            for transition in self.reverse_transitions[state_id]:
                pre_states.add(transition.next_state)
        return pre_states

    def pre(self, quant_pref, quant_pref_no, bind_pref, pre_states, states, actions, all_quant_ids):
        if quant_pref_no >= len(quant_pref):
            result = set()
            for state_id in pre_states:
                tran_ok = True
                for transition in self.transitions[state_id]:
                    correct = True
                    for id in all_quant_ids:
                        if transition.actions[id] != actions[id]:
                            correct = False
                            break

                    if correct and transition.next_state not in states:
                        tran_ok = False

                    if not tran_ok:
                        break

                if tran_ok:
                    result.add(state_id)

            return result
        if quant_pref[quant_pref_no][0] == "Exist":
            result = set()
            for action in self.agents_actions[self._strat_bind[quant_pref[quant_pref_no][1]]]:
                result.update(
                    self.pre(quant_pref, quant_pref_no + 1, bind_pref, pre_states, states,
                             self.update(actions, quant_pref[quant_pref_no][1], action), all_quant_ids))
            return result
        else:
            result = set()
            first = True

            print(self._strat_bind[quant_pref[quant_pref_no][1]])
            print(len(self.agents_actions))
            for action in self.agents_actions[self._strat_bind[quant_pref[quant_pref_no][1]]]:
                new_result = self.pre(quant_pref, quant_pref_no + 1, bind_pref, pre_states, states,
                                      self.update(actions, quant_pref[quant_pref_no][1], action),
                                      all_quant_ids)
                if first and len(new_result) > 0:
                    result.update(new_result)
                    first = False
                else:
                    result.intersection_update(new_result)

            return result

    def update(self, actions, var, action):
        new_actions = actions[:]
        new_actions[self._strat_bind[var]] = action

        return new_actions
