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

    def verify(self, winning_states, quant_pref, bind_pref, all_quant_ids):
        current_states = set(winning_states)
        current_states_len = len(current_states)
        next_states = set(winning_states)
        next_current_len = -1
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
                    if transition.actions != actions:
                        for id in all_quant_ids:
                            if transition.actions[id] == actions[id]:
                                tran_ok = False
                                break
                        if not tran_ok:
                            break
                        continue

                    if transition.next_state not in states:
                        break

                    result.add(state_id)
                    tran_ok = False
                    break

                if tran_ok:
                    result.add(state_id)

            return result
        if quant_pref[quant_pref_no][0] == "Exist":
            result = set()
            # for a_actions in self.agents_actions:
            #     for action in a_actions:
            #         result.update(
            #             self.pre(quant_pref, quant_pref_no + 1, bind_pref, pre_states, states,
            #                      self.update(bind_pref, actions, quant_pref[quant_pref_no][1], action)))
            for action in self.agents_actions[quant_pref_no]:
                result.update(
                    self.pre(quant_pref, quant_pref_no + 1, bind_pref, pre_states, states,
                             self.update(bind_pref, actions, quant_pref[quant_pref_no][1], action), all_quant_ids))
            return result
        else:
            result = set()
            first = True
            # for a_actions in self.agents_actions:
            #     for action in a_actions:
            #         new_result = self.pre(quant_pref, quant_pref_no + 1, bind_pref, pre_states, states,
            #                               self.update(bind_pref, actions, quant_pref[quant_pref_no][1], action))
            #         if first and len(new_result) > 0:
            #             result.update(new_result)
            #             first = False
            #         elif len(new_result) > 0:
            #             result.intersection_update(new_result)

            for action in self.agents_actions[quant_pref_no]:
                new_result = self.pre(quant_pref, quant_pref_no + 1, bind_pref, pre_states, states,
                                      self.update(bind_pref, actions, quant_pref[quant_pref_no][1], action),
                                      all_quant_ids)
                if first and len(new_result) > 0:
                    result.update(new_result)
                    first = False
                elif len(new_result) > 0:
                    result.intersection_update(new_result)

            return result

    def update(self, bind, actions, var, action):
        new_actions = actions[:]
        for agent_id in range(0, self.number_of_agents):
            if (var, agent_id) in bind:
                new_actions[agent_id] = action
            else:
                new_actions[agent_id] = actions[agent_id]  # don't need that

        return new_actions
