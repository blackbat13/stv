from generators.ispl.ispl_generator import IsplGenerator


class SimpleVotingModelIsplGenerator(IsplGenerator):
    def __init__(self, number_of_candidates, number_of_voters):
        super().__init__()
        self._number_of_candidates = number_of_candidates
        self._number_of_voters = number_of_voters

    def _define_semantics(self):
        return "Semantics = SA;\n"

    def _create_agents(self) -> str:
        agents = self._create_coercer()
        for voter_number in range(1, self._number_of_voters + 1):
            agents += self._create_voter(voter_number)
        return agents

    def _create_environment_obsvars(self):
        return "\tObsvars:\n" \
               "\tend Obsvars\n"

    def _create_environment_vars(self):
        vars = "\tVars:\n"
        # for voter_number in range(1, self.number_of_voters + 1):
        #     vars += "\t\tvoter" + str(voter_number) + "Vote: 0.." + str(self.number_of_candidates) + ";\n"
        for voter_number in range(1, self._number_of_voters + 1):
            vars += f"\t\tvoter{voter_number}Voted: boolean;\n"
        for voter_number in range(1, self._number_of_voters + 1):
            vars += f"\t\tvoter{voter_number}Decided: boolean;\n"
        for voter_number in range(1, self._number_of_voters + 1):
            vars += f"\t\tvoter{voter_number}Pun: {{pun, np, None}};\n"
        vars += "\tend Vars\n"
        return vars

    def _create_environment_actions(self):
        actions = "\tActions = {none};\n"
        return actions

    def _create_environment_protocol(self):
        protocol = "\tProtocol:\n\t\tOther:{none};\n\tend Protocol\n"
        return protocol

    def _create_environment_evolution(self):
        evolution = "\tEvolution:\n"
        for voter_number in range(1, self._number_of_voters + 1):
            evolution += f"\t\tvoter{voter_number}Voted=true if\n"
            for candidate_number in range(1, self._number_of_candidates + 1):
                evolution += f"\t\t\tVoter{voter_number}.Action=Vote{candidate_number} or\n"
            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"
        for voter_number in range(1, self._number_of_voters + 1):
            evolution += f"\t\tvoter{voter_number}Decided=true if\n" \
                f"\t\t\tVoter{voter_number}.Action=Give or\n" \
                f"\t\t\tVoter{voter_number}.Action=Ng;\n" \
                f"\t\tvoter{voter_number}Pun=pun if\n" \
                f"\t\t\tCoercer.Action=Pun{voter_number};\n" \
                f"\t\tvoter{voter_number}Pun=np if\n" \
                f"\t\t\tCoercer.Action=Np{voter_number};\n"
        evolution += "\tend Evolution\n"
        return evolution

    def _create_coercer(self):
        player = "Agent Coercer\n"
        player += self._create_coercer_lobsvars()
        player += self._create_coercer_vars()
        player += self._create_coercer_actions()
        player += self._create_coercer_protocol()
        player += self._create_coercer_evolution()
        player += "end Agent\n\n"
        return player

    def _create_coercer_lobsvars(self):
        lobsvars = "\tLobsvars = {"
        for voter_number in range(1, self._number_of_voters + 1):
            lobsvars += f"voter{voter_number}Voted, voter{voter_number}Decided, voter{voter_number}Pun, "
        lobsvars = lobsvars.rstrip(" ,")
        lobsvars += "};\n"
        return lobsvars

    def _create_coercer_vars(self):
        return "\tVars:\n" \
               "\t\tx: boolean;\n" \
               "\tend Vars\n"

    def _create_coercer_actions(self):
        actions = "\tActions = {"
        for voter_number in range(1, self._number_of_voters + 1):
            actions += f"Pun{voter_number}, Np{voter_number}, "
        actions += "Wait};\n"
        return actions

    def _create_coercer_protocol(self):
        protocol = "\tProtocol:\n"
        for voter_number in range(1, self._number_of_voters + 1):
            protocol += f"\t\tEnvironment.voter{voter_number}Voted=true and " \
                f"Environment.voter{voter_number}Pun=None and " \
                f"Environment.voter{voter_number}Decided=true: {{Pun{voter_number}, Np{voter_number}, Wait}};\n"
        protocol += "\t\tOther: {Wait};\n" \
                    "\tend Protocol\n"
        return protocol

    def _create_coercer_evolution(self, ):
        return "\tEvolution:\n" \
               "\t\tx=false if Action=Wait;\n" \
               "\tend Evolution\n"

    def _create_voter(self, voter_number):
        player = f"Agent Voter{voter_number}\n"
        player += self._create_voter_lobsvars(voter_number)
        player += self._create_voter_vars()
        player += self._create_voter_actions()
        player += self._create_voter_protocol()
        player += self._create_voter_evolution()
        player += "end Agent\n\n"
        return player

    def _create_voter_lobsvars(self, voter_number):
        return f"\tLobsvars = {{voter{voter_number}Voted, voter{voter_number}Pun, voter{voter_number}Decided}};\n"

    def _create_voter_vars(self):
        return f"\tVars:\n" \
               f"\t\tvote: 0..{self._number_of_candidates};\n" \
               f"\t\tdecision: {{give, ng, None}};\n" \
               f"\tend Vars\n"

    def _create_voter_actions(self):
        actions = "\tActions = {"
        for candidate_number in range(1, self._number_of_candidates + 1):
            actions += f"Vote{candidate_number}, "

        actions += "Give, Ng, Wait};\n"
        return actions

    def _create_voter_protocol(self):
        protocol = "\tProtocol:\n" \
                   "\t\tvote=0: {"
        for candidate_number in range(1, self._number_of_candidates + 1):
            protocol += f"Vote{candidate_number}, "
        protocol += "Wait};\n" \
                    "\t\tvote>0 and decision=None: {Give, Ng, Wait};\n" \
                    "\t\tOther: {Wait};\n" \
                    "\tend Protocol\n"
        return protocol

    def _create_voter_evolution(self, ):
        evolution = "\tEvolution:\n"
        for candidate_number in range(1, self._number_of_candidates + 1):
            evolution += f"\t\tvote={candidate_number} if Action=Vote{candidate_number};\n"
        evolution += "\t\tdecision=give if Action=Give;\n" \
                     "\t\tdecision=ng if Action=Ng;\n" \
                     "\tend Evolution\n"
        return evolution

    def _create_evaluation(self):
        return "Evaluation\n" \
               "\tVoter1Punished if Environment.voter1Pun=pun;\n" \
               "\tVoter1NotPunished if Environment.voter1Pun=np;\n" \
               "\tVoter1Voted1 if Voter1.vote=1;\n" \
               "\tVoter1Finish if Environment.voter1Pun=pun or Environment.voter1Pun=np;\n" \
               "end Evaluation\n\n"

    def _create_init_states(self):
        init_states = "InitStates\n" \
                      "\t\t"
        for voter_number in range(1, self._number_of_voters + 1):
            init_states += f"Voter{voter_number}.vote=0 and Voter{voter_number}.decision=None " \
                f"and Environment.voter{voter_number}Voted=false and Environment.voter{voter_number}Pun=None " \
                f"and Environment.voter{voter_number}Decided=false and "
        init_states += "Coercer.x=false;\n" \
                       "end InitStates\n\n"
        return init_states

    def _create_groups(self):
        groups = "Groups\n" \
                 "\tc={Coercer};\n"
        for voter_number in range(1, self._number_of_voters + 1):
            groups += f"\tv{voter_number}={{Voter{voter_number}}};\n"
        groups += "end Groups\n\n"
        return groups

    def _create_formulae(self):
        return "Formulae\n" \
               "\t<c>F(!Voter1Punished -> Voter1Voted1);\n" \
               "\t<v1>G(!Voter1Punished and !Voter1Voted1);\n" \
               "\t<c>G((Voter1Finish and !Voter1Punished) -> Voter1Voted1);\n" \
               "\t<v1>F(Voter1Finish and !Voter1Punished and !Voter1Voted1);\n" \
               "end Formulae\n\n"


