import itertools
import random
from tools.string_tools import StringTools


class TmnProtocolIsplGeneratorV2:
    ispl_model = ""
    agents = ["alice", "bob", "server", "attacker"]
    no_messages = 3

    def __init__(self):
        return

    def create_ispl_model(self):
        self.ispl_model += self.__define_semantics()
        self.ispl_model += self.__create_environment()
        for agent_name in self.agents:
            if agent_name == "attacker":
                continue

            self.ispl_model += self.__create_agent(agent_name)

        self.ispl_model += self.__create_attacker()
        self.ispl_model += self.__create_network()

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
        obsvars += "\t\tprocessingMessage : boolean;\n"
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
        protocol = "\tProtocol:\n\t\tOther: {none};\n\tend Protocol\n"
        return protocol

    def __create_environment_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\t\tprocessingMessage=true if\n"

        for message_content in self.agents:
            message_content = StringTools.capitalize_first_letter(message_content)
            for message_source in self.agents:
                message_source = StringTools.capitalize_first_letter(message_source)
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_encryption in self.agents:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}KeyTo{message_destination}EncryptedWith{message_encryption}Key or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        evolution += "\t\tprocessingMessage=false if\n"

        for message_content in self.agents:
            message_content = StringTools.capitalize_first_letter(message_content)
            for message_destination in self.agents:
                message_destination = StringTools.capitalize_first_letter(message_destination)
                for message_encryption in self.agents:
                    message_encryption = StringTools.capitalize_first_letter(message_encryption)
                    evolution += f"\t\t\tNetwork.Action=Forward{message_content}KeyTo{message_destination}EncryptedWith{message_encryption}Key or \n"

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

        for key_name in self.agents:
            vars += f"\t\t{key_name}Key : " + "{none, plain, encrypted};\n"

        for key_name in self.agents:
            vars += f"\t\t{key_name}KeyEncryptionKey : " + "{"
            for agent_name in self.agents:
                vars += f"{agent_name}Key, "

            vars += "none};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_attacker_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"DecryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'attacker':
                    continue
                agent_name = StringTools.capitalize_first_letter(agent_name)
                actions += f"SendMessage{message_no}To{agent_name}, "

        actions += "Wait};\n"
        return actions

    def __create_attacker_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += self.__create_protocol_decryption()
        protocol += self.__create_protocol_communication("attacker")

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_attacker_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\t\taliceKey=none if aliceKey=none;\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_agent(self, agent_name):
        agent_name = StringTools.capitalize_first_letter(agent_name)
        agent = f"Agent {agent_name}\n"
        agent += self.__create_agent_vars()
        agent += self.__create_agent_actions(agent_name)
        agent += self.__create_agent_protocol(agent_name)
        agent += self.__create_agent_evolution(agent_name)
        agent += "end Agent\n\n"
        return agent

    def __create_agent_actions(self, current_agent_name):
        actions = "\tActions = {"

        current_agent_name = StringTools.capitalize_first_letter(current_agent_name)

        for key_name in self.agents:
            key_name = StringTools.capitalize_first_letter(key_name)
            actions += f"Decrypt{key_name}Key, "
            for agent_name in self.agents:
                agent_name = StringTools.capitalize_first_letter(agent_name)
                if agent_name == current_agent_name:
                    continue
                for encryption_key in self.agents:
                    encryption_key = StringTools.capitalize_first_letter(encryption_key)
                    actions += f"Send{key_name}KeyTo{agent_name}EncryptedWith{encryption_key}Key, "

        actions += "Wait};\n"
        return actions

    def __create_agent_vars(self):
        vars = "\tVars:\n"

        for key_name in self.agents:
            vars += f"\t\t{key_name}Key : " + "{none, plain, encrypted};\n"

        for key_name in self.agents:
            vars += f"\t\t{key_name}KeyEncryptionKey : " + "{"
            for agent_name in self.agents:
                vars += f"{agent_name}Key, "

            vars += "none};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_agent_protocol(self, current_agent_name):
        protocol = "\tProtocol:\n"

        protocol += self.__create_protocol_decryption()
        protocol += self.__create_protocol_communication(current_agent_name)

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_protocol_decryption(self):
        protocol = ""

        for key_name in self.agents:
            protocol += f"\t\t{key_name}Key=encrypted and (\n"
            for agent_name in self.agents:
                protocol += f"\t\t\t({key_name}KeyEncryptionKey={agent_name}Key and {agent_name}Key=plain) or\n"

            protocol = protocol.rstrip("\nro ")
            protocol += f"): decrypt{StringTools.capitalize_first_letter(key_name)}Key;\n"

        return protocol

    def __create_protocol_communication(self, current_agent_name):
        protocol = ""

        current_agent_name = StringTools.capitalize_first_letter(current_agent_name)

        for content_key in self.agents:
            for encryption_key in self.agents:
                protocol += f"\t\t{content_key}Key=plain and {encryption_key}Key=plain and Environment.processingMessage=false: " + "{"
                for agent_name in self.agents:
                    agent_name = StringTools.capitalize_first_letter(agent_name)
                    if agent_name == current_agent_name:
                        continue

                    protocol += f"Send{StringTools.capitalize_first_letter(content_key)}KeyTo{agent_name}EncryptedWith{StringTools.capitalize_first_letter(encryption_key)}Key, "

                protocol += "Wait};\n"

        return protocol

    def __create_agent_evolution(self, current_agent_name):
        evolution = "\tEvolution:\n"

        evolution += self.__create_evolution_key_decryption()
        evolution += self.__create_evolution_message_receiving(current_agent_name)

        evolution += "\tend Evolution\n"
        return evolution

    def __create_evolution_key_decryption(self):
        evolution = ""

        for key_name in self.agents:
            evolution += f"\t\t{key_name}Key=plain if\n"
            evolution += f"\t\t\t{key_name}Key=encrypted and (\n"

            for agent_name in self.agents:
                evolution += f"\t\t\t({key_name}EncryptionKey={agent_name}Key and {agent_name}Key=plain) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        return evolution

    def __create_evolution_message_receiving(self, current_agent_name):
        evolution = ""
        current_agent_name = StringTools.capitalize_first_letter(current_agent_name)

        for received_key in self.agents:
            evolution += f"\t\t{received_key}Key=encrypted if\n"
            evolution += f"\t\t\t{received_key}Key=none and (\n"
            received_key = StringTools.capitalize_first_letter(received_key)
            for encryption_key in self.agents:
                encryption_key = StringTools.capitalize_first_letter(encryption_key)
                evolution += f"\t\t\tNetwork.Action=Forward{received_key}KeyTo{current_agent_name}EncryptedWith{encryption_key}Key or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for received_key in self.agents:
            for encryption_key in self.agents:
                evolution += f"\t\t{received_key}EncryptionKey={encryption_key}Key if\n"
                evolution += f"\t\t\t{received_key}EncryptionKey=none and\n"
                encryption_key = StringTools.capitalize_first_letter(encryption_key)
                evolution += f"\t\t\tNetwork.Action=Forward{StringTools.capitalize_first_letter(received_key)}KeyTo{current_agent_name}EncryptedWith{encryption_key}Key;\n"

        return evolution

    def __create_network(self):
        agent = "Agent Network\n"
        agent += self.__create_network_vars()
        agent += self.__create_network_actions()
        agent += self.__create_network_protocol()
        agent += self.__create_network_evolution()
        agent += "end Network\n\n"
        return agent

    def __create_network_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_network_vars(self):
        vars = "\tVars:\n"

        vars += "\t\tmessageContent : {"

        for agent_name in self.agents:
            vars += f"{agent_name}Key, "

        vars += "none};\n"

        vars += "\t\tmessageDestination: {"

        for agent_name in self.agents:
            vars += f"{agent_name}, "

        vars += "none};\n"

        vars += "\t\tmessageSource: {"

        for agent_name in self.agents:
            vars += f"{agent_name}, "

        vars += "none};\n"

        vars += "\t\tmessageEncryption : {"

        for agent_name in self.agents:
            vars += f"{agent_name}Key, "

        vars += "none};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_network_actions(self):
        actions = "\tActions = {"

        for key_name in self.agents:
            key_name = StringTools.capitalize_first_letter(key_name)
            for agent_name in self.agents:
                agent_name = StringTools.capitalize_first_letter(agent_name)
                for encryption_key in self.agents:
                    encryption_key = StringTools.capitalize_first_letter(encryption_key)
                    actions += f"Forward{key_name}KeyTo{agent_name}EncryptedWith{encryption_key}Key, "

        actions += "Wait};\n"
        return actions

    def __create_network_protocol(self):
        protocol = "\tProtocol:\n"

        for message_content in self.agents:
            for message_destination in self.agents:
                for message_encryption in self.agents:
                    protocol += f"\t\tmessageContent={message_content}Key and messageDestination={message_destination} and messageEncryption={message_encryption}Key: " + "{"
                    protocol += f"Forward{StringTools.capitalize_first_letter(message_content)}KeyTo{StringTools.capitalize_first_letter(message_destination)}EncryptedWith{StringTools.capitalize_first_letter(message_encryption)}Key" + "};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_network_evolution(self):
        evolution = "\tEvolution:\n"

        vars = ["messageContent", "messageDestination", "messageSource", "messageEncryption"]

        for var in vars:
            evolution += f"\t\t{var}=none if Action != Wait;\n"

        for message_content in self.agents:
            evolution += f"\t\tmessageContent={message_content}Key if (\n"
            message_content = StringTools.capitalize_first_letter(message_content)
            for message_source in self.agents:
                message_source = StringTools.capitalize_first_letter(message_source)
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_encryption in self.agents:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}KeyTo{message_destination}EncryptedWith{message_encryption}Key or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for message_source in self.agents:
            evolution += f"\t\tmessageSource={message_source} if (\n"
            message_source = StringTools.capitalize_first_letter(message_source)
            for message_content in self.agents:
                message_content = StringTools.capitalize_first_letter(message_content)
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_encryption in self.agents:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}KeyTo{message_destination}EncryptedWith{message_encryption}Key or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for message_destination in self.agents:
            evolution += f"\t\tmessageDestination={message_destination} if (\n"
            message_destination = StringTools.capitalize_first_letter(message_destination)
            for message_source in self.agents:
                message_source = StringTools.capitalize_first_letter(message_source)
                if message_source == message_destination:
                    continue
                for message_content in self.agents:
                    message_content = StringTools.capitalize_first_letter(message_content)
                    for message_encryption in self.agents:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}KeyTo{message_destination}EncryptedWith{message_encryption}Key or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for message_encryption in self.agents:
            evolution += f"\t\tmessageEncryption={message_encryption}Key if (\n"
            message_encryption = StringTools.capitalize_first_letter(message_encryption)
            for message_source in self.agents:
                message_source = StringTools.capitalize_first_letter(message_source)
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_content in self.agents:
                        message_content = StringTools.capitalize_first_letter(message_content)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}KeyTo{message_destination}EncryptedWith{message_encryption}Key or \n"

            evolution = evolution.rstrip("\nro ")
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
        init_states += "\tEnvironment.processingMessage=false and\n"

        for agent_name in self.agents:
            for key_name in self.agents:
                if agent_name == key_name:
                    init_states += f"\t{StringTools.capitalize_first_letter(agent_name)}.{key_name}Key=plain and\n"
                else:
                    init_states += f"\t{StringTools.capitalize_first_letter(agent_name)}.{key_name}Key=none and\n"

                init_states += f"\t{StringTools.capitalize_first_letter(agent_name)}.{key_name}EncryptionKey=none and\n"

        vars = ["messageContent", "messageDestination", "messageSource", "messageEncryption"]

        for var in vars:
            init_states += f"\tNetwork.{var}=none and\n"

        init_states = init_states.rstrip("\ndna ")
        init_states += ";\nend InitStates\n\n"
        return init_states

    def __create_groups(self):
        groups = "Groups\n"
        groups += "\ttrusted={Alice, Bob, Server};\n"
        groups += "\tatk={Attacker, Network};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self):
        formulae = "Formulae\n"
        formulae += "\t<trusted>F keyExchanged;\n"
        formulae += "\t<trusted>G !compromised;\n"
        formulae += "end Formulae\n\n"
        return formulae


tmn_protocol_ispl_generator = TmnProtocolIsplGeneratorV2()

f = open("tmn_protocol_v2.ispl", "w")
f.write(tmn_protocol_ispl_generator.create_ispl_model())
f.close()

print("Done. Saved model in tmn_protocol_v2.ispl")


# Network agent - zawiera destynacje wszystkich wiadomości (może też