import itertools
import random


class SimpleVotingModelIsplGenerator:
    ispl_model = ""

    def __init__(self, number_of_candidates, number_of_voters):
        self.number_of_candidates = number_of_candidates
        self.number_of_voters = number_of_voters

    def create_ispl_model(self):
        self.ispl_model += "Semantics = SA;\n"
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
        environment += self.__create_environment_vars()
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
        # for voter_number in range(1, self.number_of_voters + 1):
        #     vars += "\t\tvoter" + str(voter_number) + "Vote: 0.." + str(self.number_of_candidates) + ";\n"
        for voter_number in range(1, self.number_of_voters + 1):
            vars += "\t\tvoter" + str(voter_number) + "Voted: boolean;\n"
        for voter_number in range(1, self.number_of_voters + 1):
            vars += "\t\tvoter" + str(voter_number) + "Decided: boolean;\n"
        for voter_number in range(1, self.number_of_voters + 1):
            vars += "\t\tvoter" + str(voter_number) + "Pun: {pun, np, None};\n"
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
        for voter_number in range(1, self.number_of_voters + 1):
            evolution += "\t\tvoter" + str(voter_number) + "Voted=true if\n"
            for candidate_number in range(1, self.number_of_candidates+1):
                evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Vote" + str(candidate_number) + " or\n"
            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"
        for voter_number in range(1, self.number_of_voters + 1):
            evolution += "\t\tvoter" + str(voter_number) + "Decided=true if\n"
            evolution += "\t\t\tVoter"+ str(voter_number) + ".Action=Give or\n"
            evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Ng;\n"
            evolution += "\t\tvoter" + str(voter_number) + "Pun=pun if\n"
            evolution += "\t\t\tCoercer.Action=Pun" + str(voter_number) + ";\n"
            evolution += "\t\tvoter" + str(voter_number) + "Pun=np if\n"
            evolution += "\t\t\tCoercer.Action=Np" + str(voter_number) + ";\n"
        evolution += "\tend Evolution\n"
        return evolution

    def __create_coercer(self):
        player = "Agent Coercer\n"

        player += self.__create_coercer_lobsvars()
        player += self.__create_coercer_vars()
        player += self.__create_coercer_actions()
        player += self.__create_coercer_protocol()
        player += self.__create_coercer_evolution()
        player += "end Agent\n\n"
        return player

    def __create_coercer_lobsvars(self):
        lobsvars = "\tLobsvars = {"
        for voter_number in range(1, self.number_of_voters + 1):
            lobsvars += "voter" + str(voter_number) + "Voted, "
            lobsvars += "voter" + str(voter_number) + "Decided, "
            lobsvars += "voter" + str(voter_number) + "Pun, "

        lobsvars = lobsvars.rstrip(" ,")
        lobsvars += "};\n"
        return lobsvars

    def __create_coercer_vars(self):
        vars = "\tVars:\n"
        vars += "\t\tx: boolean;\n"
        vars += "\tend Vars\n"
        return vars

    def __create_coercer_actions(self):
        actions = "\tActions = {"
        for voter_number in range(1, self.number_of_voters + 1):
            actions += "Pun" + str(voter_number) + ", Np" + str(voter_number) + ", "
        actions += "Wait};\n"
        return actions

    def __create_coercer_protocol(self):
        protocol = "\tProtocol:\n"
        for voter_number in range(1, self.number_of_voters + 1):
            protocol += "\t\tEnvironment.voter" + str(voter_number) + "Voted=true and Environment.voter" + str(voter_number) + "Pun=None and Environment.voter"+ str(voter_number) + "Decided=true: {Pun" + str(voter_number) + ", Np" + str(voter_number) + ", Wait};\n"
        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_coercer_evolution(self, ):
        evolution = "\tEvolution:\n"
        evolution += "\t\tx=false if Action=Wait;\n"
        evolution += "\tend Evolution\n"
        return evolution

    def __create_voter(self, voter_number):
        player = "Agent Voter" + str(voter_number) + "\n"

        player += self.__create_voter_lobsvars(voter_number)
        player += self.__create_voter_vars()
        player += self.__create_voter_actions()
        player += self.__create_voter_protocol()
        player += self.__create_voter_evolution()
        player += "end Agent\n\n"
        return player

    def __create_voter_lobsvars(self, voter_number):
        lobsvars = "\tLobsvars = {"
        lobsvars += "voter" + str(voter_number) + "Voted, voter" + str(voter_number) + "Pun, voter" + str(voter_number) + "Decided"
        lobsvars += "};\n"
        return lobsvars

    def __create_voter_vars(self):
        vars = "\tVars:\n"
        vars += "\t\tvote: 0.." + str(self.number_of_candidates) + ";\n"
        vars += "\t\tdecision: {give, ng, None};\n"
        vars += "\tend Vars\n"
        return vars

    def __create_voter_actions(self):
        actions = "\tActions = {"
        for candidate_number in range(1, self.number_of_candidates+1):
            actions += "Vote" + str(candidate_number) + ", "

        actions += "Give, Ng, "
        actions += "Wait};\n"
        return actions

    def __create_voter_protocol(self):
        protocol = "\tProtocol:\n"
        protocol += "\t\tvote=0: {"
        for candidate_number in range(1, self.number_of_candidates+1):
            protocol += "Vote" + str(candidate_number) + ", "
        protocol += "Wait};\n"
        protocol += "\t\tvote>0 and decision=None: {Give, Ng, Wait};\n"
        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_voter_evolution(self, ):
        evolution = "\tEvolution:\n"
        for candidate_number in range(1, self.number_of_candidates + 1):
            evolution += "\t\tvote=" + str(candidate_number) + " if Action=Vote" + str(candidate_number) + ";\n"
        evolution += "\t\tdecision=give if Action=Give;\n"
        evolution += "\t\tdecision=ng if Action=Ng;\n"
        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self):
        evaulation = "Evaluation\n"
        evaulation += "\tVoter1Punished if Environment.voter1Pun=pun;\n"
        evaulation += "\tVoter1NotPunished if Environment.voter1Pun=np;\n"
        evaulation += "\tVoter1Voted1 if Voter1.vote=1;\n"
        evaulation += "\tVoter1Finish if Environment.voter1Pun=pun or Environment.voter1Pun=np;\n"
        evaulation += "end Evaluation\n\n"
        return evaulation

    def __create_init_states(self):
        init_states = "InitStates\n"
        init_states += "\t\t"
        for voter_number in range(1, self.number_of_voters + 1):
            init_states += "Voter" + str(voter_number) + ".vote=0 and Voter" + str(voter_number) + ".decision=None and Environment.voter" + str(voter_number) + "Voted=false and Environment.voter" + str(voter_number) + "Pun=None and Environment.voter" + str(voter_number) + "Decided=false and "
        init_states += "Coercer.x=false"
        init_states += ";\n"
        init_states += "end InitStates\n\n"
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
        formulae += "\t<c>F(!Voter1Punished -> Voter1Voted1);\n"
        formulae += "\t<v1>G(!Voter1Punished and !Voter1Voted1);\n"
        formulae += "\t<c>G((Voter1Finish and !Voter1Punished) -> Voter1Voted1);\n"
        formulae += "\t<v1>F(Voter1Finish and !Voter1Punished and !Voter1Voted1);\n"
        formulae += "end Formulae\n\n"
        return formulae


n = int(input("Number of candidates = "))
k = int(input("Number of voters = "))

simple_voting_model_ispl_generator = SimpleVotingModelIsplGenerator(n, k)
f = open("simple_voting_" + str(n) + "_" + str(k) + ".ispl", "w")
f.write(simple_voting_model_ispl_generator.create_ispl_model())
f.close()
