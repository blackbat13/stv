from atl.atl_ir_model import ATLIrModel
from tools.array_tools import ArrayTools


class SLIr(ATLIrModel):
    def __init__(self, number_of_agents):
        super().__init__(number_of_agents)

    def verify(self, winning_states, quant_pref, bind_pref):
        current_states = set(winning_states)
        current_states_len = len(current_states)
        next_states = set(winning_states)
        next_current_len = -1
        while current_states_len != next_current_len:
            next_current_len = len(current_states)
            next_states = set(self.pre(quant_pref, 0, bind_pref, next_states,
                                       ArrayTools.create_value_array_of_size(self.number_of_agents, '')))
            current_states.update(next_states)
            current_states_len = len(current_states)
            print(current_states)

        return current_states

    def pre(self, quant_pref, quant_pref_no, bind_pref, states, actions):
        if quant_pref_no >= len(quant_pref):
            result = set()
            for state_id in range(0, self.number_of_states):
                for transition in self.transitions[state_id]:
                    if transition.next_state not in states:
                        continue
                    if transition.actions != actions:
                        continue

                    result.add(state_id)
                    break

            return result
        if quant_pref[quant_pref_no][0] == "Exist":
            result = set()
            for a_actions in self.agents_actions:
                for action in a_actions:
                    result.update(
                        self.pre(quant_pref, quant_pref_no + 1, bind_pref, states,
                                 self.update(bind_pref, actions, quant_pref[quant_pref_no][1], action)))
            #print(quant_pref_no, result)
            if len(result) > 0:
                print(actions, result)
            return result
        else:
            result = set()
            first = True
            print("new")
            for a_actions in self.agents_actions:
                for action in a_actions:
                    new_result = self.pre(quant_pref, quant_pref_no + 1, bind_pref, states,
                                          self.update(bind_pref, actions, quant_pref[quant_pref_no][1], action))
                    if first and len(new_result) > 0:
                        result.update(new_result)
                        first = False
                        print("all", new_result)
                    elif len(new_result) > 0:
                        print("all", new_result)
                        result.intersection_update(new_result)

            #print("res", result)
            return result

    def update(self, bind, actions, var, action):
        new_actions = actions[:]
        for agent_id in range(0, self.number_of_agents):
            if (var, agent_id) in bind:
                new_actions[agent_id] = action
            else:
                new_actions[agent_id] = actions[agent_id]  # don't need that

        # print(new_actions)
        return new_actions
