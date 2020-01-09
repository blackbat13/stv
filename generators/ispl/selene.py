import argparse
import itertools


class SeleneModelIsplGenerator:
    # TODO: integrate with IsplGenerator class
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

        for i in range(1, self.number_of_voters + 1):
            obsvars += "\t\tpublicTracker" + str(i) + ": 0.." + str(self.number_of_voters) + ";\n"
            obsvars += "\t\tpublicVote" + str(i) + ": 0.." + str(self.number_of_candidates) + ";\n"

        obsvars += "\t\tvotesPublished: boolean;\n"
        obsvars += "\t\tvotingStarted: boolean;\n"
        obsvars += "\tend Obsvars\n"
        return obsvars

    def __create_environment_vars(self):
        vars = "\tVars:\n"

        for i in range(1, self.number_of_voters + 1):
            vars += "\t\ttracker" + str(i) + ": 0.." + str(self.number_of_voters) + ";\n"
            vars += "\t\tvoter" + str(i) + "Voted: boolean;\n"
            vars += "\t\tvoter" + str(i) + "Vote: 0.." + str(self.number_of_candidates) + ";\n"
            vars += "\t\tvoter" + str(i) + "TrackerSet: boolean;\n"
            vars += "\t\tvoter" + str(i) + "OwnedTracker: 0.." + str(self.number_of_voters) + ";\n"

        vars += "\tend Vars\n"
        return vars

    def __create_environment_actions(self):
        actions = "\tActions = {PublishVotes, "
        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_voters + 1):
                actions += "SetTracker" + str(i) + "To" + str(j) + ", "
        actions += "StartVoting, Wait};\n"
        return actions

    def __create_environment_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += "\t\t"
        for i in range(1, self.number_of_voters + 1):
            protocol += "voter" + str(i) + "Voted=true and "

        protocol += "publicVote1=0: {PublishVotes};\n"

        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_voters + 1):
                protocol += "\t\ttracker" + str(i) + "=0 and voter" + str(j) + "TrackerSet=false: {SetTracker" + str(
                    i) + "To" + str(j) + "};\n"

        protocol += "\t\t"
        for i in range(1, self.number_of_voters + 1):
            protocol += "tracker" + str(i) + ">0 and "

        protocol += "votingStarted=false: {StartVoting};\n"
        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_environment_evolution(self):
        evolution = "\tEvolution:\n"

        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_voters + 1):
                evolution += "\t\tpublicTracker" + str(i) + "=" + str(j) + " if\n"
                evolution += "\t\t\tAction=PublishVotes and\n"
                evolution += "\t\t\ttracker" + str(i) + "=" + str(j) + ";\n"

        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_candidates + 1):
                for k in range(1, self.number_of_voters + 1):
                    evolution += "\t\tpublicVote" + str(i) + "=" + str(j) + " if\n"
                    evolution += "\t\t\tAction=PublishVotes and\n"
                    evolution += "\t\t\tvoter" + str(k) + "Vote=" + str(j) + " and\n"
                    evolution += "\t\t\ttracker" + str(i) + "=" + str(k) + ";\n"

        for voter_number in range(1, self.number_of_voters + 1):
            evolution += "\t\tvoter" + str(voter_number) + "Voted=true if\n"
            for candidate_number in range(1, self.number_of_candidates + 1):
                evolution += "\t\t\tVoter" + str(voter_number) + ".Action=Vote" + str(candidate_number) + " or\n"
            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_candidates + 1):
                evolution += "\t\tvoter" + str(i) + "Vote=" + str(j) + " if\n"
                evolution += "\t\t\tVoter" + str(i) + ".Action=Vote" + str(j) + ";\n"

        for i in range(1, self.number_of_voters + 1):
            evolution += "\t\tvoter" + str(i) + "TrackerSet=true if\n"
            for j in range(1, self.number_of_voters + 1):
                evolution += "\t\t\tAction=SetTracker" + str(j) + "To" + str(i) + " or\n"
            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_voters + 1):
                evolution += "\t\ttracker" + str(i) + "=" + str(j) + " if\n"
                evolution += "\t\t\tAction=SetTracker" + str(i) + "To" + str(j) + ";\n"

        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_voters + 1):
                evolution += "\t\tvoter" + str(i) + "OwnedTracker=" + str(j) + " if\n"
                evolution += "\t\t\tVoter" + str(i) + ".Action=FetchGoodTracker and "
                evolution += "tracker" + str(j) + "=" + str(i) + ";\n"

        for i in range(1, self.number_of_voters + 1):
            for j in range(1, self.number_of_voters + 1):
                for l in range(1, self.number_of_voters + 1):
                    for k in range(1, self.number_of_candidates + 1):
                        evolution += "\t\tvoter" + str(i) + "OwnedTracker=" + str(j) + " if\n"
                        evolution += "\t\t\tVoter" + str(i) + ".Action=FetchTrackerForVote" + str(k) + " and "
                        evolution += "voter" + str(l) + "Vote=" + str(k) + " and "
                        evolution += "tracker" + str(j) + "=" + str(l) + ";\n"

        evolution += "\t\tvotesPublished=true if Action=PublishVotes;\n"
        evolution += "\t\tvotingStarted=true if Action=StartVoting;\n"

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

        lobsvars += "};\n"
        return lobsvars

    def __create_coercer_vars(self):
        vars = "\tVars:\n"
        for i in range(1, self.number_of_voters + 1):
            vars += '\t\ttracker' + str(i) + ": 0.." + str(self.number_of_voters) + ";\n"
        vars += "\tend Vars\n"
        return vars

    def __create_coercer_actions(self):
        actions = "\tActions = {"

        actions += "Wait};\n"
        return actions

    def __create_coercer_protocol(self):
        protocol = "\tProtocol:\n"
        protocol += "\t\tEnvironment.votesPublished=false: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_coercer_evolution(self, ):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_voter(self, voter_number):
        player = "Agent Voter" + str(voter_number) + "\n"

        player += self.__create_voter_lobsvars(voter_number)
        player += self.__create_voter_vars()
        player += self.__create_voter_actions()
        player += self.__create_voter_protocol(voter_number)
        player += self.__create_voter_evolution()
        player += "end Agent\n\n"
        return player

    def __create_voter_lobsvars(self, voter_number):
        lobsvars = "\tLobsvars = {"
        lobsvars += "voter" + str(voter_number) + "OwnedTracker"
        lobsvars += "};\n"
        return lobsvars

    def __create_voter_vars(self):
        vars = "\tVars:\n"

        vars += "\t\tvote: 0.." + str(self.number_of_candidates) + ";\n"

        vars += "\tend Vars\n"
        return vars

    def __create_voter_actions(self):
        actions = "\tActions = {"

        for i in range(1, self.number_of_candidates + 1):
            actions += "Vote" + str(i) + ", "

        for i in range(1, self.number_of_candidates + 1):
            actions += "FetchTrackerForVote" + str(i) + ", "

        actions += "FetchGoodTracker, "
        actions += "Wait};\n"
        return actions

    def __create_voter_protocol(self, voter_number):
        protocol = "\tProtocol:\n"

        protocol += "\t\tvote=0 and Environment.votingStarted=true: {"
        for i in range(1, self.number_of_candidates + 1):
            protocol += "Vote" + str(i) + ", "

        protocol += "Wait};\n"

        protocol += "\t\tvote>0 and Environment.voter" + str(
            voter_number) + "OwnedTracker=0 and Environment.votesPublished=true: {"
        for i in range(1, self.number_of_candidates + 1):
            protocol += "FetchTrackerForVote" + str(i) + ", "
        protocol += "FetchGoodTracker, Wait};\n"
        protocol += "\t\tOther: {Wait};\n"

        protocol += "\tend Protocol\n"
        return protocol

    def __create_voter_evolution(self, ):
        evolution = "\tEvolution:\n"

        for i in range(1, self.number_of_candidates + 1):
            evolution += "\t\tvote=" + str(i) + " if Action=Vote" + str(i) + ";\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self):
        evaulation = "Evaluation\n"
        evaulation += "\tVoter1Voted1 if Voter1.vote=1;\n"
        evaulation += "end Evaluation\n\n"
        return evaulation

    def __create_init_states(self):
        init_states = "InitStates\n"
        init_states += "\t\t"
        # Set trackers to voter number
        for i in range(1, self.number_of_voters + 1):
            init_states += "Voter" + str(i) + ".vote=0 and "
            init_states += "Environment.publicTracker" + str(i) + "=0 and "
            init_states += "Environment.publicVote" + str(i) + "=0 and "
            init_states += "Environment.tracker" + str(i) + "=" + str(0) + " and "
            init_states += "Environment.voter" + str(i) + "Voted=false and "
            init_states += "Environment.voter" + str(i) + "Vote=0 and "
            init_states += "Environment.voter" + str(i) + "TrackerSet=false and "
            init_states += "Environment.voter" + str(i) + "OwnedTracker=0 and "
            init_states += "Coercer.tracker" + str(i) + "=0 and"

        init_states += "Environment.votesPublished=false and "
        init_states += "Environment.votingStarted=false"
        init_states += ";\n"
        init_states += "end InitStates\n\n"
        return init_states

    def __create_groups(self):
        groups = "Groups\n"
        for voter_number in range(1, self.number_of_voters + 1):
            groups += "\tv" + str(voter_number) + "={Voter" + str(voter_number) + "};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self):
        formulae = "Formulae\n"
        formulae += "\t<v1>F(Voter1Voted1);\n"
        formulae += "end Formulae\n\n"
        return formulae


