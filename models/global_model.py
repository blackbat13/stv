from .local_model import LocalModel
from typing import List


class GlobalModel:
    def __init__(self):
        self._local_models: List[LocalModel] = []

    def parse(self, file_name: str):
        input_file = open(file_name, "r")
        lines = input_file.readlines()
        input_file.close()

        i = 0
        while i < len(lines):
            if len(lines[i].strip()) == 0:
                i += 1
                continue

            if lines[i][0:5] == "Agent":
                line_from = i
                while i < len(lines) and len(lines[i].strip()) != 0 and lines[i][0:5] != "Agent":
                    i += 1

                line_to = i
                agent_max = 1
                if len(lines[line_from].split("[")) > 1:
                    agent_max = int(lines[line_from].split("[")[1].split("]")[0])
                for agent_id in range(1, agent_max + 1):
                    self._local_models.append(LocalModel().parse("\n".join(lines[line_from:line_to]), agent_id))
