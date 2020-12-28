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
        props = {}

        if transition_str[0:6] == "shared":
            shared = True
            transition_str = transition_str[7:]

        action, transition_str = transition_str.split(":")
        if transition_str.find("->") == -1:
            state_from, transition_str = transition_str.split("-[")
            conditions, transition_str = transition_str.split("]>")
            if conditions.find("==") != -1:
                cond_var, cond_val = conditions.split("==")
                cond.append((cond_var, int(cond_val), "=="))
            elif conditions.find("!=") != -1:
                cond_var, cond_val = conditions.split("!=")
                cond.append((cond_var, int(cond_val), "!="))
            else:
                raise Exception
        else:
            state_from, transition_str = transition_str.split("->")

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
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                props[prop] = val
        else:
            state_to = transition_str

        state_from = state_from.strip()
        state_to = state_to.strip()

        return LocalTransition(state_from, state_to, action, shared, cond, props)
