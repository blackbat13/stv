from abc import ABC, abstractmethod


class IsplGenerator(ABC):

    @property
    def ispl_model(self) -> str:
        return self.__ispl_model

    def __init__(self):
        self.__ispl_model = ""

    def create_model(self) -> str:
        self.__ispl_model = ""
        self.__ispl_model += self.__define_semantics()
        self.__ispl_model += self.__create_environment()
        self.__ispl_model += self.__create_agents()
        self.__ispl_model += self.__create_evaluation()
        self.__ispl_model += self.__create_init_states()
        self.__ispl_model += self.__create_groups()
        self.__ispl_model += self.__create_formulae()
        return self.__ispl_model

    @abstractmethod
    def __define_semantics(self):
        pass

    def __create_environment(self) -> str:
        environment = "Agent Environment\n"
        environment += self.__create_environment_obsvars()
        environment += self.__create_environment_vars()
        environment += self.__create_environment_actions()
        environment += self.__create_environment_protocol()
        environment += self.__create_environment_evolution()
        environment += "end Agent\n\n"
        return environment

    @abstractmethod
    def __create_environment_obsvars(self) -> str:
        pass

    @abstractmethod
    def __create_environment_vars(self) -> str:
        pass

    @abstractmethod
    def __create_environment_actions(self) -> str:
        pass

    @abstractmethod
    def __create_environment_protocol(self) -> str:
        pass

    @abstractmethod
    def __create_environment_evolution(self) -> str:
        pass

    @abstractmethod
    def __create_agents(self) -> str:
        pass

    @abstractmethod
    def __create_evaluation(self) -> str:
        pass

    @abstractmethod
    def __create_init_states(self) -> str:
        pass

    @abstractmethod
    def __create_groups(self) -> str:
        pass

    @abstractmethod
    def __create_formulae(self) -> str:
        pass
