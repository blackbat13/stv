from atl.atl_ir_model import ATLIrModel


class SLIr(ATLIrModel):
    def __init__(self, number_of_agents):
        super().__init__(number_of_agents)

    def pre(self, quant_pref, bind_pref, states, actions):
        if quant_pref is None:
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
        if quant_pref[0][0] == "Exist":
            result = set()
            for action in self.agents_actions:
                result.update(self.update(bind_pref, actions, quant_pref[0][1], action))
            return result
        else:
            result = set()
            for action in self.agents_actions:
                result.intersection_update(self.update(bind_pref, actions, quant_pref[0][1], action))
            return result

    def update(self, bind, actions, var, action):
        new_actions = actions[:]
        for agent_id in range(0, self.number_of_agents):
            if (var, agent_id) in bind:
                new_actions[agent_id] = action
            else:
                new_actions[agent_id] = actions[agent_id]  # don't need that

        return new_actions
