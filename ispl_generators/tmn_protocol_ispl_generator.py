import itertools
import random
from tools.string_tools import StringTools


class TmnProtocolIsplGenerator:
    ispl_model = ""
    agents = ["alice", "bob", "server", "attacker"]
    no_messages = 3

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

        for message_no in range(1, self.no_messages + 1):
            obsvars += f"\t\tmessage{message_no}Key : " + "{"

            for agent_name in self.agents:
                obsvars += f"{agent_name}KeyM, "

            obsvars = obsvars.rstrip(" ,")
            obsvars += "};\n"

        for message_no in range(1, self.no_messages + 1):
            obsvars += f"\t\tmessage{message_no}Content : " + "{"

            for agent_name in self.agents:
                obsvars += f"{agent_name}KeyM, "

            obsvars = obsvars.rstrip(" ,")
            obsvars += "};\n"

        obsvars += "\t\tprotocol : boolean;\n"

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

        for agent_name in self.agents:
            vars += f"\t\t{agent_name}Key:boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no}:" + "{none,plain,encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_alice_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'alice':
                    continue
                agent_name = StringTools.to_first_word(agent_name)
                actions += f"sendMessage{message_no}To{agent_name}, "

        actions += "Wait};\n"
        return actions

    def __create_alice_protocol(self):
        protocol = "\tProtocol:\n"

        for message_no in range(1, self.no_messages + 1):
            for agent_name in self.agents:
                protocol += f"\t\t(message{message_no}=encrypted and {agent_name}Key=true and Environment.message{message_no}Key={agent_name}KeyM) or\n"

            protocol = protocol.rstrip("\nro ")
            protocol += ": {" + f"decryptMessage{message_no}" + "};\n"

        for message_no in range(1, self.no_messages + 1):
            protocol += f"\t\t(message{message_no}=plain and Environment.protocol=false): " + "{"

            for agent_name in self.agents:
                if agent_name == 'alice':
                    continue

                agent_name = StringTools.to_first_word(agent_name)
                protocol += f"sendMessage{message_no}To{agent_name}, "

            protocol += "Wait};\n"

        protocol += "\t\t(message1=plain and Environment.protocol=true): {sendMessage1ToServer};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_alice_evolution(self):
        evolution = "\tEvolution:\n"

        for agent_name in self.agents:
            evolution += f"\t\t{agent_name}Key=true if\n"

            for message_no in range(1, self.no_messages + 1):
                evolution += f"\t\t\t(Action=decryptMessage{message_no} and Environment.message{message_no}Content={agent_name}KeyM) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=plain if Action=decryptMessage{message_no};\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=encrypted if\n"
            evolution += f"\t\t\tmessage{message_no}=none and (\n"

            for agent_name in self.agents:
                if agent_name == "alice":
                    continue

                agent_name = StringTools.to_first_word(agent_name)
                evolution += f"\t\t\t{agent_name}.Action=sendMessage{message_no}ToAlice or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

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

        for agent_name in self.agents:
            vars += f"\t\t{agent_name}Key:boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no}:" + "{none,plain,encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_bob_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'bob':
                    continue
                agent_name = StringTools.to_first_word(agent_name)
                actions += f"sendMessage{message_no}To{agent_name}, "

        actions += "Wait};\n"
        return actions

    def __create_bob_protocol(self):
        protocol = "\tProtocol:\n"

        for message_no in range(1, self.no_messages + 1):
            for agent_name in self.agents:
                protocol += f"\t\t(message{message_no}=encrypted and {agent_name}Key=true and Environment.message{message_no}Key={agent_name}KeyM) or\n"

            protocol = protocol.rstrip("\nro ")
            protocol += ": {" + f"decryptMessage{message_no}" + "};\n"

        for message_no in range(1, self.no_messages + 1):
            protocol += f"\t\t(message{message_no}=plain and Environment.protocol=false): " + "{"

            for agent_name in self.agents:
                if agent_name == 'bob':
                    continue

                agent_name = StringTools.to_first_word(agent_name)
                protocol += f"sendMessage{message_no}To{agent_name}, "

            protocol += "Wait};\n"

        protocol += "\t\t(message2=plain and Environment.protocol=true): {sendMessage2ToServer};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_bob_evolution(self):
        evolution = "\tEvolution:\n"

        for agent_name in self.agents:
            evolution += f"\t\t{agent_name}Key=true if\n"

            for message_no in range(1, self.no_messages + 1):
                evolution += f"\t\t\t(Action=decryptMessage{message_no} and Environment.message{message_no}Content={agent_name}KeyM) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=plain if Action=decryptMessage{message_no};\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=encrypted if\n"
            evolution += f"\t\t\tmessage{message_no}=none and (\n"

            for agent_name in self.agents:
                if agent_name == "bob":
                    continue

                agent_name = StringTools.to_first_word(agent_name)
                evolution += f"\t\t\t{agent_name}.Action=sendMessage{message_no}ToBob or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

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

        for agent_name in self.agents:
            vars += f"\t\t{agent_name}Key:boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no}:" + "{none,plain,encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_server_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'server':
                    continue
                agent_name = StringTools.to_first_word(agent_name)
                actions += f"sendMessage{message_no}To{agent_name}, "

        actions += "Wait};\n"
        return actions

    def __create_server_protocol(self):
        protocol = "\tProtocol:\n"

        for message_no in range(1, self.no_messages + 1):
            for agent_name in self.agents:
                protocol += f"\t\t(message{message_no}=encrypted and {agent_name}Key=true and Environment.message{message_no}Key={agent_name}KeyM) or\n"

            protocol = protocol.rstrip("\nro ")
            protocol += ": {" + f"decryptMessage{message_no}" + "};\n"

        for message_no in range(1, self.no_messages + 1):
            protocol += f"\t\t(message{message_no}=plain and Environment.protocol=false): " + "{"

            for agent_name in self.agents:
                if agent_name == 'server':
                    continue

                agent_name = StringTools.to_first_word(agent_name)
                protocol += f"sendMessage{message_no}To{agent_name}, "

            protocol += "Wait};\n"

        protocol += "\t\t(message3=plain and Environment.protocol=true): {sendMessage3ToAlice};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_server_evolution(self):
        evolution = "\tEvolution:\n"

        for agent_name in self.agents:
            evolution += f"\t\t{agent_name}Key=true if\n"

            for message_no in range(1, self.no_messages + 1):
                evolution += f"\t\t\t(Action=decryptMessage{message_no} and Environment.message{message_no}Content={agent_name}KeyM) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=plain if Action=decryptMessage{message_no};\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=encrypted if\n"
            evolution += f"\t\t\tmessage{message_no}=none and (\n"

            for agent_name in self.agents:
                if agent_name == "server":
                    continue

                agent_name = StringTools.to_first_word(agent_name)
                evolution += f"\t\t\t{agent_name}.Action=sendMessage{message_no}ToServer or\n"

            evolution = evolution.rstrip("\nro")
            evolution += ");\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=plain if\n"
            for agent_name in self.agents:
                for key_name in self.agents:
                    evolution += f"\t\t\t({agent_name}Key=true and Environment.message{message_no}Content={agent_name}KeyM and {key_name}Key=true and Environment.message{message_no}Key={key_name}KeyM) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

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

        for agent_name in self.agents:
            vars += f"\t\t{agent_name}Key:boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no}:" + "{none,plain,encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_attacker_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'attacker':
                    continue
                agent_name = StringTools.to_first_word(agent_name)
                actions += f"sendMessage{message_no}To{agent_name}, "

        actions += "Wait};\n"
        return actions

    def __create_attacker_protocol(self):
        protocol = "\tProtocol:\n"

        for message_no in range(1, self.no_messages + 1):
            for agent_name in self.agents:
                protocol += f"\t\t(message{message_no}=encrypted and {agent_name}Key=true and Environment.message{message_no}Key={agent_name}KeyM) or\n"

            protocol = protocol.rstrip("\nro ")
            protocol += ": {" + f"decryptMessage{message_no}" + "};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_attacker_evolution(self):
        evolution = "\tEvolution:\n"

        for agent_name in self.agents:
            evolution += f"\t\t{agent_name}Key=true if\n"

            for message_no in range(1, self.no_messages + 1):
                evolution += f"\t\t\t(Action=decryptMessage{message_no} and Environment.message{message_no}Content={agent_name}KeyM) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for message_no in range(1, self.no_messages + 1):
            evolution += f"\t\tmessage{message_no}=encrypted if\n"
            evolution += f"\t\t\tmessage{message_no}=none and\n"
            evolution += "\t\t\t(\n"
            for agent_name in self.agents:
                agent_name = StringTools.to_first_word(agent_name)
                for second_agent in self.agents:
                    second_agent = StringTools.to_first_word(second_agent)
                    if agent_name == second_agent:
                        continue

                    evolution += f"\t\t\t{agent_name}.Action=sendMessage{message_no}To{second_agent} or\n"

            evolution = evolution.rstrip("\nro")
            evolution += ");\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self):
        evaluation = "Evaluation\n"
        evaluation += "\tkeyExchanged if Alice.bobKey=true;\n"
        evaluation += "\tcompromised if Attacker.aliceKey=true or Attacker.bobKey=true or Attacker.serverKey=true;\n"
        evaluation += "end Evaluation\n\n"
        return evaluation

    def __create_init_states(self):
        init_states = "InitStates\n"
        keys = ["server", "server", "alice"]

        init_states += "\tEnvironment.protocol=false and\n"

        for message_no in range(1, self.no_messages + 1):
            init_states += f"\tEnvironment.message{message_no}Key={keys[message_no-1]}KeyM and\n"

        keys = ["alice", "bob", "bob"]

        for message_no in range(1, self.no_messages + 1):
            init_states += f"\tEnvironment.message{message_no}Content={keys[message_no-1]}KeyM and\n"

        for agent_name in self.agents:
            agent_name = StringTools.to_first_word(agent_name)

            for message_no in range(1, self.no_messages + 1):
                msg = "none"

                if agent_name == "Alice" and message_no == 1:
                    msg = "plain"
                elif agent_name == "Bob" and message_no == 2:
                    msg = "plain"

                init_states += f"\t{agent_name}.message{message_no}={msg} and\n"

        for agent_name in self.agents:
            for key_name in self.agents:
                know_key = "false"

                if agent_name == key_name:
                    know_key = "true"

                init_states += f"\t{StringTools.to_first_word(agent_name)}.{key_name}Key={know_key} and\n"

        init_states = init_states.rstrip("\ndna ")
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


tmn_protocol_ispl_generator = TmnProtocolIsplGenerator()

f = open("tmn_protocol.ispl", "w")
f.write(tmn_protocol_ispl_generator.create_ispl_model())
f.close()

print("Done. Created model saved in tmn_protocol.ispl")
