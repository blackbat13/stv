from models.simple_model import SimpleModel
from enum import Enum
import itertools


class TMNProtocol:
    # TODO implement using ModelGenerator
    model = None
    agent_names = ["Alice", "Bob", "Server", "Attacker", "Network"]
    states_dictionary: dict = {}
    epistemic_states_dictionaries = []
    state_number: int = 0
    no_agents: int = 5
    key_pairs: dict = dict()

    class KeyStatus(Enum):
        NONE = 0
        PLAIN = 1
        ENCRYPTED = 2

    class EncryptionKey(Enum):
        ALICE = 0
        BOB = 1
        ATTACKER = 2
        SERVER_PUBLIC = 3
        SERVER_PRIVATE = 4
        NONE = 5

    class Agents(Enum):
        ALICE = 0
        BOB = 1
        ATTACKER = 2
        SERVER = 3
        NONE = 4

    def __init__(self):
        self.create_atl_model()
        self.prepare_variables()
        self.generate_model()
        self.prepare_epistemic_relation()

    def create_atl_model(self):
        self.model = SimpleModel(self.no_agents)

    def prepare_variables(self):
        for _ in range(0, self.no_agents):
            self.epistemic_states_dictionaries.append({})
        self.prepare_key_pairs()

    def prepare_key_pairs(self):
        self.key_pairs[self.EncryptionKey.ALICE] = self.EncryptionKey.ALICE
        self.key_pairs[self.EncryptionKey.BOB] = self.EncryptionKey.BOB
        self.key_pairs[self.EncryptionKey.ATTACKER] = self.EncryptionKey.ATTACKER
        self.key_pairs[self.EncryptionKey.SERVER_PUBLIC] = self.EncryptionKey.SERVER_PRIVATE
        self.key_pairs[self.EncryptionKey.SERVER_PRIVATE] = self.EncryptionKey.SERVER_PUBLIC

    def generate_first_state(self):
        know_key = []
        for _ in range(0, 4):
            know_key.append([])
            for _ in range(0, 5):
                know_key[-1].append(self.KeyStatus.NONE)

        know_key[self.Agents.ALICE.value][self.EncryptionKey.ALICE.value] = self.KeyStatus.PLAIN
        know_key[self.Agents.ALICE.value][self.EncryptionKey.SERVER_PUBLIC.value] = self.KeyStatus.PLAIN
        know_key[self.Agents.BOB.value][self.EncryptionKey.BOB.value] = self.KeyStatus.PLAIN
        know_key[self.Agents.BOB.value][self.EncryptionKey.SERVER_PUBLIC.value] = self.KeyStatus.PLAIN
        know_key[self.Agents.SERVER.value][self.EncryptionKey.SERVER_PRIVATE.value] = self.KeyStatus.PLAIN
        know_key[self.Agents.SERVER.value][self.EncryptionKey.SERVER_PUBLIC.value] = self.KeyStatus.PLAIN
        know_key[self.Agents.ATTACKER.value][self.EncryptionKey.ATTACKER.value] = self.KeyStatus.PLAIN
        know_key[self.Agents.ATTACKER.value][self.EncryptionKey.SERVER_PUBLIC.value] = self.KeyStatus.PLAIN

        key_encryption = []
        for _ in range(0, 4):
            key_encryption.append([])
            for _ in range(0, 5):
                key_encryption[-1].append(self.EncryptionKey.NONE)

        first_state = {
            'processing_message': False,
            'know_key': know_key,
            'key_encryption': key_encryption,
            'message_content': self.EncryptionKey.NONE,
            'message_to': self.Agents.NONE,
            'message_from': self.Agents.NONE,
            'message_encryption': self.EncryptionKey.NONE
        }

        self.add_state(first_state)

    def generate_model(self):
        self.generate_first_state()
        current_state_number = -1
        for state in self.model.states:
            current_state_number += 1

            possible_actions = []
            for agent_id in range(0, 4):
                possible_actions.append([('wait')])
                for key_id in range(0, 5):
                    if state['know_key'][agent_id][key_id] == self.KeyStatus.ENCRYPTED:
                        key_encryption = state['key_encryption'][agent_id][key_id].value
                        if state['know_key'][agent_id][key_encryption] == self.KeyStatus.PLAIN:
                            possible_actions[agent_id].append(('decrypt', key_id))

            if not state['processing_message']:
                for agent_id in range(0, 4):
                    for message_key_id in range(0, 5):
                        if state['know_key'][agent_id][message_key_id] != self.KeyStatus.PLAIN:
                            continue
                        for encryption_key_id in range(0, 5):
                            if state['know_key'][agent_id][encryption_key_id] != self.KeyStatus.PLAIN:
                                continue
                            for recipient_id in range(0, 4):
                                if agent_id == recipient_id:
                                    continue

                                possible_actions[agent_id].append(
                                    ('send_message', message_key_id, encryption_key_id, recipient_id))

                possible_actions.append([('wait')])
            else:
                for agent_id in range(0, 4):
                    if state['message_to'].value != agent_id:
                        possible_actions[self.Agents.ATTACKER.value].append(('change_message_to', agent_id))
                    if state['message_from'].value != agent_id:
                        possible_actions[self.Agents.ATTACKER.value].append(('change_message_from', agent_id))
                for message_key_id in range(0, 5):
                    if state['know_key'][self.Agents.ATTACKER.value][message_key_id] != self.KeyStatus.PLAIN:
                        continue
                    for encryption_key_id in range(0, 5):
                        if state['know_key'][self.Agents.ATTACKER.value][encryption_key_id] != self.KeyStatus.PLAIN:
                            continue
                        if state['message_content'].value == message_key_id and state['message_encryption'].value == encryption_key_id:
                            continue
                        possible_actions[self.Agents.ATTACKER.value].append(('change_message', message_key_id, encryption_key_id))

                possible_actions.append([('wait'), ('forward')])

            for action in itertools.product(*possible_actions):
                send_message = 0
                for agent_id in range(0, 4):
                    if action[agent_id][0] == 'send_message':
                        send_message += 1

                if send_message > 1:
                    continue



    def add_state(self, state):
        new_state_number = self.get_state_number(state)
        for agent_no in range(0, self.no_agents):
            epistemic_state = self.get_epistemic_state(state, agent_no)
            self.add_to_epistemic_dictionary(epistemic_state, new_state_number, agent_no)
        return new_state_number

    def get_state_number(self, state):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.states_dictionary:
            self.states_dictionary[state_str] = self.state_number
            new_state_number = self.state_number
            self.model.states.append(state)
            self.state_number += 1
        else:
            new_state_number = self.states_dictionary[state_str]

        return new_state_number

    def add_to_epistemic_dictionary(self, state, new_state_number, agent_no):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.epistemic_states_dictionaries[agent_no]:
            self.epistemic_states_dictionaries[agent_no][state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionaries[agent_no][state_str].add(new_state_number)

    def get_epistemic_state(self, state, agent_no):
        epistemic_coins = state['coins'][:]
        for i in range(0, self.no_agents):
            if i == agent_no or i == agent_no - 1:
                continue

            epistemic_coins[i] = self.Coin.NONE
        epistemic_state = {'number_of_odd': state['number_of_odd'], 'coins': epistemic_coins, 'paying': -2}
        return epistemic_state

    def prepare_epistemic_relation(self):
        for agent_no in range(0, self.no_agents):
            for state, epistemic_class in self.epistemic_states_dictionaries[agent_no].items():
                self.model.add_epistemic_class(agent_no, epistemic_class)
