from stv.tools.string_tools import StringTools


class TmnProtocolIsplGenerator:
    # TODO: integrate with IsplGenerator class
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
        protocol = "\tProtocol:\n\t\tOther: {none};\n\tend Protocol\n"
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
            vars += f"\t\t{agent_name}Key : boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no} : " + "{none, plain, encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_alice_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'alice':
                    continue
                agent_name = StringTools.capitalize_first_letter(agent_name)
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

                agent_name = StringTools.capitalize_first_letter(agent_name)
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

                agent_name = StringTools.capitalize_first_letter(agent_name)
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
            vars += f"\t\t{agent_name}Key : boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no} : " + "{none, plain, encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_bob_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'bob':
                    continue
                agent_name = StringTools.capitalize_first_letter(agent_name)
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

                agent_name = StringTools.capitalize_first_letter(agent_name)
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

                agent_name = StringTools.capitalize_first_letter(agent_name)
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
            vars += f"\t\t{agent_name}Key : boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no} : " + "{none, plain, encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_server_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'server':
                    continue
                agent_name = StringTools.capitalize_first_letter(agent_name)
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

                agent_name = StringTools.capitalize_first_letter(agent_name)
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

                agent_name = StringTools.capitalize_first_letter(agent_name)
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
            vars += f"\t\t{agent_name}Key : boolean;\n"

        for message_no in range(1, self.no_messages + 1):
            vars += f"\t\tmessage{message_no} : " + "{none, plain, encrypted};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_attacker_actions(self):
        actions = "\tActions = {"

        for message_no in range(1, self.no_messages + 1):
            actions += f"decryptMessage{message_no}, "

            for agent_name in self.agents:
                if agent_name == 'attacker':
                    continue
                agent_name = StringTools.capitalize_first_letter(agent_name)
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
                agent_name = StringTools.capitalize_first_letter(agent_name)
                for second_agent in self.agents:
                    second_agent = StringTools.capitalize_first_letter(second_agent)
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
            init_states += f"\tEnvironment.message{message_no}Key={keys[message_no - 1]}KeyM and\n"

        keys = ["alice", "bob", "bob"]

        for message_no in range(1, self.no_messages + 1):
            init_states += f"\tEnvironment.message{message_no}Content={keys[message_no - 1]}KeyM and\n"

        for agent_name in self.agents:
            agent_name = StringTools.capitalize_first_letter(agent_name)

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

                init_states += f"\t{StringTools.capitalize_first_letter(agent_name)}.{key_name}Key={know_key} and\n"

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


