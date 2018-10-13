import itertools
import random
from tools.string_tools import StringTools


class CompTmnProtocolIsplGenerator:
    ispl_model = ""
    agents = ["alice", "bob", "server", "attacker"]
    no_messages = 3
    no_keys = 3
    min_val = 1
    max_val = 100

    def __init__(self):
        return

    def create_ispl_model(self):
        self.ispl_model += self.__define_semantics()
        self.ispl_model += self.__create_environment()
        self.ispl_model += self.__create_alice()
        self.ispl_model += self.__create_bob()
        self.ispl_model += self.__create_server()
        self.ispl_model += self.__create_attacker()

        self.ispl_model += self.__create_evaluation()
        self.ispl_model += self.__create_init_states()
        self.ispl_model += self.__create_groups()
        self.ispl_model += self.__create_formulae()
        return self.ispl_model

    def __define_semantics(self):
        semantics = "Semantics=SingleAssignment;\n\n"
        return semantics

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

    def __create_alice(self):
        agent = "Agent Alice\n"
        agent += self.__create_alice_vars()
        agent += self.__create_alice_actions()
        agent += self.__create_alice_protocol()
        agent += self.__create_alice_evolution()
        agent += "end Agent\n\n"
        return agent

    def __create_alice_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_alice_vars(self):
        vars = "\tVars:\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no} : {self.min_val} .. {self.max_val};\n"

        for key_no in range(1, self.no_keys + 1):
            vars += f"\t\tkey{key_no} : {self.min_val} .. {self.max_val};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_alice_actions(self):
        actions = "\tActions = {"

        actions += "Wait};\n"
        return actions

    def __create_alice_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_alice_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_bob(self):
        agent = "Agent Bob\n"
        agent += self.__create_bob_vars()
        agent += self.__create_bob_actions()
        agent += self.__create_bob_protocol()
        agent += self.__create_bob_evolution()
        agent += "end Agent\n\n"
        return agent

    def __create_bob_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_bob_vars(self):
        vars = "\tVars:\n"

        vars += "\tend Vars\n"
        return vars

    def __create_bob_actions(self):
        actions = "\tActions = {"

        actions += "Wait};\n"
        return actions

    def __create_bob_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_bob_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_server(self):
        agent = "Agent Server\n"
        agent += self.__create_server_vars()
        agent += self.__create_server_actions()
        agent += self.__create_server_protocol()
        agent += self.__create_server_evolution()
        agent += "end Agent\n\n"
        return agent

    def __create_server_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_server_vars(self):
        vars = "\tVars:\n"

        vars += "\tend Vars\n"
        return vars

    def __create_server_actions(self):
        actions = "\tActions = {"

        actions += "Wait};\n"
        return actions

    def __create_server_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_server_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_attacker(self):
        agent = "Agent Attacker\n"
        agent += self.__create_attacker_vars()
        agent += self.__create_attacker_actions()
        agent += self.__create_attacker_protocol()
        agent += self.__create_attacker_evolution()
        agent += "end Agent\n\n"
        return agent

    def __create_attacker_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_attacker_vars(self):
        vars = "\tVars:\n"

        vars += "\tend Vars\n"
        return vars

    def __create_attacker_actions(self):
        actions = "\tActions = {"

        actions += "Wait};\n"
        return actions

    def __create_attacker_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_attacker_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self):
        evaluation = "Evaluation\n"

        evaluation += "end Evaluation\n\n"
        return evaluation

    def __create_init_states(self):
        init_states = "InitStates\n"

        init_states += ";\nend InitStates\n\n"
        return init_states

    def __create_groups(self):
        groups = "Groups\n"
        groups += "\ttrusted={Alice, Bob, Server};\n"
        groups += "\tatk={Attacker};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self):
        formulae = "Formulae\n"
        formulae += "\t<trusted>F keyExchanged;\n"
        formulae += "\t<trusted>G !compromised;\n"
        formulae += "end Formulae\n\n"
        return formulae


tmn_protocol_ispl_generator = CompTmnProtocolIsplGenerator()

f = open("comp_tmn_protocol.ispl", "w")
f.write(tmn_protocol_ispl_generator.create_ispl_model())
f.close()

print("Done. Created model saved in comp_tmn_protocol.ispl")
