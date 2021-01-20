from stv.logics.atl import ATLIrModel, ATLirModel, Transition
# from stv.logics.atl.mv import MvATLirModel
from stv.logics.sl import SLIr
from typing import List, Set, Dict
import ast
import itertools
import json


class SimpleModel:
    def __init__(self, no_agents: int):
        self._no_states: int = 0
        self._no_transitions: int = 0
        self._first_state_id: int = 0
        self._no_agents: int = no_agents
        self._graph: List[List[Transition]] = []
        self._pre_image: List[List[int]] = []
        self._epistemic_classes: List[List[Set[int]]] = []
        self._epistemic_class_membership: List[List[int]] = []
        self._states: List[{}] = []
        self._coalition = [0]
        for _ in range(0, self._no_agents):
            self._epistemic_classes.append([])
            self._epistemic_class_membership.append([])

    def set_coalition(self, coalition: List[int]):
        self._coalition = coalition

    @property
    def graph(self) -> List[List[Transition]]:
        return self._graph

    @graph.setter
    def graph(self, value: List[List[Transition]]):
        self._graph = value

    @property
    def no_states(self) -> int:
        return self._no_states

    @property
    def no_transitions(self) -> int:
        return self._no_transitions

    @property
    def first_state_id(self) -> int:
        return self._first_state_id

    @property
    def no_agents(self) -> int:
        return self._no_agents

    @property
    def pre_image(self) -> List[List[int]]:
        return self._pre_image

    @property
    def epistemic_classes(self) -> List[List[Set[int]]]:
        return self._epistemic_classes

    @property
    def epistemic_class_membership(self) -> List[List[int]]:
        return self._epistemic_class_membership

    @property
    def states(self) -> List:
        return self._states

    @states.setter
    def states(self, value: List):
        self._states = value

    def has_transition(self, transition: Transition):
        for l in self._graph:
            if transition in l:
                return True

        return False

    def add_transition(self, from_state_id: int, to_state_id: int, actions: List[str]) -> None:
        """
        Adds transition between to states in the model
        :param from_state_id:
        :param to_state_id:
        :param actions: List of actions for the transition
        :return: None
        """
        self.resize_to_state(max(from_state_id, to_state_id))
        # if self.is_unique_transition(Transition(to_state_id, actions), from_state_id):
        self._graph[from_state_id].append(Transition(to_state_id, actions))
        self._pre_image[to_state_id].append(from_state_id)
        self._no_transitions += 1

    def is_unique_transition(self, transition: Transition, state_id: int) -> bool:
        for tr in self._graph[state_id]:
            if tr.actions == transition.actions and tr.next_state == transition.next_state:
                return False

        return True

    def resize_to_state(self, state_id: int) -> None:
        """
        Resize used structures to hold more states
        :param state_id:
        :return:
        """
        while len(self._graph) <= state_id:
            self._graph.append([])
            self._pre_image.append([])

        for agent_number in range(0, self._no_agents):
            while len(self._epistemic_class_membership[agent_number]) <= state_id:
                self._epistemic_class_membership[agent_number].append(-1)

        self._no_states = max(self._no_states, state_id + 1)

    def add_epistemic_relation(self, state_id_1: int, state_id_2: int, agent_number: int) -> None:
        """
        Adds epistemic relation between two states for the given agent to the model
        :param state_id_1:
        :param state_id_2:
        :param agent_number:
        :return: None
        """
        if self._epistemic_class_membership[agent_number][state_id_1] != -1:
            self._epistemic_classes[agent_number][self._epistemic_class_membership[agent_number][state_id_1]].add(
                state_id_2)
            self._epistemic_class_membership[agent_number][state_id_2] = self._epistemic_class_membership[agent_number][
                state_id_1]
        elif self._epistemic_class_membership[agent_number][state_id_2] != -1:
            self._epistemic_classes[agent_number][self._epistemic_class_membership[agent_number][state_id_2]].add(
                state_id_1)
            self._epistemic_class_membership[agent_number][state_id_1] = self._epistemic_class_membership[agent_number][
                state_id_2]
        else:
            self._epistemic_classes[agent_number].append({state_id_1, state_id_2})
            self._epistemic_class_membership[agent_number][state_id_1] = len(
                self._epistemic_class_membership[agent_number]) - 1
            self._epistemic_class_membership[agent_number][state_id_2] = self._epistemic_class_membership[agent_number][
                state_id_1]

    def add_epistemic_class(self, agent_id: int, epistemic_class: Set[int]) -> None:
        """
        Adds epistemic class to the model
        :param agent_id: Agent id for which epistemic class is specified
        :param epistemic_class: Set of states ids in the epistemic class
        :return: None
        """
        self._epistemic_classes[agent_id].append(epistemic_class)
        epistemic_class_number = len(self._epistemic_classes[agent_id]) - 1
        for state in epistemic_class:
            self._epistemic_class_membership[agent_id][state] = epistemic_class_number

    def epistemic_class_for_state(self, state_id: int, agent_id: int) -> Set[int]:
        """
        Returns a set of states ids in the epistemic class of a given state for a given agent
        :param state_id:
        :param agent_id:
        :return: Set of states ids in the epistemic class
        """
        if self._epistemic_class_membership[agent_id][state_id] == -1:
            return {state_id}

        return self._epistemic_classes[agent_id][self._epistemic_class_membership[agent_id][state_id]]

    def epistemic_class_for_state_and_coalition(self, state_id: int, coalition: List[int]) -> Set[int]:
        """
        Returns a set of states ids in the epistemic class of a given state for a given coalition
        :param state_id:
        :param coalition: List of agents ids
        :return: Set of states ids in the epistemic class
        """
        epistemic_class = set()
        for agent_number in coalition:
            if self._epistemic_class_membership[agent_number][state_id] == -1:
                epistemic_class.add(state_id)
            else:
                epistemic_class.update(
                    self._epistemic_classes[agent_number][self._epistemic_class_membership[agent_number][state_id]])

        return epistemic_class

    def get_possible_strategies(self, state_id: int) -> List[tuple]:
        """
        Returns a list of possible strategies in a state
        :param state_id:
        :return: List of possible strategies
        """
        possible_actions = set()
        for transition in self._graph[state_id]:
            possible_actions.add(tuple(transition.actions))

        return list(possible_actions)

    def get_possible_strategies_for_set(self, states: List[int]) -> List[List]:
        """
        Returns a list of possible strategies for a set of states
        :param states:
        :return:
        """
        possible_actions = []
        for state in states:
            possible_actions.append(self.get_possible_strategies(state))

        strategies = []
        for pr in itertools.product(*possible_actions):
            strat = []

            for i in range(len(pr)):
                strat.append(pr[i])

            strategies.append(strat)

        return strategies

    def get_possible_strategies_for_coalition(self, state_id: int, coalition: List[int]) -> List[tuple]:
        """
        Returns a list of possible strategies for given coalition in a given state.
        Order of actions in a strategy is the same as order of agents in the coalition.
        :param state_id:
        :param coalition: list of agents ids
        :return: List of possible strategies
        """
        possible_actions = set()
        for transition in self._graph[state_id]:
            actions = []
            for agent_id in coalition:
                actions.append(transition.actions[agent_id])
            possible_actions.add(tuple(actions))

        return list(possible_actions)

    def to_atl_perfect(self, actions) -> ATLIrModel:
        """
        Creates Alternating-Time Temporal Logic model with perfect information
        :param actions:
        :return: ATLIr model
        """
        atl_model = ATLIrModel(self._no_agents)
        atl_model = self._copy_model(atl_model, actions, epistemic=False)
        return atl_model

    def to_atl_imperfect(self, actions) -> ATLirModel:
        """
        Creates Alternating-Time Temporal Logic model with imperfect information
        :param actions:
        :return: ATLir model
        """
        atl_model = ATLirModel(self._no_agents)
        atl_model = self._copy_model(atl_model, actions, epistemic=True)
        return atl_model

    def to_mvatl_imperfect(self, actions, lattice):
        """
        Creates Multi-Valued Alternating-Time Temporal Logic model with imperfect information
        :param actions:
        :param lattice:
        :return: MvATLir model
        """
        mvatl_model = MvATLirModel(self._no_agents, lattice)
        mvatl_model = self._copy_model(mvatl_model, actions, epistemic=True)
        return mvatl_model

    def to_sl_perfect(self, actions) -> SLIr:
        """
        Creates Strategy Logic model with perfect information
        :param actions:
        :return: SLIr model
        """
        sl_model = SLIr(self._no_agents)
        sl_model = self._copy_model(sl_model, actions, epistemic=False)
        return sl_model

    def _copy_model(self, model, actions, epistemic: bool):
        model = self._add_actions_to_model(actions, model)
        model = self._add_transitions_to_model(model)
        if epistemic:
            model = self._add_epistemic_classes_to_model(model)
        model.states = self._states
        return model

    def _add_actions_to_model(self, actions, model):
        for i in range(0, len(actions)):
            for action in actions[i]:
                model.add_action(i, action)

        return model

    def _add_transitions_to_model(self, model):
        for state_id in range(0, len(self._graph)):
            for transition in self._graph[state_id]:
                model.add_transition(state_id, transition.next_state, transition.actions)

        return model

    def _add_epistemic_classes_to_model(self, model):
        for i in range(0, len(self._epistemic_classes)):
            for epistemic_class in self._epistemic_classes[i]:
                model.add_epistemic_class(i, epistemic_class)

        return model

    def to_subjective(self, coalition: List[int]) -> None:
        """
        Converts model to subjective semantics for ATLir
        Adds one more state to the model and marks it as the initial state
        :param coalition: list of agent ids for which model should be converted
        :return: None
        """
        first_state_epistemic_class = self.epistemic_class_for_state_and_coalition(0, coalition)
        state_id = len(self._states)
        actions = []
        for _ in range(0, self._no_agents):
            actions.append('Wait')
        for epistemic_state_id in first_state_epistemic_class:
            self.add_transition(state_id, epistemic_state_id, actions)

        self._first_state_id = state_id
        self._states.append(self._states[0])

    def simulate(self, agent_number: int) -> None:
        print("----SIMULATION START-----")
        current_state = 0
        while True:
            print()
            self.simulate_print_current_state(current_state)
            self.simulate_print_epistemic_states(current_state, agent_number)
            if len(self._graph[current_state]) == 0:
                break

            self.simulate_print_transitions(current_state)
            choice = int(input("Choose transition="))
            if choice == -1:
                break

            current_state = self._graph[current_state][choice].next_state

        print("----SIMULATION END-----")

    def simulate_print_current_state(self, current_state: int) -> None:
        print("Current state:")
        print(self._states[current_state])

    def simulate_print_epistemic_states(self, current_state: int, agent_number: int) -> None:
        print("Epistemic states:")
        for state in self.epistemic_class_for_state(current_state, agent_number):
            print(self._states[state])

    def simulate_print_transitions(self, current_state: int) -> None:
        print('Transitions:')
        i = 0
        for transition in self._graph[current_state]:
            print(str(i) + ":", transition.to_str())
            i += 1

    def dump(self) -> str:
        result = ""
        result += f"{self._no_states}\n"
        result += f"{self._no_agents}\n"
        result += self.dump_states()
        result += self.dump_transitions()
        result += self.dump_epistemic_classes()
        return result

    def dump_states(self) -> str:
        result = ""
        for state in self._states:
            result += f"{json.dumps(state)}\n"

        return result

    def dump_transitions(self) -> str:
        result = f"{self._no_transitions}\n"
        for state_id in range(0, self._no_states):
            for transition in self._graph[state_id]:
                result += f"{state_id} {transition.next_state} {json.dumps(transition.actions)}\n"

        return result

    def dump_epistemic_classes(self) -> str:
        result = ""
        for agent_id in range(0, self._no_agents):
            result += f"{len(self._epistemic_classes[agent_id])}\n"
            for epistemic_class in self._epistemic_classes[agent_id]:
                result += f"{len(epistemic_class)}"
                for state_id in epistemic_class:
                    result += f" {state_id}"
                result += "\n"

        return result

    def js_dump_model(self, winning: List = [], epistemic: bool = True, asynchronous: bool = False, reduced_model = None) -> str:
        nodes = self.fill_nodes_model(winning, reduced_model)
        links = self.fill_links_model(epistemic, asynchronous, reduced_model)
        return json.dumps({"nodes": nodes, "links": links})

    def fill_nodes_model(self, winning: List = [], reduced_model = None) -> List[hash]:
        nodes = []
        state_id = 0
        for state in self.states:
            nodes.append({"T": state, "id": state_id, "bgn": 0})
            if reduced_model is not None and state in reduced_model.states:
                nodes[state_id]["reduced"] = 1

            state_id += 1

        for state_id in self.epistemic_class_for_state(0, 0):
            nodes[state_id]["bgn"] = 1

        for state_id in winning:
            nodes[state_id]["win"] = 1

        return nodes

    def fill_links_model(self, epistemic: bool, asynchronous: bool, reduced_model = None) -> List[hash]:
        links = []
        transition_id = 0
        for state_id in range(0, self._no_states):
            for transition in self._graph[state_id]:
                # if transition.next_state == state_id:
                #     continue

                actions = transition.actions

                if asynchronous:
                    for act in actions:
                        if len(act) > 0:
                            actions = act
                            break

                links.append(
                    {"id": transition_id, "source": state_id, "target": transition.next_state, "T": actions,
                     "str": 0})

                if reduced_model is not None:
                    state_from = self._states[state_id]
                    state_to = self._states[transition.next_state]
                    if state_from in reduced_model.states and state_to in reduced_model.states:
                        red_state_from_id = reduced_model._states.index(state_from)
                        red_state_to_id = reduced_model._states.index(state_to)
                        for tr in reduced_model.graph[red_state_from_id]:
                            if tr.next_state == red_state_to_id and tr.actions == transition.actions:
                                links[transition_id]["reduced"] = 1
                                break

                transition_id += 1

        if epistemic:
            links += self._create_epistemic_links(transition_id)

        return links

    def js_dump_strategy_objective(self, strategy) -> str:
        nodes = self.fill_nodes_strategy_objective()
        links = self.fill_links_strategy_objective(nodes, strategy)
        return json.dumps({"nodes": nodes, "links": links})

    def fill_nodes_strategy_objective(self) -> List[hash]:
        nodes = []
        state_id = 0
        for state in self._states:
            nodes.append({"T": state, "id": state_id, "str": 0})
            state_id += 1

        return nodes

    def fill_links_strategy_objective(self, nodes, strategy) -> List[hash]:
        links = []
        transition_id = 0
        for state_id in range(0, self._no_states):
            for transition in self._graph[state_id]:
                # if transition.next_state == state_id:
                #     continue

                self.js_dump_transition(transition, state_id, strategy, links, nodes, transition_id)
                transition_id += 1

        links += self._create_epistemic_links(transition_id)

        return links

    def js_dump_strategy_subjective(self, strategy) -> str:
        nodes = self.fill_nodes_strategy_subjective()
        links = self.fill_links_strategy_subjective(nodes, strategy)
        return json.dumps({"nodes": nodes, "links": links})

    def fill_nodes_strategy_subjective(self) -> List[hash]:
        nodes = []
        state_id = 0
        for state in self._states:
            if state_id != self._first_state_id:
                nodes.append({"T": state, "id": state_id, "str": 0})
            state_id += 1

        return nodes

    def fill_links_strategy_subjective(self, nodes, strategy) -> List[hash]:
        links = []
        transition_id: int = 0
        for state_id in range(0, self._no_states):
            if state_id == self._first_state_id:
                continue
            for transition in self._graph[state_id]:
                if transition.next_state == state_id:
                    continue

                self.js_dump_transition(transition, state_id, strategy, links, nodes, transition_id)
                transition_id += 1

        links += self._create_epistemic_links(transition_id)

        return links

    def _create_epistemic_links(self, link_id: int) -> list:
        links = []
        for agent_id in self._coalition:  # range(self.no_agents):
            for state_id_1 in range(self.no_states):
                if self._epistemic_class_membership[agent_id][state_id_1] == -1:
                    continue
                for state_id_2 in range(state_id_1 + 1, self.no_states):
                    if self._epistemic_class_membership[agent_id][state_id_1] == \
                            self._epistemic_class_membership[agent_id][state_id_2]:
                        links.append(
                            {'id': link_id, "source": state_id_1, "target": state_id_2, "T": agent_id, "str": 3})
                        link_id += 1
        return links

    def js_dump_transition(self, transition, state_id, strategy, links, nodes, transition_id) -> None:
        actions = []
        ln = 0
        if strategy[state_id] is not None:
            ln = len(strategy[state_id])
        for agent_id in self._coalition:
            actions.append(transition.actions[agent_id])
        # for i in range(0, ln):
        #     actions.append(transition.actions[i])
        # print(strategy[state_id], actions, strategy[state_id] == actions)
        if strategy[state_id] == actions:
            links.append(
                {"id": transition_id, "source": state_id, "target": transition.next_state, "T": transition.actions,
                 "str": 1})
            nodes[state_id]["str"] = 1
            nodes[transition.next_state]["str"] = 1
        else:
            links.append(
                {"id": transition_id, "source": state_id, "target": transition.next_state, "T": transition.actions,
                 "str": 0})

    @staticmethod
    def load_from_json(json_str: str, imperfect: bool, DEBUG: bool = False) -> [int]:
        json_obj = json.loads(json_str)
        label = ast.literal_eval(json_obj['links'][0]['label'])
        no_agents = len(label)
        simple_model = SimpleModel(no_agents)
        no_states = len(json_obj['nodes'])
        simple_model.states = [{} for _ in range(no_states)]
        simple_model._no_states = no_states
        simple_model.resize_to_state(no_states - 1)
        actions = [set() for _ in range(no_agents)]
        for node in json_obj['nodes']:
            if DEBUG:
                print(node)
            id = int(node['id'])
            label = node['label']
            props = node['props']
            simple_model.states[id] = {'label': label, 'props': props}

        for transition in json_obj['links']:
            if DEBUG:
                print(transition)
            source = transition['source']
            target = transition['target']
            label = ast.literal_eval(transition['label'])
            for agent_id in range(no_agents):
                actions[agent_id].add(label[agent_id])
            simple_model.add_transition(from_state_id=source, to_state_id=target, actions=label)

        if imperfect:
            observables = json_obj['observables']
            for agent_id in range(no_agents):
                epistemic_dict = dict()
                state_id = -1
                for state in simple_model.states:
                    state_id += 1
                    props = set()
                    for prop in state['props']:
                        if prop in observables[agent_id]:
                            props.add(prop)
                    if str(props) in epistemic_dict:
                        epistemic_dict[str(props)].add(state_id)
                    else:
                        epistemic_dict[str(props)] = {state_id}
                for epistemic_class in epistemic_dict.values():
                    simple_model.add_epistemic_class(agent_id, epistemic_class)

        formula = json_obj['formula']['form']
        coalition = formula['group']
        formula = formula['operand1']['form']
        result = []
        if formula['op'] == 'F':
            formula = formula['operand1']
            expression = formula
            winning_states = set()
            for state_id in range(len(simple_model.states)):
                state = simple_model.states[state_id]
                if simple_model.evaluate_on_state(expression, state):
                    winning_states.add(state_id)

            if imperfect:
                atl_perfect = simple_model.to_atl_perfect(actions)
                result_p = atl_perfect.minimum_formula_many_agents(coalition, winning_states)

                atl_imperfect = simple_model.to_atl_imperfect(actions)
                result_ip = atl_imperfect.minimum_formula_many_agents(coalition, winning_states)

                result = result_ip.intersection(result_p)
            else:
                atl_perfect = simple_model.to_atl_perfect(actions)
                result = atl_perfect.minimum_formula_many_agents(coalition, winning_states)

        elif formula['op'] == 'G':
            formula = formula['operand1']
            expression = formula
            winning_states = set()
            for state_id in range(len(simple_model.states)):
                state = simple_model.states[state_id]
                if simple_model.evaluate_on_state(expression, state):
                    winning_states.add(state_id)

            if imperfect:
                atl_perfect = simple_model.to_atl_perfect(actions)
                result_p = atl_perfect.maximum_formula_many_agents(coalition, winning_states)

                atl_imperfect = simple_model.to_atl_imperfect(actions)
                result_ip = atl_imperfect.maximum_formula_many_agents(coalition, winning_states)

                result = result_ip.intersection(result_p)
            else:
                atl_perfect = simple_model.to_atl_perfect(actions)
                result = atl_perfect.maximum_formula_many_agents(coalition, winning_states)

        return result

    def evaluate_on_state(self, expression, state) -> bool:
        if 'op' not in expression:
            expression = expression['form']

        operator = expression['op']
        if operator[0] == 'p':
            id = int(operator[1:])
            return id in state['props']

        if operator == 'and':
            return self.evaluate_on_state(expression['operand1'], state) and self.evaluate_on_state(
                expression['operand2'], state)

        if operator == 'or':
            return self.evaluate_on_state(expression['operand1'], state) or self.evaluate_on_state(
                expression['operand2'], state)

        if operator == 'not':
            return not self.evaluate_on_state(expression['operand1'], state)

    def join_to_sink(self, sink_states: Set[int], props: list):
        new_model, states_mapping, sink_id = self._join_states(sink_states, props)
        new_model = self._join_transitions(states_mapping, new_model, sink_id)
        new_model = self._join_epistemic_classes(states_mapping, new_model, sink_id)
        return new_model

    def _join_states(self, sink_states, props) -> (object, List[int], int):
        new_model: SimpleModel = SimpleModel(self._no_agents)
        states_mapping: List[int] = []
        new_id: int = 0
        sink_id: int = len(self._states) - len(sink_states)
        for i in range(0, len(self._states)):
            if i in sink_states:
                states_mapping.append(sink_id)
            else:
                states_mapping.append(new_id)
                new_id += 1
                new_model.states.append(self._states[i])

        new_model.states.append({'props': props})

        return new_model, states_mapping, sink_id

    def _join_transitions(self, states_mapping: List[int], new_model, sink_id: int):
        for state_id in range(0, len(self._graph)):
            if states_mapping[state_id] == sink_id:
                continue
            for transition in self._graph[state_id]:
                new_model.add_transition(states_mapping[state_id], states_mapping[transition.next_state],
                                         transition.actions)

        new_model.add_transition(sink_id, sink_id, ["-1" for _ in range(self.no_agents)])
        return new_model

    def _join_epistemic_classes(self, states_mapping: List[int], new_model, sink_id: int):
        for agent_id in range(0, len(self._epistemic_classes)):
            for epistemic_class in self._epistemic_classes[agent_id]:
                new_epistemic_class = set()
                for state_id in epistemic_class:
                    if states_mapping[state_id] != sink_id:
                        new_epistemic_class.add(states_mapping[state_id])
                new_model.add_epistemic_class(agent_id, new_epistemic_class)

        return new_model

    def get_partial_strategies(self, state_id: int, agent_id: int) -> Dict[str, List[Transition]]:
        result = dict()
        for transition in self.graph[state_id]:
            action = transition.actions[agent_id]
            if action in result:
                result[action].append(transition)
            else:
                result[action] = [transition]
        return result

    def group_by_epistemic_classes(self, states: List[int], agent_id: int) -> List[List[int]]:
        vis = [False for _ in range(len(states))]
        result = []
        for i in range(len(states)):
            if vis[i]:
                continue

            vis[i] = True
            state_id = states[i]
            result.append([state_id])
            epistemic_class_id = self.epistemic_class_membership[agent_id][state_id]
            for j in range(i + 1, len(states)):
                if vis[j]:
                    continue

                state2_id = states[j]
                epistemic_class2_id = self.epistemic_class_membership[agent_id][state2_id]
                if epistemic_class_id == epistemic_class2_id:
                    result[-1].append(state2_id)
                    vis[j] = True

        return result

    def check_bisimulation(self, sim_model, mapping: Dict[int, List[int]], coalition: List[int]) -> bool:
        # agent_id = self._coalition[0]
        agent_id = coalition[0]
        for epistemic_class in self.epistemic_classes[agent_id]:
            # print(epistemic_class)
            for state_id in epistemic_class:
                partial_strats = self.get_partial_strategies(state_id, agent_id)
                for action in partial_strats:
                    trans = partial_strats[action]
                    sim_states = mapping[state_id]
                    sim_groups = sim_model.group_by_epistemic_classes(sim_states, agent_id)
                    for sim_group in sim_groups:
                        sim_repr_id = sim_group[0]
                        sim_partial_strats = sim_model.get_partial_strategies(sim_repr_id, agent_id)
                        glob_ok = False
                        for sim_action in sim_partial_strats:
                            sim_trans = sim_partial_strats[sim_action]
                            ok = True
                            for sim_state_id in sim_group:
                                if not self.match(state_id, sim_state_id, sim_model, agent_id):
                                    ok = False
                                    break

                                if not self.simulepist(state_id, sim_state_id, sim_model, agent_id, mapping):
                                    ok = False
                                    break

                                if not self.simultrans(epistemic_class,
                                                       sim_model.epistemic_class_for_state(sim_state_id, agent_id),
                                                       mapping, trans, sim_trans):
                                    ok = False
                                    break

                            if ok:
                                glob_ok = True
                                break

                        if not glob_ok:
                            return False
        return True

    def match(self, state_id: int, sim_state_id: int, sim_model, agent_id: int) -> bool:
        # print(self.states[state_id]['Propositions'], sim_model.states[sim_state_id]['Propositions'])
        # print(self.states[state_id])
        return self.states[state_id]['Propositions'] == sim_model.states[sim_state_id]['Propositions']

    def simulepist(self, state_id: int, sim_state_id: int, sim_model, agent_id: int,
                   mapping: Dict[int, List[int]]) -> bool:
        # for each agent
        for sim_epistemic_state_id in sim_model.epistemic_class_for_state(sim_state_id, agent_id):
            ok = False
            for epistemic_state_id in self.epistemic_class_for_state(state_id, agent_id):
                if sim_epistemic_state_id in mapping[epistemic_state_id]:
                    ok = True
                    break

            if not ok:
                return False

        return True

    def simultrans(self, epistemic_class: Set[int], sim_epistemic_class: Set[int], mapping: Dict[int, List[int]],
                   trans: List[Transition], sim_trans: List[Transition]) -> bool:
        for state_id in epistemic_class:
            for sim_state_id in sim_epistemic_class:
                if sim_state_id not in mapping[state_id]:
                    continue

                for sim_transition in sim_trans:
                    sim_suc_id = sim_transition.next_state
                    ok = False
                    for transition in trans:
                        suc_id = transition.next_state
                        if sim_suc_id in mapping[suc_id]:
                            ok = True
                            break

                    if not ok:
                        return False

        return True

    @staticmethod
    def parse_mapping(file_name: str) -> (Dict[int, List[int]], List[int]):
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()
        result = dict()
        coalition = []

        for line in lines:
            if line[0:9] == "coalition":
                coalition = list(map(int, line.split(":")[1].split(",")))
                continue
            states_left, states_right = line.split("->")
            states_left = list(map(int, states_left.strip(" ").split(",")))
            states_right = list(map(int, states_right.strip(" ").split(",")))
            for state_id in states_left:
                result[state_id] = states_right[:]

        return result, coalition

    @staticmethod
    def parse_mapping_sets(file_name: str) -> (List[List[List[int]]], List[int]):
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()
        result = []
        coalition = []

        for line in lines:
            if line[0:9] == "coalition":
                coalition = list(map(int, line.split(":")[1].split(",")))
                continue
            states_left, states_right = line.split("->")
            states_left = list(map(int, states_left.strip(" ").split(",")))
            states_right = list(map(int, states_right.strip(" ").split(",")))
            result.append([states_left[:], states_right[:]])

        return result, coalition