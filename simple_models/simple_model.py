from typing import List, Set
from atl.atl_ir_model import ATLIrModel, ATLirModel
from atl.strategy_logic import SLIr
import json


class SimpleModel:
    class Transition:
        next_state: int = 0
        actions: List[str] = []

        def __init__(self, next_state: int, actions: List[str]):
            self.actions = actions[:]
            self.next_state = next_state

        def to_str(self):
            return f"Next state: {self.next_state}; Actions: {self.actions}"

    graph: List[List[Transition]] = []
    no_states = 0
    no_agents = 0
    no_transitions = 0
    epistemic_classes = []
    epistemic_class_membership = []
    states = []
    first_state_id = 0

    def __init__(self, no_agents: int):
        self.clear_all()
        self.no_agents = no_agents
        for _ in range(0, self.no_agents):
            self.epistemic_classes.append([])
            self.epistemic_class_membership.append([])

    def clear_all(self):
        self.graph = []
        self.no_states = 0
        self.no_agents = 0
        self.no_transitions = 0
        self.epistemic_classes = []
        self.epistemic_class_membership = []
        self.states = []

    def add_transition(self, from_state_id: int, to_state_id: int, actions: List[str]):
        """
        Adds transition between to states in the model

        Parameters
        ----------
        from_state_id: int
        to_state_id: int
        actions: [String]
        """
        self.resize_to_state(max(from_state_id, to_state_id))
        self.graph[from_state_id].append(self.Transition(to_state_id, actions))
        self.no_transitions += 1

    def resize_to_state(self, state_id: int):
        while len(self.graph) <= state_id:
            self.graph.append([])

        for agent_number in range(0, self.no_agents):
            while len(self.epistemic_class_membership[agent_number]) <= state_id:
                self.epistemic_class_membership[agent_number].append(-1)

        self.no_states = max(self.no_states, state_id + 1)

    def add_epistemic_relation(self, state_id_1: int, state_id_2: int, agent_number: int):
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

    def add_epistemic_class(self, agent_number: int, epistemic_class: Set[int]):
        self.epistemic_classes[agent_number].append(epistemic_class)
        epistemic_class_number = len(self.epistemic_classes[agent_number]) - 1
        for state in epistemic_class:
            self.epistemic_class_membership[agent_number][state] = epistemic_class_number

    def epistemic_class_for_state(self, state_id: int, agent_number: int) -> Set[int]:
        if self.epistemic_class_membership[agent_number][state_id] == -1:
            return {state_id}

        return self.epistemic_classes[agent_number][self.epistemic_class_membership[agent_number][state_id]]

    def epistemic_class_for_state_and_coalition(self, state_id: int, agents_numbers: list) -> Set[int]:
        epistemic_class = set()
        for agent_number in agents_numbers:
            if self.epistemic_class_membership[agent_number][state_id] == -1:
                epistemic_class.add(state_id)
            else:
                epistemic_class.update(
                    self.epistemic_classes[agent_number][self.epistemic_class_membership[agent_number][state_id]])

        return epistemic_class

    def get_possible_strategies(self, state_id: int) -> List[tuple]:
        possible_actions = set()
        for transition in self.graph[state_id]:
            possible_actions.add(tuple(transition.actions))

        return list(possible_actions)

    def get_possible_strategies_for_coalition(self, state_id: int, coalition: List[int]) -> List[tuple]:
        possible_actions = set()
        for transition in self.graph[state_id]:
            actions = []
            for agent_id in coalition:
                actions.append(transition.actions[agent_id])
            possible_actions.add(tuple(actions))

        return list(possible_actions)

    def to_atl_perfect(self, actions) -> ATLIrModel:
        atl_model = ATLIrModel(self.no_agents)
        for i in range(0, len(actions)):
            for action in actions[i]:
                atl_model.add_action(i, action)
        for state_id in range(0, len(self.graph)):
            for transition in self.graph[state_id]:
                atl_model.add_transition(state_id, transition.next_state, transition.actions)
        atl_model.states = self.states
        return atl_model

    def to_atl_imperfect(self, actions) -> ATLirModel:
        atl_model = ATLirModel(self.no_agents)
        for i in range(0, len(actions)):
            for action in actions[i]:
                atl_model.add_action(i, action)
        for state_id in range(0, len(self.graph)):
            for transition in self.graph[state_id]:
                atl_model.add_transition(state_id, transition.next_state, transition.actions)
        for i in range(0, len(self.epistemic_classes)):
            for epistemic_class in self.epistemic_classes[i]:
                atl_model.add_epistemic_class(i, epistemic_class)
        atl_model.states = self.states
        return atl_model

    def to_sl_perfect(self, actions) -> SLIr:
        sl_model = SLIr(self.no_agents)
        for i in range(0, len(actions)):
            for action in actions[i]:
                sl_model.add_action(i, action)
        for state_id in range(0, len(self.graph)):
            for transition in self.graph[state_id]:
                sl_model.add_transition(state_id, transition.next_state, transition.actions)
        sl_model.states = self.states
        return sl_model

    def to_subjective(self, coalition: List[int]) -> None:
        """
        Converts model to subjective semantics for ATLir
        Adds one more state to the model and marks it as the initial state
        :param coalition: list of agent ids for which model should be converted
        :return: None
        """
        first_state_epistemic_class = self.epistemic_class_for_state_and_coalition(0, coalition)
        state_id = len(self.states)
        actions = []
        for _ in range(0, self.no_agents):
            actions.append('Wait')
        for epistemic_state_id in first_state_epistemic_class:
            self.add_transition(state_id, epistemic_state_id, actions)

        self.first_state_id = state_id
        self.states.append(self.states[0])

    def simulate(self, agent_number: int) -> None:
        print("----SIMULATION START-----")
        current_state = 0
        while True:
            print()
            print("Current state:")
            print(self.states[current_state])
            print("Epistemic states:")
            for state in self.epistemic_class_for_state(current_state, agent_number):
                print(self.states[state])

            if len(self.graph[current_state]) == 0:
                break

            print('Transitions:')
            i = 0
            for transition in self.graph[current_state]:
                print(str(i) + ":", transition.to_str())
                i += 1

            choice = int(input("Choose transition="))
            if choice == -1:
                break

            current_state = self.graph[current_state][choice].next_state

        print("----SIMULATION END-----")

    def dump(self) -> str:
        result = ""
        result += f"{self.no_states}\n"
        result += f"{self.no_agents}\n"
        for state in self.states:
            result += f"{json.dumps(state)}\n"

        result += f"{self.no_transitions}\n"
        for state_id in range(0, self.no_states):
            for transition in self.graph[state_id]:
                result += f"{state_id} {transition.next_state} {json.dumps(transition.actions)}\n"

        for agent_id in range(0, self.no_agents):
            result += f"{len(self.epistemic_classes[agent_id])}\n"
            for epistemic_class in self.epistemic_classes[agent_id]:
                result += f"{len(epistemic_class)}"
                for state_id in epistemic_class:
                    result += f" {state_id}"
                result += "\n"

        return result

    def js_dump(self) -> str:
        nodes = []
        state_id = 0
        for state in self.states:
            nodes.append({"T": state, "id": state_id, "bgn": 0})
            state_id += 1

        for state_id in self.epistemic_class_for_state(0, 0):
            nodes[state_id]["bgn"] = 1

        links = []
        for state_id in range(0, self.no_states):
            for transition in self.graph[state_id]:
                if transition.next_state == state_id:
                    continue
                links.append({"source": state_id, "target": transition.next_state, "T": transition.actions, "str": 0})

        return json.dumps({"nodes": nodes, "links": links})

    def js_dump_strategy(self, strategy) -> str:
        nodes = []
        state_id = 0
        for state in self.states:
            nodes.append({"T": state, "id": state_id})
            state_id += 1

        links = []
        for state_id in range(0, self.no_states):
            for transition in self.graph[state_id]:
                if transition.next_state == state_id:
                    continue
                actions = []
                ln = 0
                if strategy[state_id] is not None:
                    ln = len(strategy[state_id])
                for i in range(0, ln):
                    actions.append(transition.actions[i])
                if strategy[state_id] == actions:
                    links.append(
                        {"source": state_id, "target": transition.next_state, "T": transition.actions, "str": 1})
                    nodes[state_id]["str"] = 1
                    nodes[transition.next_state]["str"] = 1
                else:
                    links.append(
                        {"source": state_id, "target": transition.next_state, "T": transition.actions, "str": 0})

        return json.dumps({"nodes": nodes, "links": links})

    def js_dump_strategy_subjective(self, strategy) -> str:
        nodes = []
        state_id = 0
        for state in self.states:
            if state_id != self.first_state_id:
                nodes.append({"T": state, "id": state_id})
            state_id += 1

        links = []
        for state_id in range(0, self.no_states):
            if state_id == self.first_state_id:
                continue
            for transition in self.graph[state_id]:
                if transition.next_state == state_id:
                    continue
                actions = []
                ln = 0
                if strategy[state_id] is not None:
                    ln = len(strategy[state_id])
                for i in range(0, ln):
                    actions.append(transition.actions[i])
                if strategy[state_id] == actions:
                    links.append(
                        {"source": state_id, "target": transition.next_state, "T": transition.actions, "str": 1})
                    nodes[state_id]["str"] = 1
                    nodes[transition.next_state]["str"] = 1
                else:
                    links.append(
                        {"source": state_id, "target": transition.next_state, "T": transition.actions, "str": 0})

        return json.dumps({"nodes": nodes, "links": links})
