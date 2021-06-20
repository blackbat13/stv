from typing import List, Dict, Any, Set


class LocalState:
    def __init__(self, identifier: int = -1):
        self._identifier: int = identifier
        self._label: str = ""
        self._propositions: Set[str] = set()
        self._variables: Dict[str, Any] = dict()

    @property
    def identifier(self) -> int:
        return self._identifier

    @identifier.setter
    def identifier(self, val: int):
        # TODO verify that the value is integer
        self._identifier = val

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, val: str):
        # TODO verify that the value is string
        self._label = val

    @property
    def propositions(self) -> Set[str]:
        return self._propositions.copy()

    @property
    def variables(self) -> Dict[str, Any]:
        return self._variables

    def add_proposition(self, name: str):
        """
        Add proposition to the state
        :param name: name of the proposition to add
        :return: None
        """
        self._propositions.add(name)

    def check_proposition(self, name: str) -> bool:
        """
        Checks if the proposition is true in the state
        :param name: name of the proposition to check
        :return: true if proposition holds in the state, false otherwise
        """
        return name in self._propositions

    def evaluate(self, condition: str) -> bool:
        """
        Evaluates condition based on the state propositions
        :param condition: condition to evaluate on state
        :return: true if condition holds in the state, false otherwise
        """
        raise NotImplementedError()

    def add_variable(self, name: str, value: Any):
        """
        Adds variable to the state
        :param name: name of the variable to add
        :param value: value of the variable
        :return: None
        """
        # TODO raise error if variable already defined in the state
        self._variables[name] = value

    def change_variable(self, name: str, value: Any):
        """
        Changes value of the variable in the state
        :param name: name of the variable
        :param value: new value of the variable
        :return: None
        """
        # TODO raise error if variable not in the state
        self._variables[name] = value

    def remove_variable(self, name: str):
        """
        Removes variable from the state
        :param name: name of the variable
        :return:
        """
        # TODO raise error if variable not in the state
        self._variables.pop(name)

    def get_variable(self, name: str) -> Any:
        """
        Gets value of the variable in the state
        :param name: name of the variable
        :return: value of the variable
        """
        # TODO raise error if variable not in the state
        return self._variables[name]

    def __str__(self) -> str:
        return f"State_{self._identifier} {self._label}, " \
               f"propositions: {self._propositions}, " \
               f"variables: {self._variables}"


class GlobalState(LocalState):
    def __init__(self, identifier: int = -1):
        super(GlobalState, self).__init__(identifier)


class LocalTransition:
    def __init__(self, from_state: LocalState, to_state: LocalState, actions: List[str]):
        self._from_state = from_state
        self._to_state = to_state
        self._actions = actions


class GlobalTransition(LocalTransition):
    def __init__(self, from_state: GlobalState, to_state: GlobalState, actions: List[str]):
        super(GlobalTransition, self).__init__(from_state, to_state, actions)


class LocalModel:
    def __init__(self):
        self._states: List[LocalState] = []
        self._transitions: List[LocalTransition] = []


class Agent:
    def __init__(self, local_model: LocalModel, name: str = "", identifier: int = -1):
        self._name: str = name
        self._identifier: int = identifier
        self._local_model = local_model

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> int:
        return self._identifier

    @property
    def observables(self) -> List[str]:
        """List of observable propositions"""
        raise NotImplementedError

    @property
    def actions(self) -> List[str]:
        """List of actions of the agent"""
        raise NotImplementedError


class AsynchronousModel:
    pass


class GlobalModel:
    pass
