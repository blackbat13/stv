from stv.models.asynchronous import LocalTransition


class LocalTransitionParser:
    """
    Parser for local transition.
    """

    def __init__(self):
        pass

    def parse(self, transition_str: str) -> LocalTransition:
        """
        Parse transition string.
        :param transition_str: String representing the transition.
        :return: None
        """

        shared: bool = False
        action: str = ""
        state_from: str = ""
        state_to: str = ""
        cond = []
        cond_str = ""
        props = {}

        if transition_str[0:6] == "shared":
            shared = True
            transition_str = transition_str[7:]

        action, transition_str = transition_str.split(":")

        # parsing the pre-condition
        if transition_str.find("->") == -1:
            state_from, transition_str = transition_str.split("-[")
            conditions, transition_str = transition_str.split("]>")
            cond_str = conditions
            conditions = conditions.split('and')  # assume that conditions list represents their conjunction
            for condition in conditions:
                recognized_op = False
                for op in ["==", "!=", ">=", "<=", ">", "<"]:
                    if condition.find(op) != -1:
                        term1, term2 = condition.split(op)
                        # casting to int - in local_transition class
                        cond.append((term1.strip(" "), term2.strip(" "), op.strip(" ")))
                        recognized_op = True
                        break

                if not recognized_op:
                    print(f"ERR: Unknown binary operator in '{condition}'")
                    raise Exception
        else:
            state_from, transition_str = transition_str.split("->")

        # parsing the post-condition
        if transition_str.find("[") != -1:
            state_to, transition_str = transition_str.split("[")
            transition_str = transition_str.split("]")[0]
            variables = transition_str.split(",")
            for variable in variables:
                variable = variable.strip(" ")
                prop, val = variable.split("=")
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
                        # print(f"ERR: Attempt to assign a non-integer value to a variable in '{prop}={val}'")
                        pass
                if prop[-1] == "+":
                    prop = prop.rstrip("+")
                    props[prop] = ("+", val)
                elif prop[-1] == "-":
                    prop = prop.rstrip("-")
                    props[prop] = ("-", val)
                else:
                    props[prop] = ("", val)
        else:
            state_to = transition_str

        state_from = state_from.strip()
        state_to = state_to.strip()

        return LocalTransition(state_from, state_to, action, shared, cond, props, cond_str)
