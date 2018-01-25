class SimpleModel:
    graph = []
    no_states = 0
    no_agents = 0
    epistemic_classes = []
    epistemic_class_membership = []

    def __init__(self, no_agents):
        self.no_agents = no_agents
        for _ in range(0, self.no_agents):
            self.epistemic_classes.append([])
            self.epistemic_class_membership.append([])

    def add_transition(self, from_state_id, to_state_id, actions):
        """
        Adds transition between to states in the model

        Parameters
        ----------
        from_state_id: int
        to_state_id: int
        actions: [String]
        """
        self.resize_to_state(max(from_state_id, to_state_id))

        self.graph[from_state_id].append({'next_state': to_state_id, 'actions': actions})

    def resize_to_state(self, state_id):
        while len(self.graph) <= state_id:
            self.graph.append([])

        for agent_number in range(0, self.no_agents):
            while len(self.epistemic_class_membership[agent_number]) <= state_id:
                self.epistemic_class_membership[agent_number].append(-1)

        self.no_states = max(self.no_states, state_id+1)

    def add_epistemic_relation(self, state_id_1, state_id_2, agent_number):
        if self.epistemic_class_membership[agent_number][state_id_1] != -1:
            self.epistemic_classes[agent_number][self.epistemic_class_membership[agent_number][state_id_1]].append(
                state_id_2)
            self.epistemic_class_membership[agent_number][state_id_2] = self.epistemic_class_membership[agent_number][
                state_id_1]
        elif self.epistemic_class_membership[agent_number][state_id_2] != -1:
            self.epistemic_classes[agent_number][self.epistemic_class_membership[agent_number][state_id_2]].append(
                state_id_1)
            self.epistemic_class_membership[agent_number][state_id_1] = self.epistemic_class_membership[agent_number][
                state_id_2]
        else:
            self.epistemic_classes[agent_number].append([state_id_1, state_id_2])
            self.epistemic_class_membership[agent_number][state_id_1] = len(
                self.epistemic_class_membership[agent_number]) - 1
            self.epistemic_class_membership[agent_number][state_id_2] = self.epistemic_class_membership[agent_number][
                state_id_1]

    def add_epistemic_class(self, agent_number, epistemic_class):
        self.epistemic_classes[agent_number].append(epistemic_class)
        epistemic_class_number = len(self.epistemic_classes[agent_number]) - 1
        for state in epistemic_class:
            self.epistemic_class_membership[agent_number][state] = epistemic_class_number

    def epistemic_class_for_state(self, state_id, agent_number):
        if self.epistemic_class_membership[agent_number][state_id] == -1:
            return [state_id]

        return self.epistemic_classes[agent_number][self.epistemic_class_membership[agent_number][state_id]]