class SeleneModelMkIsplGenerator:
    # TODO: integrate with IsplGenerator class
    def __init__(self, votersNo, ballotsNo, maxCoerced, maxWaitingForVotes, maxWaitingForHelp, coalitionSize):

        self.votersNo = votersNo
        self.ballotsNo = ballotsNo
        self.maxCoerced = maxCoerced
        self.voteWait = maxWaitingForVotes
        self.helpWait = maxWaitingForHelp
        self.clSize = coalitionSize

        self.agentTxt = "-- ISPL model of SELENE protocol for {0} voters, {1} candidates, --\n".format(str(votersNo),
                                                                                                       str(ballotsNo))
        self.agentTxt += "-- {0} voters accessible for the coercer, and waiting time {1}.  --\n\n\n".format(
            str(maxCoerced), str(maxWaitingForVotes))

        self.agentTxt += "Semantics = SA;\n\n"
        self.agentTxt += self.buildEnvironment()
        self.agentTxt += self.buildElectionDefenseSystem()
        for i in range(1, self.votersNo + 1):
            self.agentTxt += self.buildVoter(i)
        self.agentTxt += self.buildCoercer()
        self.agentTxt += self.buildEvaluation()
        self.agentTxt += self.buildInitStates()
        self.agentTxt += self.buildGroups()
        self.agentTxt += self.buildFormulae()

    def getISPL(self):
        return self.agentTxt

    def buildEnvironment(self):

        txt = "Agent Environment\n\nObsvars:\n"

        # building Obsvars and Vars
        txt += "\t-- this is WBB\n"
        txt += "".join(
            ["\tpublicVote{0}: 0..{1};\n".format(str(i), str(self.ballotsNo)) for i in range(1, self.votersNo + 1)])
        txt += "\tvoteWait: 0..{};\n".format(self.voteWait + 2)
        txt += "\tdefenseTimer: 0..{};\n".format(self.helpWait + 2)
        txt += "\n\tvotesPublished: boolean;\n\tvotingStarted: boolean;\n\tvotingFinished: boolean;\n"
        txt += "end Obsvars\n\nVars:\n"

        txt += "\t-- observable to ElectionDefenseSystem only\n"
        for i in range(1, self.votersNo + 1):
            txt += "\ttracker{}: 0..{};\n".format(str(i), str(self.votersNo))
            txt += "\tvoter{}Vote: 0..{};\n".format(str(i), str(self.ballotsNo))
            txt += "\tvoter{}TrackerSet: boolean;\n\n".format(str(i))

        txt += "\t-- observable to resp. Voters and ElectionDefenseSystem\n"
        for i in range(1, self.votersNo + 1):
            txt += "\tvoter{}OwnedTracker: 0..{};\n".format(str(i), str(self.votersNo))
            txt += "\tvoteDemandedFromVoter{}: 0..{};\n".format(str(i), str(self.ballotsNo))

        txt += "\n\t-- observable to Coercer and resp. Voters"
        for i in range(1, self.votersNo + 1):
            txt += "\n\tfalseOrCopiedTrackerForVoter{}: 0..{};".format(str(i), str(self.votersNo))

        txt += "\nend Vars\n\n"

        # building Actions
        txt += "Actions = {PublishVotes, StartVoting, Wait, "
        txt += ", ".join(["SetTracker{}To{}".format(str(i), str(j)) for i in range(1, self.votersNo + 1) \
                          for j in range(1, self.votersNo + 1)])
        txt += "};\n\n"

        # building Protocol
        txt += "Protocol:\n"
        txt += "\n".join(
            ["\ttracker{0} = 0 and voter{1}TrackerSet = false: {{SetTracker{0}To{1}}};".format(str(i), str(j)) \
             for i in range(1, self.votersNo + 1) for j in range(1, self.votersNo + 1)])

        txt += "\n\n\t"
        txt += " and ".join(["tracker{} > 0".format(str(i)) for i in range(1, self.votersNo + 1)])
        txt += " and votingStarted = false: {StartVoting};\n"

        txt += "\n\t"
        txt += " and ".join(["voter{}Vote > 0".format(str(i)) for i in range(1, self.votersNo + 1)])
        txt += " and votesPublished = false: {PublishVotes};\n"

        txt += "\n\tOther: {Wait};\n"

        txt += "\nend Protocol"

        # building Evolution
        txt += "\n\nEvolution:\n"

        # Evolution: trackers
        txt += "\n\t-- setting trackers\n"
        txt += "\n".join(["\ttracker{0} = {1} if Action = SetTracker{0}To{1};".format(str(i), str(j)) \
                          for i in range(1, self.votersNo + 1) \
                          for j in range(1, self.votersNo + 1)])
        txt += "\n"

        for j in range(1, self.votersNo + 1):
            txt += "\n\tvoter{}TrackerSet = true if \n\t".format(str(j))
            txt += " or ".join(["Action = SetTracker{0}To{1}".format(str(i), str(j)) \
                                for i in range(1, self.votersNo + 1)])
            txt += ";\n"

        # Evolution: voting
        txt += "\n\t-- voting\n"
        txt += "\tvotingStarted = true if Action = StartVoting;\n\n"
        txt += "\n".join(["\tvoter{0}Vote = {1} if Voter{0}.Action = Vote{1};".format(str(i), str(j)) \
                          for i in range(1, self.votersNo + 1) \
                          for j in range(1, self.ballotsNo + 1)])
        txt += "\n\tvoteWait = voteWait + 1 if votesPublished = false and votingStarted = true;"

        # Evolution: publishing votes
        txt += "\n\n\t-- publishing votes\n"
        txt += "\tvotesPublished = true if Action = PublishVotes;\n\n"

        txt += "\n".join([
            "\tpublicVote{0} = {2} if Action = PublishVotes and voter{1}Vote = {2} and tracker{0} = {1};".format(
                str(Ntrackr), str(Nvotr), str(Nballot)) \
            for Ntrackr in range(1, self.votersNo + 1) \
            for Nvotr in range(1, self.votersNo + 1)
            for Nballot in range(1, self.ballotsNo + 1)])

        # Evolution: fetching correct trackers
        txt += "\n\n\t-- fetching correct trackers\n"
        txt += "\n".join([
            "\tvoter{0}OwnedTracker = {1} if Voter{0}.Action = FetchGoodTracker and tracker{1} = {0};".format(
                str(i), str(j)) \
            for i in range(1, self.votersNo + 1) for j in range(1, self.votersNo + 1)])

        # Evolution: copying true trackers
        txt += "\n\n\t-- copying true trackers\n"
        txt += "\n".join([
            "\tfalseOrCopiedTrackerForVoter{0} = {1} if Voter{0}.Action = CopyRealTracker and tracker{1} = {0};".format(
                str(i), str(j)) \
            for i in range(1, self.votersNo + 1) for j in range(1, self.votersNo + 1)])

        # Evolution: gathering help requests
        txt += "\n\n\t-- gathering help requests\n"
        txt += "\n".join(
            ["\tvoteDemandedFromVoter{0} = {1} if Voter{0}.Action = HelpINeedVote{1};".format(str(i), str(j)) \
             for i in range(1, self.votersNo + 1) for j in range(1, self.ballotsNo + 1)])
        txt += "\n\tdefenseTimer = defenseTimer + 1 if votesPublished = true and votingFinished = false;\n"

        # Evolution: tracker forging, complementary to ElectionDefenseSystem actions
        txt += "\n\n\t-- falsifying trackers\n"
        txt += "\n".join([
            "\tfalseOrCopiedTrackerForVoter{0} = {1} if ElectionDefenseSystem.Action = SetFalseTrackerForVoter{0}To{1} and !(Voter{0}.Action = CopyRealTracker);".format(
                str(i), str(j)) \
            for i in range(1, self.votersNo + 1) for j in range(1, self.votersNo + 1)])

        # Evolution: finish voting
        txt += "\n\n\t-- end voting\n"
        txt += "\tvotingFinished = true if " + " and ".join(
            ["Voter{}.Action = Finish".format(str(i)) for i in range(1, self.votersNo + 1)]) + ";\n"

        txt += "\nend Evolution\n\nend Agent\n\n"

        return txt

    def buildElectionDefenseSystem(self):

        txt = "\nAgent ElectionDefenseSystem\n\n"

        # mark actions observable by this agent
        txt += "\tLobsvars = {" + ", ".join([
            "tracker{0}, voter{0}Vote, voter{0}TrackerSet, voter{0}OwnedTracker, voteDemandedFromVoter{0}".format(
                str(i)) for i in range(1, self.votersNo + 1)]) + "};\n"

        # building Vars
        txt += "\nVars:\n"
        txt += "\n".join(["\tfalseTrackerSentToVoter{}: boolean;".format(str(i)) for i in range(1, self.votersNo + 1)])
        txt += "\nend Vars\n\n"

        # building Actions
        txt += "\tActions = {"
        txt += ", ".join(["SetFalseTrackerForVoter{0}To{1}".format(str(i), str(j)) \
                          for i in range(1, self.votersNo + 1) for j in range(1, self.votersNo + 1)])
        txt += ", Wait};\n\n"

        # building Protocol
        txt += "Protocol:\n"
        txt += "\t-- sending false trackers - possible only once per voter\n"

        for vtr in range(1, self.votersNo + 1):
            txt += "\tfalseTrackerSentToVoter{0} = false and Environment.voteDemandedFromVoter{0} > 0".format(str(vtr))
            txt += "\n\tand Environment.votesPublished = true and Environment.votingFinished = false: {"
            txt += ", ".join(
                ["SetFalseTrackerForVoter{0}To{1}".format(str(vtr), str(i)) for i in range(1, self.votersNo + 1)])
            txt += ", Wait};\n"

        txt += "\n\tOther: {Wait};\n"

        txt += "end Protocol"

        # building Evolution
        txt += "\n\nEvolution:\n"
        for vtr in range(1, self.votersNo + 1):
            txt += "\tfalseTrackerSentToVoter{0} = true if ".format(str(vtr))
            txt += " or ".join(["Action = SetFalseTrackerForVoter{0}To{1}".format(str(vtr), str(i)) \
                                for i in range(1, self.votersNo + 1)])
            txt += ";\n"
        txt += "end Evolution\n\nend Agent\n\n"

        return txt

    def buildVoter(self, vtr):

        txt = "\nAgent Voter{}\n\n".format(str(vtr))

        # mark actions observable by this agent
        txt += "\tLobsvars = {{voter{0}OwnedTracker, falseOrCopiedTrackerForVoter{0}, voteDemandedFromVoter{0}}};\n".format(
            str(vtr))

        # building Vars
        txt += "\nVars:\n"
        txt += "\tvote: 0..{0};\n\tdemandedVote: 0..{0}; --the vote demanded from the voter by the Coercer\n".format(
            str(self.ballotsNo))
        txt += "\thelpRequestSent: boolean; --used so that the voter can ask for help only once\n"
        txt += "\ttrueTrackerCopied: boolean;\n"
        txt += "end Vars\n\n"

        # building Actions
        txt += "\tActions = {"
        txt += ", ".join(["Vote{0}, HelpINeedVote{0}".format(str(i)) for i in range(1, self.ballotsNo + 1)])
        txt += ", FetchGoodTracker, CopyRealTracker, Wait, Finish};\n\n"

        # building Protocol
        txt += "Protocol:\n"

        txt += "\tEnvironment.votingFinished = false and vote = 0 and Environment.votingStarted=true: {"
        txt += ", ".join(["Vote{0}".format(str(i)) for i in range(1, self.ballotsNo + 1)])
        txt += "};\n"

        txt += "\tEnvironment.votingFinished = false and Environment.defenseTimer < {1} and Environment.voter{0}OwnedTracker = 0 and Environment.votesPublished = true: {{FetchGoodTracker}};\n".format(
            str(vtr), str(self.helpWait))
        txt += "\tEnvironment.votingFinished = false and Environment.defenseTimer < {1} and Environment.voter{0}OwnedTracker > 0 and Environment.votesPublished = true and trueTrackerCopied = false: {{CopyRealTracker}};\n".format(
            str(vtr), str(self.helpWait))
        txt += "\tEnvironment.votingFinished = false and Environment.defenseTimer < {0} and helpRequestSent = false and Environment.votesPublished = true: {{".format(
            str(self.helpWait))
        txt += ", ".join(["HelpINeedVote{0}".format(str(i)) for i in range(1, self.ballotsNo + 1)])
        txt += "};\n"

        txt += "\tEnvironment.votingFinished = false and Environment.defenseTimer < {1} and Environment.falseOrCopiedTrackerForVoter{0} > 0 : {{Finish}};".format(
            str(vtr), str(self.helpWait))
        txt += "\n\tEnvironment.votingFinished = false and Environment.defenseTimer = {0} : {{Finish}};".format(
            str(self.helpWait))

        txt += "\n\t!((Environment.voteWait = {0} and vote = 0) or (Environment.defenseTimer = {1} and Environment.votingFinished = false)): {{Wait}};\n".format(
            str(self.voteWait), str(self.helpWait))

        txt += "end Protocol"

        # building Evolution
        txt += "\n\nEvolution:\n"

        txt += "\n".join(["\tvote = {0} if Action = Vote{0};".format(str(i)) for i in range(1, self.ballotsNo + 1)])
        txt += "\n"

        txt += "\n".join(
            ["\tdemandedVote = {0} if Coercer.Action = RequestVote{0}FromVoter{1};".format(str(i), str(vtr)) for i in
             range(1, self.ballotsNo + 1)])

        txt += "\n\thelpRequestSent = true if ("
        txt += " or ".join(["Action = HelpINeedVote{0}".format(str(i)) for i in range(1, self.ballotsNo + 1)])
        txt += ");\n"

        txt += "\ttrueTrackerCopied = true if Action = CopyRealTracker;"

        txt += "\nend Evolution\n\nend Agent\n\n"

        return txt

    def buildCoercer(self):

        txt = "\nAgent Coercer\n\n"

        # mark actions observable by this agent
        txt += "\tLobsvars = {"
        txt += ", ".join(["falseOrCopiedTrackerForVoter{}".format(str(i)) for i in range(1, self.votersNo + 1)])
        txt += "};\n"

        # building Vars
        txt += "\nVars:\n"
        txt += "\t-- the number of voters that the coercer will influence\n"

        txt += "\tcoercedVoters: 0..{0};\n\tmaxCoerced: 0..{1};\n".format(str(self.votersNo), str(self.maxCoerced))

        txt += "".join(["\tvoteDemandedFromVoter{0}: 0..{1};\n".format(str(i), str(self.ballotsNo)) for i in
                        range(1, self.votersNo + 1)])

        txt += "end Vars\n\n"

        # building Actions
        txt += "\tActions = {Wait, "
        txt += ", ".join(["RequestVote{0}FromVoter{1}".format(str(i), str(j)) \
                          for i in range(1, self.ballotsNo + 1) for j in range(1, self.votersNo + 1)])
        txt += "};\n\n"

        # building Protocol
        txt += "Protocol:\n"
        for i in range(1, self.votersNo + 1):
            txt += "\tcoercedVoters < maxCoerced and voteDemandedFromVoter{0} = 0 and Environment.votesPublished = false: {{".format(
                str(i))
            txt += ", ".join(
                ["RequestVote{0}FromVoter{1}".format(str(j), str(i)) for j in range(1, self.ballotsNo + 1)])
            txt += ", Wait};\n"

        txt += "\tOther: {Wait};"

        txt += "\nend Protocol"

        # building Evolution
        txt += "\n\nEvolution:\n"
        txt += "\tcoercedVoters = coercedVoters + 1 if ("

        txt += " or ".join(["Action = RequestVote{0}FromVoter{1}".format(str(i), str(j)) \
                            for i in range(1, self.ballotsNo + 1) for j in range(1, self.votersNo + 1)])
        txt += ");\n"

        txt += "".join(
            ["\n\tvoteDemandedFromVoter{0} = {1} if Action = RequestVote{1}FromVoter{0};".format(str(i), str(j)) \
             for i in range(1, self.votersNo + 1) for j in range(1, self.ballotsNo + 1)])

        txt += "\nend Evolution\n\nend Agent\n\n"

        return txt

    def buildEvaluation(self):

        txt = "\n\nEvaluation\n"

        # this is needed for formula phi_1 from the draft

        txt += "".join(["\tVoter{0}Voted{1} if Voter{0}.vote = {1};\n".format(str(i), str(j)) \
                        for i in range(1, self.votersNo + 1) for j in range(1, self.ballotsNo + 1)])
        txt += "\n\tvotingFinished if Environment.votingFinished = true;\n\n"

        txt += "".join(
            ["\tCoercerReq{1}FromVoter{0} if Coercer.voteDemandedFromVoter{0} = {1};\n".format(str(i), str(j)) \
             for i in range(1, self.votersNo + 1) for j in range(1, self.ballotsNo + 1)])

        txt += "\n\tNotStarted if Environment.votesPublished = false;\n"

        txt += "\n\tObservableThatSomeVoterDidntObey if \n"
        for i in range(1, self.maxCoerced + 1):  # for each coerced voter...
            voter = str(i)
            for j in range(1, self.ballotsNo + 1):  # ...and each vote...
                vote = str(j)
                cclause = "\t(Coercer.voteDemandedFromVoter{0} = {1} and (\n".format(voter, vote)
                # ...go through trackers...
                cclause += " or\n".join([
                    "\t\t(Environment.falseOrCopiedTrackerForVoter{voterNb} = {trackerNb} and !(Environment.publicVote{trackerNb} = {voteExpect}))".format(
                        voterNb=voter, trackerNb=str(k), voteExpect=vote) \
                    for k in range(1, self.votersNo + 1)])

                cclause += "\n\t))"
                if i == self.maxCoerced and j == self.ballotsNo:
                    cclause += ";\n"
                else:
                    cclause += " or\n"

                txt += cclause

        txt += "\n\tObservableRefusalToProvideTracker if\n\t"
        txt += "\n\tor ".join(
            ["(Coercer.voteDemandedFromVoter{0} > 0 and Environment.falseOrCopiedTrackerForVoter{0} = 0)".format(str(i)) \
             for i in range(1, self.maxCoerced + 1)])
        txt += ";\n"

        # some inefficiency here...
        txt += "\n\tObservableInconsistencyinTrackerClaims if\n"
        for i in range(1, self.maxCoerced + 1):  # for each coerced voter...
            voter = str(i)
            cclause = "\t(Coercer.voteDemandedFromVoter{0} > 0 and Environment.falseOrCopiedTrackerForVoter{0} > 0 and (\n\t\t".format(
                voter)
            cclause += "\n\t\tor ".join([
                "(Environment.falseOrCopiedTrackerForVoter{0} = Environment.falseOrCopiedTrackerForVoter{1})".format(
                    voter, str(j)) \
                for j in range(1, self.votersNo + 1) if j != i])
            cclause += ")"

            if i < self.maxCoerced:
                cclause += ") or\n"

            txt += cclause
        txt += ");\n"

        txt += "\nend Evaluation\n"

        return txt

    def buildInitStates(self):

        txt = "\n\nInitStates\n"
        fotv = """
\tVoter{0}.vote = 0 and
\tVoter{0}.demandedVote = 0 and
\tVoter{0}.trueTrackerCopied = false and
\tVoter{0}.helpRequestSent = false
\tand Environment.publicVote{0} = 0
\tand Environment.tracker{0} = 0
\tand Environment.voter{0}Vote = 0
\tand Environment.voter{0}TrackerSet = false
\tand Environment.voter{0}OwnedTracker = 0 
\tand Environment.voteDemandedFromVoter{0} = 0
\tand Environment.falseOrCopiedTrackerForVoter{0} = 0	
\tand Coercer.voteDemandedFromVoter{0} = 0
\tand ElectionDefenseSystem.falseTrackerSentToVoter{0} = false
"""
        txt += "\n\tand\n".join([fotv.format(str(i)) for i in range(1, self.votersNo + 1)])

        txt += """
\tand Environment.votesPublished=false
\tand Environment.votingStarted=false
\tand Environment.votingFinished=false
\tand Coercer.coercedVoters = 0
\tand Environment.defenseTimer=0
"""

        txt += "\tand Coercer.maxCoerced = {0}\n\tand Environment.voteWait=0;\n".format(self.maxCoerced)

        txt += "\nend InitStates\n"

        return txt

    def buildGroups(self):

        txt = "\n\nGroups"
        txt += "\n\tgoodGuys = {ElectionDefenseSystem, "
        txt += ", ".join(["Voter{0}".format(str(i)) for i in range(1, self.votersNo + 1)])
        txt += "};"
        txt += "\n\tgoodGuysSansOne = {ElectionDefenseSystem, "
        txt += ", ".join(["Voter{0}".format(str(i)) for i in range(2, self.votersNo + 1)])
        txt += "};"
        txt += "\n\tcoercer = {Coercer};"
        txt += "\nend Groups\n"

        return txt

    def buildFormulae(self):

        txt = "\n\nFormulae\n"

        nvgroup = ["!Voter{}Voted1".format(str(i)) for i in range(1, self.clSize + 1)]

        firstgroupformula = " and ".join(nvgroup)
        secondgroupformula = " or ".join(nvgroup)
        firstformula = "K(Coercer, (" + " or ".join(nvgroup) + "))"
        secondformula = " or ".join(["K(Coercer, ({}))".format(nvv) for nvv in nvgroup])

        groupformulas = [firstgroupformula, secondgroupformula]
        coercerknowledgeformulas = [firstformula, secondformula]

        formtemplate = "<coercer> F (votingFinished and (("
        formtemplate += "{0}"
        formtemplate += ") ->({1}))"
        formtemplate += ");"

        for gform, cknowform in itertools.product(groupformulas, coercerknowledgeformulas):
            txt += "\n" + formtemplate.format(gform, cknowform)

        txt += "\nend Formulae\n"

        return txt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    votersNo = int(input("Number of voters: "))
    ballotsNo = int(input("number of possible ballots: "))
    maxCoerced = int(input("number of voters coerced by the coercer: "))
    maxWaitingForVotes = int(input("how many steps the environment will wait for votes: "))
    maxWaitingForHelp = int(input("how many steps the environment will wait for help requests, after voting is over: "))
    coaltionSize = int(input("The size of coalitions in formulae 1 and 2: "))
    # parser.add_argument("votersNo", help="the number of voters", type=int)
    # parser.add_argument("ballotsNo", help="the number of possible ballots", type=int)
    # parser.add_argument("maxCoerced", help="the number of voters coerced by the coercer", type=int)
    # parser.add_argument("maxWaitingForVotes", help="how many steps the environment will wait for votes", type=int)
    # parser.add_argument("maxWaitingForHelp",
    #                     help="how many steps the environment will wait for help requests, after voting is over",
    #                     type=int)
    # args = parser.parse_args()
    #
    # if args.maxCoerced > args.votersNo:
    #     print("Error: can't coerce more voters than present (maxCoerced too big).")
    #     sys.exit()

    model = SeleneModelMkIsplGenerator(votersNo, ballotsNo, maxCoerced, maxWaitingForVotes, maxWaitingForHelp,
                                       coaltionSize)

    f = open(
        f'selene_model_{votersNo}_{ballotsNo}_{maxCoerced}_{maxWaitingForVotes}_{maxWaitingForHelp}_{coaltionSize}.ispl',
        "w")
    f.write(model.getISPL())
    f.close()

    # print(model.getISPL())
    print(
        f'Saved model in selene_model_{votersNo}_{ballotsNo}_{maxCoerced}_{maxWaitingForVotes}_{maxWaitingForHelp}_{coaltionSize}.ispl')