class SimpleVotingModel2IsplGenerator:
    ispl_model = ""

    def __init__(self, number_of_candidates, number_of_voters):
        self.number_of_candidates = number_of_candidates
        self.number_of_voters = number_of_voters

    def create_model(self):
        self.ispl_model += "Semantics = SA;\n"
        self.ispl_model += self.__create_environment()
        self.ispl_model += self.__create_election_authority()
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
        obsvars += "\t\tprotection: {high, low, None};\n"
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
        for voter_number in range(1, self.number_of_voters + 1):
            vars += "\t\tvoter" + str(voter_number) + "Decision: {give, ng, None};\n"
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
            for candidate_number in range(1, self.number_of_candidates + 1):
                evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Vote" + str(candidate_number) + " or\n"
            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"
        for voter_number in range(1, self.number_of_voters + 1):
            evolution += "\t\tvoter" + str(voter_number) + "Decided=true if\n"
            evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Give or\n"
            evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Ng;\n"
            evolution += "\t\tvoter" + str(voter_number) + "Decision=give if\n"
            evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Give;\n"
            evolution += "\t\tvoter" + str(voter_number) + "Decision=ng if\n"
            evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Ng;\n"
            evolution += "\t\tvoter" + str(voter_number) + "Pun=pun if\n"
            evolution += f"\t\t\tCoercer.Action=Pun{voter_number} and (protection=low or voter{voter_number}Decision=give);\n"
            evolution += "\t\tvoter" + str(voter_number) + "Pun=np if\n"
            evolution += f"\t\t\tCoercer.Action=Np{voter_number} or (protection=high and voter{voter_number}Decision=ng);\n"
        evolution += f"\t\tprotection=low if\nEA.Action=Low;\n"
        evolution += f"\t\tprotection=high if\nEA.Action=High;\n"
        evolution += "\tend Evolution\n"
        return evolution

    def __create_election_authority(self):
        player = "Agent EA\n"
        player += self.__create_election_authority_vars()
        player += self.__create_election_authority_actions()
        player += self.__create_election_authority_protocol()
        player += self.__create_election_authority_evolution()
        player += "end Agent\n\n"
        return player

    def __create_election_authority_vars(self):
        vars = "\tVars:\n"
        vars += "\t\tinit: boolean;\n"
        vars += "\tend Vars\n"
        return vars

    def __create_election_authority_actions(self):
        actions = "\tActions = {Low, High, Wait};\n"
        return actions

    def __create_election_authority_protocol(self):
        protocol = "\tProtocol:\n"
        protocol += "\t\tinit=true: {High, Low};\n"
        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_election_authority_evolution(self, ):
        evolution = "\tEvolution:\n"
        evolution += "\t\tinit=false if Action=High or Action=Low;\n"
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
            protocol += "\t\tEnvironment.voter" + str(voter_number) + "Voted=true and Environment.voter" + str(
                voter_number) + "Pun=None and Environment.voter" + str(voter_number) + "Decided=true: {Pun" + str(
                voter_number) + ", Np" + str(voter_number) + ", Wait};\n"
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
        lobsvars += "voter" + str(voter_number) + "Voted, voter" + str(voter_number) + "Pun, voter" + str(
            voter_number) + "Decided"
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
        for candidate_number in range(1, self.number_of_candidates + 1):
            actions += "Vote" + str(candidate_number) + ", "

        actions += "Give, Ng, "
        actions += "Wait};\n"
        return actions

    def __create_voter_protocol(self):
        protocol = "\tProtocol:\n"
        protocol += "\t\t(Environment.protection = high or Environment.protection = low) and vote=0: {"
        for candidate_number in range(1, self.number_of_candidates + 1):
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
            init_states += "Voter" + str(voter_number) + ".vote=0 and Voter" + str(
                voter_number) + ".decision=None and Environment.voter" + str(
                voter_number) + "Voted=false and Environment.voter" + str(
                voter_number) + "Pun=None and Environment.voter" + str(
                voter_number) + "Decided=false and Environment.voter" + str(voter_number) + "Decision=None and "
        init_states += "Coercer.x=false and EA.init=true and Environment.protection=None"
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
        formulae += "\t#PR [[env]] (Environment, env) <<e>> (EA, e) [[c]] (Coercer, c) <<v>> (Voter1, v)"
        for voter_id in range(2, self.number_of_voters + 1):
            formulae += f" [[v{voter_id}]] (Voter{voter_id}, v{voter_id})"
        formulae += "F (Voter1Voted1 and Voter1Finish and !Voter1Punished);\n"
        formulae += "end Formulae\n\n"
        return formulae