from abc import ABC, abstractmethod


class IsplGenerator(ABC):
    """
    Template class for ispl generators.
    """

    @property
    def ispl_model(self) -> str:
        return self.__ispl_model

    def __init__(self):
        self.__ispl_model = ""

    def create_model(self) -> str:
        self.__ispl_model = ""
        self.__ispl_model += self._define_semantics()
        self.__ispl_model += self._create_environment()
        self.__ispl_model += self._create_agents()
        self.__ispl_model += self._create_evaluation()
        self.__ispl_model += self._create_init_states()
        self.__ispl_model += self._create_groups()
        self.__ispl_model += self._create_formulae()
        return self.__ispl_model

    @abstractmethod
    def _define_semantics(self):
        pass

    def _create_environment(self) -> str:
        environment = "Agent Environment\n"
        environment += self._create_environment_obsvars()
        environment += self._create_environment_vars()
        environment += self._create_environment_actions()
        environment += self._create_environment_protocol()
        environment += self._create_environment_evolution()
        environment += "end Agent\n\n"
        return environment

    @abstractmethod
    def _create_environment_obsvars(self) -> str:
        pass

    @abstractmethod
    def _create_environment_vars(self) -> str:
        pass

    @abstractmethod
    def _create_environment_actions(self) -> str:
        pass

    @abstractmethod
    def _create_environment_protocol(self) -> str:
        pass

    @abstractmethod
    def _create_environment_evolution(self) -> str:
        pass

    @abstractmethod
    def _create_agents(self) -> str:
        pass

    @abstractmethod
    def _create_evaluation(self) -> str:
        pass

    @abstractmethod
    def _create_init_states(self) -> str:
        pass

    @abstractmethod
    def _create_groups(self) -> str:
        pass

    @abstractmethod
    def _create_formulae(self) -> str:
        pass
