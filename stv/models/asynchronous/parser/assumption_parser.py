import copy

from stv.models.asynchronous.global_model import LogicType
from stv.tools import StringTools
from stv.models.asynchronous import GlobalModel
from stv.models.asynchronous.parser.local_model_parser import LocalModelParser
from typing import List, Dict
import base64


class AssumptionParser:
    """
    Parser for the global model.
    """

    def __init__(self):
        pass

    def parseBase64String(self, base64String: str) -> List[GlobalModel]:
        """
        Parse model from the base64 string.
        :param string: Base64 model string.
        :return: List[GlobalModel].
        """
        string = base64.b64decode(base64String).decode("UTF-8")
        return self.parseString(string)

    def parseLines(self, lines: List[str]):
        local_models = []
        reduction = []
        bounded_vars = []
        persistent = []
        coalition = []
        goal = []
        logicType = LogicType.ATL
        formula = ""
        show_epistemic = True
        semantics = "synchronous"
        i = 0
        initial = {}
        groups = []
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
                    groups[-1]['models'].append(len(local_models) - 1)
            elif self._is_persistent_header(lines[i]):
                persistent = self._parse_list(lines[i])
                i += 1
            elif self._is_formula_header(lines[i]):
                formula = self._parse_formula(lines[i])
                groups[-1]['formula'] = formula
                i += 1
            elif self._is_show_epistemic_header(lines[i]):
                show_epistemic = self._parse_show_epistemic(lines[i])
                i += 1
            elif self._is_initial_header(lines[i]):
                initial = self._parse_initial(lines[i])
                i += 1
            elif self._is_group_header(lines[i]):
                group_name = self._parse_group(lines[i])
                groups.append({'models': [], 'formula': "", 'name': group_name})
                i += 1
            elif self._is_conf_header(lines[i]):
                i += 1

        result = []
        for group_id in range(len(groups)):
            if groups[group_id]['formula'] == "":
                continue

            group_props = set()
            for local_id in groups[group_id]['models']:
                group_props.update(local_models[local_id].local)
                group_props.update(local_models[local_id].interface)

            new_local_models = copy.deepcopy(local_models)
            for local_id in range(len(new_local_models)):
                if local_id in groups[group_id]['models']:
                    continue

                new_local_models[local_id].remove_props(group_props)

            result.append(GlobalModel(new_local_models, reduction, bounded_vars, persistent, coalition, goal, logicType,
                                      groups[group_id]['formula'],
                                      show_epistemic,
                                      semantics, initial, f"Assumption {groups[group_id]['name']}"))

        global_model = GlobalModel(local_models, reduction, bounded_vars, persistent, coalition, goal, logicType,
                                      groups[0]['formula'],
                                      show_epistemic,
                                      semantics, initial, 'Global')

        return result, global_model

    def parseString(self, string: str):
        lines = string.splitlines()
        for i in range(0, len(lines)):
            if not lines[i].endswith("\n"):
                lines[i] += "\n"
        return self.parseLines(lines)


    def parseFile(self, file_name: str) -> List[GlobalModel]:
        """
        Parse model from the file.
        :param file_name: Name of the file.
        :return: None.
        """
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()
        return self.parseLines(lines)

    @staticmethod
    def _is_group_header(line: str):
        return line[0:5] == "Group"

    @staticmethod
    def _is_conf_header(line: str):
        return line[0:4] == "Conf"

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
    def _is_persistent_header(line: str):
        return line[0:10] == "PERSISTENT"

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
    def _parse_group(line: str) -> str:
        name = line.split(" ")[1]
        name = name.strip(": \n")
        return name

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
        line = line.split(":")[1]  # string after the colon
        line = line.strip().strip("[").strip("]")  # strip whitespace and square brackets
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
    assumption_parser = AssumptionParser()
    filename = "robots_assumption"
    # global_models = assumption_parser.parse("train_controller_assumption.txt")
    global_models = assumption_parser.parseFile(f"{filename}.txt")

    for model_id in range(len(global_models)):
        file = open(f"{filename}_{model_id}.txt", "w")
        file.write(f"{global_models[model_id]}")
        file.close()
