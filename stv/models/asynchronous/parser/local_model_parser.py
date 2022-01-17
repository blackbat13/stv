from stv.models.asynchronous import LocalTransition, LocalModel
from stv.models.asynchronous.parser.local_transition_parser import LocalTransitionParser
from typing import List, Dict, Set


class LocalModelParser:
    """
    Parser for the local model.
    """

    def __init__(self):
        pass

    def parse(self, agent_id: int, model_str: str, agent_no: int) -> LocalModel:
        """
        Parse model string.
        :param agent_id: Agent identifier.
        :param model_str: String representation of the model.
        :param agent_no: Agent number.
        :return: None.
        """
        lines: List[str] = model_str.splitlines()
        agent_name: str = self._parse_agent_name(lines[0], str(agent_no))
        init_state: str = lines[1].split(" ")[1]
        states: Dict[str, int] = {init_state: 0}
        protocol: List[List[str]] = []
        actions: Set[str] = set()
        transitions: List[List[LocalTransition]] = []
        state_num: int = 1
        transition_id: int = 0
        local: List[str] = []
        interface: List[str] = []

        for i in range(2, len(lines)):
            line = lines[i].strip()
            line = line.replace("aID", agent_name)
            line = line.replace("ID", str(agent_no))
            if self._is_protocol_line(line):
                protocol = self._parse_protocol(line)
                continue
            elif self._is_local_line(line):
                local = self._parse_local_line(line)
                continue
            elif self._is_interface_line(line):
                interface = self._parse_interface_line(line)
                continue

            local_transition = LocalTransitionParser().parse(line)
            local_transition.id = transition_id
            local_transition.agent_id = agent_id
            transition_id += 1
            if not local_transition.shared:
                local_transition.action += f"_{agent_name}"
                local_transition.prot_name = local_transition.action

            actions.add(local_transition.action)
            state_from = local_transition.state_from
            state_to = local_transition.state_to
            if state_from not in states:
                states[state_from] = state_num
                state_num += 1

            if state_to not in states:
                states[state_to] = state_num
                state_num += 1

            while len(transitions) <= states[state_from]:
                transitions.append([])

            transitions[states[state_from]].append(local_transition)

        while len(transitions) < len(states):
            transitions.append([])
        #
        # for tran in transitions:
        #     for tr in tran:
        #         print(tr.prot_name)
        return LocalModel(agent_id, agent_name, states, transitions, protocol, actions, interface, local)

    @staticmethod
    def _parse_agent_name(line: str, agent_no: str) -> str:
        if line.find(" ") != -1:
            line = line.split(" ")[1]
        if line.find("[") != -1:
            line = line.split("[")[0] + agent_no
        if line.find(":") != -1:
            line = line.split(":")[0]

        return line

    @staticmethod
    def _is_protocol_line(line: str) -> bool:
        return line[:8] == "PROTOCOL"

    @staticmethod
    def _is_local_line(line: str) -> bool:
        return line[:5] == "LOCAL"

    @staticmethod
    def _is_interface_line(line: str) -> bool:
        return line[:9] == "INTERFACE"

    def _parse_interface_line(self, line: str) -> List[str]:
        line = line.split(":")[1]
        line = line.strip().lstrip("[").rstrip("]")
        return list(map(str.strip, line.split(",")))

    def _parse_local_line(self, line: str) -> List[str]:
        line = line.split(":")[1]
        line = line.strip().lstrip("[").rstrip("]")
        return list(map(str.strip, line.split(",")))

    def _parse_protocol(self, line: str) -> (str, List[List[str]]):
        line = line.split(":")
        protocol = self._parse_protocol_list(line[1])
        return protocol

    @staticmethod
    def _parse_protocol_list(line: str) -> List[List[str]]:
        protocol = []
        line = line.strip().lstrip("[").rstrip("]")
        for arr in line.split("],"):
            arr = arr.strip().lstrip("[").rstrip("]")
            lst = []
            for element in arr.split(","):
                lst.append(element.strip())
            protocol.append(lst)
        return protocol