class TmnProtocolIsplGeneratorV2:
    ispl_model = ""
    agents = ["alice", "bob", "server", "attacker"]
    keys = ["aliceKey", "bobKey", "serverPublicKey", "serverPrivateKey", "attackerKey"]
    no_messages = 3
    follow_protocol = True

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

        if not self.follow_protocol:
            for message_content in self.keys:
                message_content = StringTools.capitalize_first_letter(message_content)
                for message_source in self.agents:
                    message_source = StringTools.capitalize_first_letter(message_source)
                    for message_destination in self.agents:
                        message_destination = StringTools.capitalize_first_letter(message_destination)
                        if message_source == message_destination:
                            continue
                        for message_encryption in self.keys:
                            message_encryption = StringTools.capitalize_first_letter(message_encryption)
                            evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"
        else:
            evolution += "\t\t\tAlice.Action=SendAliceKeyToServerEncryptedWithServerPublicKey or\n"
            evolution += "\t\t\tBob.Action=SendBobKeyToServerEncryptedWithServerPublicKey or\n"
            evolution += "\t\t\tServer.Action=SendBobKeyToAliceEncryptedWithAliceKey or\n"
            for message_content in self.keys:
                message_content = StringTools.capitalize_first_letter(message_content)
                message_source = "Attacker"
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_encryption in self.keys:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"

        evolution = evolution.rstrip("\nro ")
        evolution += ";\n"

        evolution += "\t\tprocessingMessage=false if\n"

        for message_content in self.keys:
            message_content = StringTools.capitalize_first_letter(message_content)
            for message_destination in self.agents:
                message_destination = StringTools.capitalize_first_letter(message_destination)
                for message_encryption in self.keys:
                    message_encryption = StringTools.capitalize_first_letter(message_encryption)
                    evolution += f"\t\t\tNetwork.Action=Forward{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"

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

        for key_name in self.keys:
            vars += f"\t\t{key_name}K : " + "{none, plain, encrypted};\n"

        for key_name in self.keys:
            vars += f"\t\t{key_name}EncryptionKey : " + "{"
            for key_name2 in self.keys:
                vars += f"{key_name2}, "

            vars += "none};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_attacker_actions(self):
        actions = "\tActions = {"

        for key_name in self.keys:
            key_name = StringTools.capitalize_first_letter(key_name)
            actions += f"Decrypt{key_name}, "
            for agent_name in self.agents:
                agent_name = StringTools.capitalize_first_letter(agent_name)
                if agent_name == "Attacker":
                    continue
                for encryption_key in self.keys:
                    encryption_key = StringTools.capitalize_first_letter(encryption_key)
                    actions += f"Send{key_name}To{agent_name}EncryptedWith{encryption_key}, "

        for agent_name in self.agents:
            agent_name = StringTools.capitalize_first_letter(agent_name)
            actions += f"RedirectTo{agent_name}, "

        for content_key in self.keys:
            content_key = StringTools.capitalize_first_letter(content_key)
            for encryption_key in self.keys:
                encryption_key = StringTools.capitalize_first_letter(encryption_key)
                actions += f"ChangeContentTo{content_key}EncryptedWith{encryption_key}, "

        actions += "ForwardMessage, "
        actions += "Wait};\n"
        return actions

    def __create_attacker_protocol(self):
        protocol = "\tProtocol:\n"

        protocol += self.__create_protocol_decryption()
        protocol += self.__create_protocol_communication("attacker")

        protocol += "\t\tEnvironment.processingMessage=true : {"
        for agent_name in self.agents:
            agent_name = StringTools.capitalize_first_letter(agent_name)
            protocol += f"RedirectTo{agent_name}, "

        protocol += "ForwardMessage, Wait};\n"

        for content_key in self.keys:
            for encryption_key in self.keys:
                protocol += f"\t\t{content_key}K=plain and {encryption_key}K=plain and Environment.processingMessage=true: " + "{"
                protocol += f"ChangeContentTo{StringTools.capitalize_first_letter(content_key)}EncryptedWith{StringTools.capitalize_first_letter(encryption_key)}, "
                protocol += "Wait};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_attacker_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += self.__create_evolution_key_decryption()
        evolution += self.__create_evolution_message_receiving("Attacker")

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

    def __create_agent_vars(self):
        vars = "\tVars:\n"

        for key_name in self.keys:
            vars += f"\t\t{key_name}K : " + "{none, plain, encrypted};\n"

        for key_name in self.keys:
            vars += f"\t\t{key_name}EncryptionKey : " + "{"
            for key_name2 in self.keys:
                vars += f"{key_name2}, "

            vars += "none};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_agent_actions(self, current_agent_name):
        actions = "\tActions = {"

        current_agent_name = StringTools.capitalize_first_letter(current_agent_name)

        for key_name in self.keys:
            key_name = StringTools.capitalize_first_letter(key_name)
            actions += f"Decrypt{key_name}, "
            if not self.follow_protocol:
                for agent_name in self.agents:
                    agent_name = StringTools.capitalize_first_letter(agent_name)
                    if agent_name == current_agent_name:
                        continue
                    for encryption_key in self.keys:
                        encryption_key = StringTools.capitalize_first_letter(encryption_key)
                        actions += f"Send{key_name}To{agent_name}EncryptedWith{encryption_key}, "
        if self.follow_protocol:
            if current_agent_name == "Alice":
                actions += "SendAliceKeyToServerEncryptedWithServerPublicKey, "
            elif current_agent_name == "Bob":
                actions += "SendBobKeyToServerEncryptedWithServerPublicKey, "
            elif current_agent_name == "Server":
                actions += "SendBobKeyToAliceEncryptedWithAliceKey, "

        actions += "Wait};\n"
        return actions

    def __create_agent_protocol(self, current_agent_name):
        protocol = "\tProtocol:\n"

        protocol += self.__create_protocol_decryption()
        if not self.follow_protocol:
            protocol += self.__create_protocol_communication(current_agent_name)
        else:
            if current_agent_name == "Alice":
                protocol += "\t\tEnvironment.protocol=true and Environment.processingMessage=false: {SendAliceKeyToServerEncryptedWithServerPublicKey, Wait};\n"
            elif current_agent_name == "Bob":
                protocol += "\t\tEnvironment.protocol=true and Environment.processingMessage=false: {SendBobKeyToServerEncryptedWithServerPublicKey, Wait};\n"
            elif current_agent_name == "Server":
                protocol += "\t\tEnvironment.protocol=true and aliceKeyK=plain and bobKeyK=plain and Environment.processingMessage=false: {SendBobKeyToAliceEncryptedWithAliceKey, Wait};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_protocol_decryption(self):
        protocol = ""

        for key_name in self.keys:
            protocol += f"\t\t{key_name}K=encrypted and (\n"

            for key_name2 in self.keys:
                if key_name2.find("Public") != -1:
                    key_name3 = key_name2.replace("Public", "Private")
                    protocol += f"\t\t\t({key_name}EncryptionKey={key_name2} and {key_name3}K=plain) or\n"
                elif key_name2.find("Private") != -1:
                    key_name3 = key_name2.replace("Private", "Public")
                    protocol += f"\t\t\t({key_name}EncryptionKey={key_name2} and {key_name3}K=plain) or\n"
                else:
                    protocol += f"\t\t\t({key_name}EncryptionKey={key_name2} and {key_name2}K=plain) or\n"

            protocol = protocol.rstrip("\nro ")
            protocol += "): {" + f"Decrypt{StringTools.capitalize_first_letter(key_name)}" + "};\n"

        return protocol

    def __create_protocol_communication(self, current_agent_name):
        protocol = ""

        current_agent_name = StringTools.capitalize_first_letter(current_agent_name)

        for content_key in self.keys:
            for encryption_key in self.keys:
                protocol += f"\t\t{content_key}K=plain and {encryption_key}K=plain and Environment.processingMessage=false and Environment.protocol=false: " + "{"
                for agent_name in self.agents:
                    agent_name = StringTools.capitalize_first_letter(agent_name)
                    if agent_name == current_agent_name:
                        continue

                    protocol += f"Send{StringTools.capitalize_first_letter(content_key)}To{agent_name}EncryptedWith{StringTools.capitalize_first_letter(encryption_key)}, "

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

        for key_name in self.keys:
            evolution += f"\t\t{key_name}K=plain if\n"
            key_name = StringTools.capitalize_first_letter(key_name)
            evolution += f"\t\t\tAction=Decrypt{key_name};\n"

        return evolution

    def __create_evolution_message_receiving(self, current_agent_name):
        evolution = ""
        current_agent_name = StringTools.capitalize_first_letter(current_agent_name)

        for received_key in self.keys:
            evolution += f"\t\t{received_key}K=encrypted if\n"
            evolution += f"\t\t\t{received_key}K=none and (\n"
            received_key = StringTools.capitalize_first_letter(received_key)
            for encryption_key in self.keys:
                encryption_key = StringTools.capitalize_first_letter(encryption_key)
                evolution += f"\t\t\tNetwork.Action=Forward{received_key}To{current_agent_name}EncryptedWith{encryption_key} or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for received_key in self.keys:
            for encryption_key in self.keys:
                evolution += f"\t\t{received_key}EncryptionKey={encryption_key} if\n"
                evolution += f"\t\t\t{received_key}EncryptionKey=none and\n"
                encryption_key = StringTools.capitalize_first_letter(encryption_key)
                evolution += f"\t\t\tNetwork.Action=Forward{StringTools.capitalize_first_letter(received_key)}To{current_agent_name}EncryptedWith{encryption_key};\n"

        return evolution

    def __create_network(self):
        agent = "Agent Network\n"
        agent += self.__create_network_vars()
        agent += self.__create_network_actions()
        agent += self.__create_network_protocol()
        agent += self.__create_network_evolution()
        agent += "end Agent\n\n"
        return agent

    def __create_network_lobsvars(self):
        lobsvars = "\tLobsvars = {"

        lobsvars += "};\n"
        return lobsvars

    def __create_network_vars(self):
        vars = "\tVars:\n"

        vars += "\t\tmessageContent : {"

        for key_name in self.keys:
            vars += f"{key_name}, "

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

        for key_name in self.keys:
            vars += f"{key_name}, "

        vars += "none};\n"

        vars += "\t\tattackerDone : boolean;\n"
        vars += "\t\tforwardAllToAttacker : boolean;\n"
        vars += "\t\tforwardedToAttacker : boolean;\n"
        vars += "\t\twaitForAttacker : boolean;\n"

        vars += "\tend Vars\n"
        return vars

    def __create_network_actions(self):
        actions = "\tActions = {"

        for key_name in self.keys:
            key_name = StringTools.capitalize_first_letter(key_name)
            for agent_name in self.agents:
                agent_name = StringTools.capitalize_first_letter(agent_name)
                for encryption_key in self.keys:
                    encryption_key = StringTools.capitalize_first_letter(encryption_key)
                    actions += f"Forward{key_name}To{agent_name}EncryptedWith{encryption_key}, "

        actions += "Wait};\n"
        return actions

    def __create_network_protocol(self):
        protocol = "\tProtocol:\n"

        for message_content in self.keys:
            for message_destination in self.agents:
                for message_encryption in self.keys:
                    protocol += f"\t\t((attackerDone=true and waitForAttacker=true) or waitForAttacker=false) and ((forwardAllToAttacker=true and forwardedToAttacker=true) or forwardAllToAttacker=false) and messageContent={message_content} and messageDestination={message_destination} and messageEncryption={message_encryption}: " + "{"
                    protocol += f"Forward{StringTools.capitalize_first_letter(message_content)}To{StringTools.capitalize_first_letter(message_destination)}EncryptedWith{StringTools.capitalize_first_letter(message_encryption)}" + "};\n"

        for message_content in self.keys:
            for message_encryption in self.keys:
                protocol += f"\t\tforwardAllToAttacker=true and forwardedToAttacker=false and messageContent={message_content} and messageEncryption={message_encryption}: " + "{"
                protocol += f"Forward{StringTools.capitalize_first_letter(message_content)}ToAttackerEncryptedWith{StringTools.capitalize_first_letter(message_encryption)}" + "};\n"

        protocol += "\t\tOther: {Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_network_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\t\tattackerDone=true if Attacker.Action=ForwardMessage;\n"

        evolution += self.__create_network_evolution_forward_to_attacker()
        evolution += self.__create_network_evolution_clean_vars()
        evolution += self.__create_network_evolution_redirect()
        evolution += self.__create_network_evolution_change_content()

        for message_content in self.keys:
            evolution += f"\t\tmessageContent={message_content} if (\n"
            message_content = StringTools.capitalize_first_letter(message_content)
            if not self.follow_protocol:
                for message_source in self.agents:
                    message_source = StringTools.capitalize_first_letter(message_source)
                    for message_destination in self.agents:
                        message_destination = StringTools.capitalize_first_letter(message_destination)
                        if message_source == message_destination:
                            continue
                        for message_encryption in self.keys:
                            message_encryption = StringTools.capitalize_first_letter(message_encryption)
                            evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"
            else:
                message_source = "Attacker"
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_encryption in self.keys:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        if not self.follow_protocol:
            for message_source in self.agents:
                evolution += f"\t\tmessageSource={message_source} if (\n"
                message_source = StringTools.capitalize_first_letter(message_source)
                for message_content in self.keys:
                    message_content = StringTools.capitalize_first_letter(message_content)
                    for message_destination in self.agents:
                        message_destination = StringTools.capitalize_first_letter(message_destination)
                        if message_source == message_destination:
                            continue
                        for message_encryption in self.keys:
                            message_encryption = StringTools.capitalize_first_letter(message_encryption)
                            evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"
        else:
            evolution += f"\t\tmessageSource=attacker if (\n"
            message_source = "Attacker"
            for message_content in self.keys:
                message_content = StringTools.capitalize_first_letter(message_content)
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_encryption in self.keys:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for message_destination in self.agents:
            if self.follow_protocol and message_destination == "attacker":
                continue
            evolution += f"\t\tmessageDestination={message_destination} if (\n"
            message_destination = StringTools.capitalize_first_letter(message_destination)
            if not self.follow_protocol:
                for message_source in self.agents:
                    message_source = StringTools.capitalize_first_letter(message_source)
                    if message_source == message_destination:
                        continue
                    for message_content in self.keys:
                        message_content = StringTools.capitalize_first_letter(message_content)
                        for message_encryption in self.keys:
                            message_encryption = StringTools.capitalize_first_letter(message_encryption)
                            evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"
            else:
                message_source = "Attacker"
                if message_source == message_destination:
                    continue
                for message_content in self.keys:
                    message_content = StringTools.capitalize_first_letter(message_content)
                    for message_encryption in self.keys:
                        message_encryption = StringTools.capitalize_first_letter(message_encryption)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for message_encryption in self.keys:
            evolution += f"\t\tmessageEncryption={message_encryption} if (\n"
            message_encryption = StringTools.capitalize_first_letter(message_encryption)
            if not self.follow_protocol:
                for message_source in self.agents:
                    message_source = StringTools.capitalize_first_letter(message_source)
                    for message_destination in self.agents:
                        message_destination = StringTools.capitalize_first_letter(message_destination)
                        if message_source == message_destination:
                            continue
                        for message_content in self.keys:
                            message_content = StringTools.capitalize_first_letter(message_content)
                            evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"
            else:
                message_source = "Attacker"
                for message_destination in self.agents:
                    message_destination = StringTools.capitalize_first_letter(message_destination)
                    if message_source == message_destination:
                        continue
                    for message_content in self.keys:
                        message_content = StringTools.capitalize_first_letter(message_content)
                        evolution += f"\t\t\t{message_source}.Action=Send{message_content}To{message_destination}EncryptedWith{message_encryption} or \n"
            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        if self.follow_protocol:
            evolution += "\t\tmessageContent=aliceKey if Alice.Action=SendAliceKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageContent=bobKey if Bob.Action=SendBobKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageContent=bobKey if Server.Action=SendBobKeyToAliceEncryptedWithAliceKey;\n"

            evolution += "\t\tmessageSource=alice if Alice.Action=SendAliceKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageSource=bob if Bob.Action=SendBobKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageSource=server if Server.Action=SendBobKeyToAliceEncryptedWithAliceKey;\n"

            evolution += "\t\tmessageDestination=server if Alice.Action=SendAliceKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageDestination=server if Bob.Action=SendBobKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageDestination=alice if Server.Action=SendBobKeyToAliceEncryptedWithAliceKey;\n"

            evolution += "\t\tmessageEncryption=serverPublicKey if Alice.Action=SendAliceKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageEncryption=serverPublicKey if Bob.Action=SendBobKeyToServerEncryptedWithServerPublicKey;\n"
            evolution += "\t\tmessageEncryption=aliceKey if Server.Action=SendBobKeyToAliceEncryptedWithAliceKey;\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_network_evolution_forward_to_attacker(self):
        evolution = "\t\tforwardedToAttacker=true if\n"
        evolution += "\t\t\tforwardAllToAttacker=true and (\n"

        for key_name in self.keys:
            key_name = StringTools.capitalize_first_letter(key_name)
            for encryption_key in self.keys:
                encryption_key = StringTools.capitalize_first_letter(encryption_key)
                evolution += f"\t\t\tAction=Forward{key_name}ToAttackerEncryptedWith{encryption_key} or\n"

        evolution = evolution.rstrip("\nro ")
        evolution += ");\n"

        return evolution

    def __create_network_evolution_clean_vars(self):
        evolution = ""
        vars = [["messageContent", "none"], ["messageDestination", "none"], ["messageSource", "none"],
                ["messageEncryption", "none"], ["forwardedToAttacker", "false"], ["attackerDone", "false"]]
        for var in vars:
            evolution += f"\t\t{var[0]}={var[1]} if\n"
            evolution += f"\t\t\t((forwardedToAttacker=true and forwardAllToAttacker=true) or forwardAllToAttacker=false) and (\n"
            for key_name in self.keys:
                key_name = StringTools.capitalize_first_letter(key_name)
                for agent_name in self.agents:
                    agent_name = StringTools.capitalize_first_letter(agent_name)
                    for encryption_key in self.keys:
                        encryption_key = StringTools.capitalize_first_letter(encryption_key)
                        evolution += f"\t\t\tAction=Forward{key_name}To{agent_name}EncryptedWith{encryption_key} or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        return evolution

    def __create_network_evolution_redirect(self):
        evolution = ""
        for agent_name in self.agents:
            evolution += f"\t\tmessageDestination={agent_name} if\n"
            evolution += "\t\t\tEnvironment.processingMessage=true and\n"
            agent_name = StringTools.capitalize_first_letter(agent_name)
            evolution += f"\t\t\tAttacker.Action=RedirectTo{agent_name};\n"

        return evolution

    def __create_network_evolution_change_content(self):
        evolution = ""

        for content_key in self.keys:
            evolution += f"\t\tmessageContent={content_key} if\n"
            evolution += "\t\t\tEnvironment.processingMessage=true and (\n"
            content_key = StringTools.capitalize_first_letter(content_key)
            for encryption_key in self.keys:
                encryption_key = StringTools.capitalize_first_letter(encryption_key)
                evolution += f"\t\t\tAttacker.Action=ChangeContentTo{content_key}EncryptedWith{encryption_key} or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for encryption_key in self.keys:
            evolution += f"\t\tmessageEncryption={encryption_key} if\n"
            evolution += "\t\t\tEnvironment.processingMessage=true and (\n"
            encryption_key = StringTools.capitalize_first_letter(encryption_key)
            for content_key in self.keys:
                content_key = StringTools.capitalize_first_letter(content_key)
                evolution += f"\t\t\tAttacker.Action=ChangeContentTo{content_key}EncryptedWith{encryption_key} or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        return evolution

    def __create_evaluation(self):
        evaluation = "Evaluation\n"
        evaluation += "\tkeyExchanged if Alice.bobKeyK=plain;\n"
        evaluation += "\tcompromised if Attacker.aliceKeyK=plain or Attacker.bobKeyK=plain or Attacker.serverPrivateKeyK=plain;\n"
        evaluation += "end Evaluation\n\n"
        return evaluation

    def __create_init_states(self):
        init_states = "InitStates\n"

        init_states += "\tEnvironment.processingMessage=false and\n"

        for agent_name in self.agents:
            for key_name in self.keys:
                if key_name.find(agent_name) != -1 or key_name.find("PublicKey") != -1:
                    init_states += f"\t{StringTools.capitalize_first_letter(agent_name)}.{key_name}K=plain and\n"
                else:
                    init_states += f"\t{StringTools.capitalize_first_letter(agent_name)}.{key_name}K=none and\n"

                init_states += f"\t{StringTools.capitalize_first_letter(agent_name)}.{key_name}EncryptionKey=none and\n"

        vars = ["messageContent", "messageDestination", "messageSource", "messageEncryption"]

        for var in vars:
            init_states += f"\tNetwork.{var}=none and\n"

        init_states += "\tNetwork.attackerDone=false and\n"
        init_states += "\tNetwork.forwardAllToAttacker=true and\n"
        init_states += "\tNetwork.waitForAttacker=true and\n"
        init_states += "\tNetwork.forwardedToAttacker=false;\n"
        init_states += "end InitStates\n\n"
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
