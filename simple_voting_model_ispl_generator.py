import itertools
import random


class SimpleVotingModelIsplGenerator:
    ispl_model = ""

    def __init__(self, number_of_candidates, number_of_voters):
        self.number_of_candidates = number_of_candidates
        self.number_of_voters = number_of_voters

    def create_ispl_model(self):
        self.ispl_model += self.__create_environment()
        self.ispl_model += self.__create_coercer()
        for voter_number in range(1, self.number_of_voters + 1):
            self.ispl_model += self.__create_voter(voter_number)
        self.ispl_model += self.__create_evaluation()
        self.ispl_model += self.__create_init_states()
        self.ispl_model += self.__create_groups()
        self.ispl_model += self.__create_formulae()
        return self.ispl_model

    def __create_environment(self):
        environment = "Agent Environment\n"
        environment += self.__create_environment_obsvars()
        # environment += self.__create_environment_vars()
        environment += self.__create_environment_actions()
        environment += self.__create_environment_protocol()
        environment += self.__create_environment_evolution()
        environment += "end Agent\n\n"
        return environment

    def __create_environment_obsvars(self):
        obsvars = "\tObsvars:\n"

        obsvars += "\tend Obsvars\n"
        return obsvars

    def __create_environment_vars(self):
        vars = "\tVars:\n"

        vars += "\tend Vars\n"
        return vars

    def __create_environment_actions(self):
        actions = "\tActions = {none};\n"
        return actions

    def __create_environment_protocol(self):
        protocol = "\tProtocol:\n\t\tOther:{none};\n\tend Protocol\n"
        return protocol

    def __create_environment_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_coercer(self):
        player = "Agent Coercer\n"

        player += self.__create_coercer_vars()
        player += self.__create_coercer_actions()
        player += self.__create_coercer_protocol()
        player += self.__create_coercer_evolution()
        player += "end Agent\n\n"
        return player

    def __create_coercer_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_coercer_vars(self):
        vars = "\tVars:\n"

        vars += "\tend Vars\n"
        return vars

    def __create_coercer_actions(self):
        actions = "\tActions = {"

        actions += "Wait};\n"
        return actions

    def __create_coercer_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_coercer_evolution(self, ):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_voter(self, voter_number):
        player = "Agent Voter" + str(voter_number) + "\n"

        player += self.__create_voter_vars()
        player += self.__create_voter_actions()
        player += self.__create_voter_protocol()
        player += self.__create_voter_evolution()
        player += "end Agent\n\n"
        return player

    def __create_voter_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_voter_vars(self):
        vars = "\tVars:\n"

        vars += "\tend Vars\n"
        return vars

    def __create_voter_actions(self):
        actions = "\tActions = {"

        actions += "Wait};\n"
        return actions

    def __create_voter_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_voter_evolution(self, ):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self):
        evaulation = "Evaluation\n"

        evaulation += "end Evaluation\n\n"
        return evaulation

    def __create_init_states(self):
        init_states = "InitStates\n"

        init_states += ";\nend InitStates\n\n"
        return init_states

    def __create_groups(self):
        groups = "Groups\n"
        groups += "\tc={Coercer};\n"
        for voter_number in range(1, self.number_of_voters + 1):
            groups += "\tv" + str(voter_number) + "={Voter" + str(voter_number) + "};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self):
        formulae = "Formulae\n"

        formulae += "end Formulae\n\n"
        return formulae


n = 2
k = 1
simple_voting_model_ispl_generator = SimpleVotingModelIsplGenerator(n, k)
f = open("simple_voting_" + str(n) + "_" + str(k) + ".ispl", "w")
f.write(simple_voting_model_ispl_generator.create_ispl_model())
f.close()
