from stv.models.asynchronous.global_model import LogicType
from stv.tools import StringTools
from stv.models.asynchronous import GlobalModel
from stv.models.asynchronous.parser.local_model_parser import LocalModelParser
from typing import List, Dict


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
        bounded_vars = []
        persistent = []
        coalition = []
        goal = []
        logicType = LogicType.ATL
        formula = ""
        show_epistemic = True
        semantics = "asynchronous"
        i = 0
        initial = {}
        while i < len(lines):
            # print(f"LOG: parsing line{i}")
            if StringTools.is_blank_line(lines[i]) or self._is_comment_line(lines[i]):
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
                reduction = self._parse_list(lines[i])
                i += 1
            elif self._is_bounded_vars_header(lines[i]):
                bounded_vars = self._parse_list(lines[i])
                i += 1
            elif self._is_persistent_header(lines[i]):
                persistent = self._parse_list(lines[i])
                i += 1
            elif self._is_coalition_header(lines[i]):
                coalition = self._parse_list(lines[i])
                i += 1
            elif self._is_goal_header(lines[i]):
                goal = self._parse_list(lines[i])
                i += 1
            elif self._is_logic_header(lines[i]):
                logicType = self._parse_logic(lines[i])
                i += 1
            elif self._is_formula_header(lines[i]):
                formula = self._parse_formula(lines[i])
                i += 1
            elif self._is_show_epistemic_header(lines[i]):
                show_epistemic = self._parse_show_epistemic(lines[i])
                i += 1
            elif self._is_semantics_header(lines[i]):
                semantics = self._parse_semantics(lines[i])
                i += 1
            elif self._is_initial_header(lines[i]):
                initial = self._parse_initial(lines[i])
                i += 1

        return GlobalModel(local_models, reduction, bounded_vars, persistent, coalition, goal, logicType, formula, show_epistemic,
                           semantics, initial)

    @staticmethod
    def _is_show_epistemic_header(line: str):
        return line[0:14] == "SHOW_EPISTEMIC"

    @staticmethod
    def _is_comment_line(line: str):
        return line[0] == "%"

    @staticmethod
    def _is_agent_header(line: str):
        return line[0:5] == "Agent"

    @staticmethod
    def _is_reduction_header(line: str):
        return line[0:9] == "REDUCTION"

    @staticmethod
    def _is_bounded_vars_header(line: str):
        return line[0:12] == "BOUNDED_VARS"

    @staticmethod
    def _is_persistent_header(line: str):
        return line[0:10] == "PERSISTENT"

    @staticmethod
    def _is_coalition_header(line: str):
        return line[0:9] == "COALITION"

    @staticmethod
    def _is_goal_header(line: str):
        return line[0:4] == "GOAL"

    @staticmethod
    def _is_logic_header(line: str):
        return line[0:5] == "LOGIC"

    @staticmethod
    def _is_formula_header(line: str):
        return line[0:7] == "FORMULA"

    @staticmethod
    def _is_semantics_header(line: str):
        return line[0:9] == "SEMANTICS"

    @staticmethod
    def _is_initial_header(line: str):
        return line[0:7] == "INITIAL"

    @staticmethod
    def _parse_initial(line: str) -> Dict:
        props = {}
        _, line = line.split("[")
        line = line.split("]")[0]
        variables = line.split(",")
        for variable in variables:
            variable = variable.strip(" ")
            prop, val = variable.split("=")
            prop = prop.strip(" ")
            val = val.strip(" ")
            if val.casefold() == "true":
                val = True
            elif val.casefold() == "false":
                val = False
            else:
                try:
                    val = int(val)
                except ValueError:
                    pass
            props[prop] = val
        return props

    @staticmethod
    def _parse_list(line: str) -> List[str]:
        line = line.split(":")[1] # string after the colon
        line = line.strip().strip("[").strip("]") # strip whitespace and square brackets
        red = []
        for element in line.split(","):
            red.append(element.strip())
        return red

    @staticmethod
    def _parse_agent_max(line: str) -> int:
        if len(line.split("[")) > 1:
            return int(line.split("[")[1].split("]")[0])
        return 1

    @staticmethod
    def _parse_logic(line: str) -> LogicType:
        logicStr = line.split(":")[1].strip(" ").strip()
        if logicStr == "ATL":
            return LogicType.ATL
        elif logicStr == "CTL":
            return LogicType.CTL
        else:
            return LogicType.ATL

    @staticmethod
    def _parse_formula(line: str) -> str:
        return line.split(":")[1].strip(" ")

    @staticmethod
    def _parse_semantics(line: str) -> str:
        return line.split(":")[1].strip(" ").strip("\n")

    @staticmethod
    def _parse_show_epistemic(line: str) -> bool:
        return line.split(":")[1].strip(" ").casefold() == "true"

    def _find_agent_end(self, lines: List[str], line_index: int) -> int:
        while line_index < len(lines) and not StringTools.is_blank_line(
                lines[line_index]) and not self._is_agent_header(lines[line_index]):
            line_index += 1
        return line_index


if __name__ == "__main__":
    global_model_parser = GlobalModelParser()
    global_model_parser.parse("provafor.txt")
