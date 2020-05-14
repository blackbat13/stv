from stv.tools import StringTools
from stv.models.asynchronous import LocalModel, GlobalModel
from stv.models.asynchronous.parser.local_model_parser import LocalModelParser
from typing import List


class GlobalModelParser:
    """
    Parser for the global model.
    """

    def __init__(self):
        pass

    def parse(self, file_name: str) -> GlobalModel:
        """
        Parse model from the file.
        :param file_name: Name of the file.
        :return: None.
        """
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()
        local_models = []
        reduction = []
        i = 0
        while i < len(lines):
            if StringTools.is_blank_line(lines[i]):
                i += 1
                continue

            if self._is_agent_header(lines[i]):
                line_from = i
                i = self._find_agent_end(lines, i + 1)
                line_to = i
                agent_max = self._parse_agent_max(lines[line_from])
                for agent_id in range(1, agent_max + 1):
                    local_model = LocalModelParser().parse(len(local_models), "".join(lines[line_from:line_to]),
                                                           agent_id)
                    local_models.append(local_model)
            elif self._is_reduction_header(lines[i]):
                reduction = self._parse_reduction(lines[i])
                i += 1

        return GlobalModel(local_models, reduction)

    @staticmethod
    def _is_agent_header(line: str):
        return line[0:5] == "Agent"

    @staticmethod
    def _is_reduction_header(line: str):
        return line[0:9] == "REDUCTION"

    @staticmethod
    def _parse_reduction(line: str) -> List[str]:
        line = line.split(":")[1]
        line = line.strip().strip("[").strip("]")
        red = []
        for element in line.split(","):
            red.append(element.strip())
        return red

    @staticmethod
    def _parse_agent_max(line: str):
        if len(line.split("[")) > 1:
            return int(line.split("[")[1].split("]")[0])
        return 1

    def _find_agent_end(self, lines: List[str], line_index: int):
        while line_index < len(lines) and not StringTools.is_blank_line(
                lines[line_index]) and not self._is_agent_header(lines[line_index]):
            line_index += 1
        return line_index
