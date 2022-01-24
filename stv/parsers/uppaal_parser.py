from xml.etree import ElementTree


class UppaalTransition:
    def __init__(self):
        self.source = ""
        self.target = ""
        self.guard = ""
        self.assignment = ""
        self.comments = ""

    def parse(self, transition):
        self.source = transition.find("source").attrib["ref"]
        self.target = transition.find("target").attrib["ref"]
        labels = transition.findall("label")
        for label in labels:
            if label.attrib["kind"] == "guard":
                self.guard = label.text
            if label.attrib["kind"] == "assignment":
                self.assignment = label.text
            if label.attrib["kind"] == "comments":
                self.comments = label.text

    def __str__(self):
        result = f"Source: {self.source}\n"
        result += f"Target: {self.target}\n"
        result += f"Guard: {self.guard}\n"
        result += f"Assignment: {self.assignment}\n"
        result += f"Comments: {self.comments}\n"
        return result


class UppaalLocalModel:
    def __init__(self, agent_name: str):
        self._name = agent_name
        self._states = []
        self._transitions = []
        self._init = ""

    def add_transition(self, transition):
        self._transitions.append(transition)

    def set_init(self, id: str):
        self._init = id

    def add_state(self, id: str, name: str):
        self._states.append({"id": id, "name": name})

    def print_states(self):
        for state in self._states:
            print(state)

    def __str__(self):
        result = f"Agent name: {self._name}\n"
        result += f"Init state: {self._init}\n"
        result += "States:\n"
        for state in self._states:
            result += str(state) + "\n"
        result += "Transitions:\n"
        for tran in self._transitions:
            result += str(tran) + "\n"
        return result


class UppaalModelParser:
    def __init__(self, file_name: str):
        self._tree = ElementTree.parse(file_name)
        self._root = self._tree.getroot()
        self._local_models = []

    def parse(self):
        for elem in self._root:
            if elem.tag == "template":
                self._parse_local_model(elem)

    def _parse_local_model(self, template):
        local_model = UppaalLocalModel(template.find("name").text)
        locations = template.findall("location")
        transitions = template.findall("transition")

        for loc in locations:
            local_model.add_state(loc.attrib["id"], loc.find("name").text)

        for tran in transitions:
            uppaal_transition = UppaalTransition()
            uppaal_transition.parse(tran)
            local_model.add_transition(uppaal_transition)

        local_model.set_init(template.find("init").attrib["ref"])

        print(local_model)

    def apply(self, nat_strat):
        for elem in self._root:
            if elem.tag == "template" and elem.find("name").text == nat_strat._agent_name:
                transitions = elem.findall("transition")
                for tran in transitions:
                    comment = ""
                    guard_label = None
                    labels = tran.findall("label")
                    for label in labels:
                        if label.attrib["kind"] == "comments":
                            comment = label.text
                        if label.attrib["kind"] == "guard":
                            guard_label = label

                    if comment == "":
                        continue

                    for strat in nat_strat._strategy:
                        if strat["action"] == comment or (strat["action"] == "*" and comment not in nat_strat._actions):
                            if guard_label is not None:
                                # tran.remove(guard_label)
                                guard = guard_label.text
                                guard = f"({guard}) && {strat['conditions']}"
                                guard_label.text = guard
                                # tran.append(guard_label)
                            else:
                                nail_count = len(tran.findall("nail"))
                                label = ElementTree.Element("label")
                                label.set("kind", "guard")
                                label.text = strat["conditions"]
                                label.set("x", "0")
                                label.set("y", "0")

                                tran.insert(len(tran) - nail_count, label)
                                # tran.append(label)
                            # Add guard label
                            break
        data = ElementTree.tostring(self._root)
        file = open("test.xml", "w+b")
        file.write(data)
        file.close()


class NaturalStrategy:
    def __init__(self):
        self._agent_name = ""
        self._strategy = []
        self._actions = set()

    def parse(self, file_name: str):
        file = open(file_name)
        lines = file.read().split("\n")
        for line in lines:
            if line[0:5] == "Agent":
                self._agent_name = line.split(":")[1].strip(" ")
            else:
                conditions, state = line.split("->")
                conditions = conditions.strip(" ")
                state = state.strip(" ")
                self._strategy.append({"conditions": conditions, "action": state})
                self._actions.add(state)

        file.close()

    def prepare(self):
        for i in range(len(self._strategy) - 1, 0, -1):
            new_condition = "(("
            for j in range(0, i):
                new_condition += f"!{self._strategy[j]['conditions']} && "
            new_condition = new_condition.rstrip("& ")
            new_condition += f") && {self._strategy[i]['conditions']})"
            self._strategy[i]["conditions"] = new_condition

        # self._strategy.append({"conditions": f"!({self._strategy[-1]['conditions']})", "action": "*"})

    def __str__(self):
        result = f"Agent name: {self._agent_name}\n"
        result += "Strategy:\n"
        for strat in self._strategy:
            result += str(strat) + "\n"

        return result


if __name__ == "__main__":
    parser = UppaalModelParser("test.xml")
    # parser.parse()

    natural_strategy = NaturalStrategy()
    natural_strategy.parse("nat_strat4_Check4SN.txt")
    natural_strategy.prepare()
    print(natural_strategy)

    parser.apply(natural_strategy)
    # parser.parse()
