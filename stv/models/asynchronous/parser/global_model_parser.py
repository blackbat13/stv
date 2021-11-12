from stv.models.asynchronous.global_model import LogicType
from stv.tools import StringTools
from stv.models.asynchronous import GlobalModel
from stv.models.asynchronous.parser.local_model_parser import LocalModelParser
from typing import List, Dict

import re
from stv.models.asynchronous import LocalTransition, LocalModel
from stv.parsers import FormulaParser

class GlobalModelParser:
    """
    Parser for the global model.
    """

    def __init__(self):
        pass

    def parse_from_file(self, file_name: str) -> GlobalModel:
        """
        Parse model from the file.
        :param file_name: Name of the file.
        :return: None.
        """
        input_file = open(file_name, "r")
        input_string = input_file.read()
        input_file.close()
        return self.parse_from_string(input_string)

    def parse_from_string(self, input_string: str) -> GlobalModel:
        lines = input_string.splitlines()
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
                    local_model = LocalModelParser().parse(len(local_models),
                                                           "\n".join(lines[line_from:line_to]),
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

    # TODO: add support for verification of multiple queries (currently only the first will be considered)
    # TODO: remove hard-coded and redundant variables (logicType, coalition, etc)
    # TODO: keywords for local(per agent instance) and global variables
    def parse_2(self, input_string: str):
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

        action_is_shared_dict = {}  # maps action name to the number of agents sharing it
        agents = []  # describe the model
        queries = []  # describe the specification

        i = 0
        initial = {}

        headers = [
            "query",
            "agent",
        ]

        # reserved statement prefixes
        agent_spec_keywords = [
            "init",
            "var",
            "protocol"
        ]

        query_spec_keywords = [
            "reduction",
            "formula",
            "comment"
        ]

        headers_pattern = rf"({'|'.join(headers)})([^{{:]*?){{([^}}]*)}}"
        agent_spec_pattern = rf"^({'|'.join(agent_spec_keywords)})\s*:\s*([^{{}};]*?)$"
        query_spec_pattern = rf"^({'|'.join(query_spec_keywords)})\s*:\s*([^{{}};]*?)$"
        comments_pattern = rf"#.*\n"

        # remove comments from the input string
        input_string = re.sub(comments_pattern, rf"\n", input_string, re.MULTILINE)

        for m in re.finditer(headers_pattern, input_string, re.MULTILINE | re.IGNORECASE):
            header_match = m.group(1).strip()
            if header_match.lower() == "agent":
                agent_name = m.group(2).strip()
                agent_max = 1

                if (xx := re.match(rf"([^\]\[]*)\[(\s*\d*\s*)\]", agent_name, re.IGNORECASE)):
                    agent_name = xx.group(1)
                    agent_max = int(xx.group(2).strip())

                # new agent
                a = {
                    "name": agent_name,
                    "max": agent_max,
                    "edges": [],
                    "locations": set(),
                    "protocol": []
                }

                statements = list(map(lambda x: x.strip(), m.group(3).split(';')))
                statements = list(filter(None, statements))

                for statement in statements:
                    # print(statement)
                    if (match := re.match(agent_spec_pattern, statement, re.MULTILINE | re.IGNORECASE)) is not None:
                        a[match.group(1)] = match.group(2)
                    else:
                        action_match = re.match(rf"^([^{{}}:]*)\s*:\s*([^{{}}]*?)$", statement,
                                                re.MULTILINE | re.IGNORECASE)
                        action_name = action_match.group(1)
                        action_body = action_match.group(2)

                        if action_name.startswith("sh "):
                            action_name = action_name[3:].strip()
                        elif action_name.startswith("shared "):
                            action_name = action_name[7:].strip()

                        # edge_match = re.match(rf"^(.*)\s*(-->|-\[[^\[\]]*\]->)\s*(.*)$", action_body, re.MULTILINE)
                        edge_match = re.match(rf"^(.+?)-(\[[^\[\]]*\])?->\s*([^:]*)(:.*)?$", action_body,
                                              re.MULTILINE)

                        edge_src = edge_match.group(1).strip()
                        edge_trg = edge_match.group(3).strip()

                        a["locations"].update([edge_src, edge_trg])

                        edge_effect = ""
                        edge_guard = ""

                        edge_bracket = edge_match.group(2)
                        if edge_bracket is not None:
                            edge_bracket = edge_bracket[1:][:-1]
                            edge_guard, *edge_effect = edge_bracket.split(':')
                            if len(edge_effect) > 0:
                                edge_effect = edge_effect[0]
                            else:
                                edge_effect = ""
                        if edge_match.group(4) is not None:
                            edge_effect = ','.join(
                                list(filter(lambda x: x != "", [edge_effect, edge_match.group(4)[1:]])))

                        edge_guard = edge_guard.strip()
                        edge_effect = list(map(lambda x: x.replace(" ", ""), edge_effect.split(',')))

                        # process alias for message passing via action name suffix: <action_name>(? | !)<message>
                        action_name_match = re.match(rf"^([^!\?]+)([!\?].*$)", action_name, re.MULTILINE)
                        if action_name_match is not None:
                            action_name = action_name_match.group(1)
                            in_alias = re.findall(rf"\?[^!\?]*", action_name_match.group(2), re.MULTILINE)
                            out_alias = re.findall(rf"![^!\?]*", action_name_match.group(2), re.MULTILINE)
                            for msg in in_alias:
                                edge_effect.append(f"in({msg[1:]})")
                            for msg in out_alias:
                                edge_effect.append(f"out({msg[1:]})")

                        a["edges"].append([
                            action_name,  # action name
                            # action_body,  # from,to, [guard,update,...]
                            [
                                edge_src,
                                edge_trg,
                                edge_guard,
                                edge_effect
                            ]
                        ])

                # if there is at least one shared action (of the same name among several agents)
                if len(list(filter(lambda x: x > 0, action_is_shared_dict.values()))) > 0:
                    semantics = "asynchronous"

                # reorder locations, so that initial location is always "in front" (this is needed for the LocalModel later)
                # if no init location were specified should raise an error
                a["locations"] = list(a["locations"])
                a["locations"].insert(0, a["locations"].pop(a["locations"].index(a["init"])))

                agents.append(a)

            elif header_match.lower() == "query":
                q = {
                    "query_name": m.group(2).strip(),
                    "formula": None,
                    "reduction": [],
                    "comment": ""
                }

                statements = list(map(lambda x: x.strip(), m.group(3).split(';')))
                statements = list(filter(None, statements))

                for statement in statements:
                    if (match := re.match(query_spec_pattern, statement, re.MULTILINE | re.IGNORECASE)) is not None:
                        q_attr = match.group(1)
                        q_val = match.group(2)

                        # remove extra whitespaces from value (except comments)
                        if q_attr != "comment":
                            q_val = q_val.replace(" ", "")

                        if q_attr != "formula":
                            q[q_attr] = q_val
                        else:
                            # ? YK: would there be a problem if parseAtlFormula/parseCtlFormula were static methods (not to instantiate FormulaParser) ?
                            formula_parser = FormulaParser()
                            if q_val.startswith("<<"):
                                q[q_attr] = formula_parser.parseAtlFormula(q_val)
                            else:
                                q[q_attr] = formula_parser.parseCtlFormula(q_val)

                    else:
                        print(f"WARN: unsupported query statement - {statement}")
                queries.append(q)

            else:
                print(f"WARN: unsupported header - {header_match}")

        # fill the action_is_shared_dict
        for a in agents:
            agent_actions = list(set(map(lambda x: x[0], a["edges"])))
            for action_name in agent_actions:
                if action_name in action_is_shared_dict:
                    action_is_shared_dict[action_name] += 1
                else:
                    action_is_shared_dict[action_name] = 0

        # temporary/quick solution for out/in
        io_alias_dict = {}
        edge_groups = {}
        for a in agents:
            for action_name, edge in a["edges"]:
                if action_name not in edge_groups:
                    edge_groups[action_name] = []
                edge_groups[action_name].append(edge)

        for action_name, edge_group in edge_groups.items():
            in_msg = []
            for edge in edge_group:
                for el in edge[3]:
                    if el.startswith("in"):
                        in_msg.append(el[3:-1].split(','))
                edge[3] = list(filter(lambda x: not x.startswith("in"), edge[3]))
            for edge in edge_group:
                new_effect = []
                for el in edge[3]:
                    if el.startswith("out"):
                        for msg in in_msg:
                            eles = list(map(
                                lambda j, n: f"{msg[j]}=?{n}",
                                enumerate(el[4:-1].split(',')))
                            )
                            new_effect.extend(eles)
                        # el = ""
                    else:
                        new_effect.append(el)
                # edge[3] = filter(lambda x: x != "", edge[3])
                edge[3] = new_effect[:]

        # Prepare local models
        agent_id = 0
        for a in agents:
            # Prepare transitions
            locations = dict((st, ii) for ii, st in enumerate(a["locations"]))
            transitions = []
            t_id = 0
            while len(transitions) < len(a["locations"]):
                transitions.append([])

            # TODO: add out/in support
            for action_name, edge in a["edges"]:
                (edge_src, edge_trg, edge_guard, edge_effect) = edge
                shared = action_is_shared_dict[action_name] > 0

                # Prepare props (copy of the code from dev)
                props = {}
                for el in edge_effect:
                    if len(el) == 0:
                        continue
                    prop, val = el.split("=")
                    if val.casefold() == "true":
                        val = True
                    elif val.casefold() == "false":
                        val = False
                    elif val[0] == "?":
                        pass
                    else:
                        try:
                            val = int(val)
                        except ValueError:
                            pass

                    if prop[-1] == "+":
                        prop = prop.rstrip("+")
                        props[prop] = ("+", val)
                    elif prop[-1] == "-":
                        prop = prop.rstrip("-")
                        props[prop] = ("-", val)
                    else:
                        props[prop] = val

                t = LocalTransition(edge_src, edge_trg, action_name, shared, edge_guard, props)
                t.id = t_id
                t_id += 1
                t.agent_id = agent_id
                if not t.shared:
                    t.action += f"_{a['name']}"
                transitions[locations[edge_src]].append(t)

            # Generate a local model for each instance of the agent(-type)
            for i in range(a["max"]):
                local_model = LocalModel(agent_id,
                                         f"{a['name']}{i + 1}",
                                         locations,
                                         transitions,
                                         a["protocol"],
                                         set(map(lambda x: x[0], a["edges"]))
                                         )
                local_models.append(local_model)
                agent_id += 1

        # Temporary piece of code
        reduction = queries[0]["reduction"]
        coalition = queries[0]["formula"].agents
        persistent = list(map(lambda v: v[1:],  # strip !-symbol
                              filter(lambda vv: vv.startswith("!"),  # only persistent var_names
                                     filter(None,
                                            list(map(lambda ag: ag.get("var"), agents))
                                            ),  # union over vars
                                     )
                              ))
        # Note, there is no duplicate check for persistent variables here
        return GlobalModel(
            local_models,
            reduction,
            bounded_vars,
            persistent,
            coalition,
            goal,
            logicType,
            str(queries[0]["formula"]),
            show_epistemic,
            semantics,
            initial
        )
