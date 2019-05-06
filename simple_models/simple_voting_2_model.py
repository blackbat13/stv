from simple_models.model_generator import ModelGenerator
from tools.array_tools import ArrayTools
import itertools


class SimpleVoting2Model(ModelGenerator):
    no_voters = 0
    no_candidates = 0

    def __init__(self, no_voters, no_candidates):
        super().__init__(no_agents=no_voters + no_candidates)
        self.no_voters = no_voters
        self.no_candidates = no_candidates
        self.generate_model()

    def generate_first_state(self):
        first_state = {'vote': ArrayTools.create_value_array_of_size(self.no_voters, -1),
                       'voter_action': ArrayTools.create_value_array_of_size(self.no_voters, ''),
                       'pun': ArrayTools.create_value_array_of_size(self.no_voters, None),
                       'finish': ArrayTools.create_value_array_of_size(self.no_voters, False),
                       'ea_action': ''}
        self.add_state(first_state)

    def generate_model(self):
        self.generate_first_state()
        current_state_id = -1
        for state in self.states:
            current_state_id += 1
            if self.is_final_state(state):
                continue

            if state['ea_action'] == '':
                self.generate_ea_action(state, current_state_id)
                continue

            actions_product_array = [self.get_coercer_possible_actions(state)]
            for voter_id in range(0, self.no_voters):
                actions_product_array.append(self.get_voter_possible_actions(state, voter_id))

            for possibility in itertools.product(*actions_product_array):
                all_wait = True
                for act in possibility:
                    if act != 'Wait':
                        all_wait = False
                        break

                if all_wait:
                    continue
                coercer_action = possibility[0]
                voter_action = possibility[1:]
                new_state = {'vote': state['vote'][:],
                             'voter_action': state['voter_action'][:],
                             'pun': state['pun'][:],
                             'finish': state['finish'][:],
                             'ea_action': state['ea_action']}

                actions = ArrayTools.create_value_array_of_size(self.no_voters + 2, 'Wait')

                if coercer_action != 'Wait':
                    voter_id = coercer_action[1]
                    if coercer_action[0] == 'pun':
                        if state['ea_action'] == 'high' and state['voter_action'][voter_id] == 'ng':
                            new_state['pun'][voter_id] = False
                        else:
                            new_state['pun'][voter_id] = True
                        actions[1] = f'pun{voter_id}'
                        new_state['finish'][voter_id] = True
                    else:
                        new_state['pun'][voter_id] = False
                        actions[1] = f'np{voter_id}'
                        new_state['finish'][voter_id] = True

                for voter_id in range(0, self.no_voters):
                    if voter_action[voter_id] == 'Wait':
                        continue
                    if voter_action[voter_id] == 'give':
                        new_state['voter_action'][voter_id] = 'give'
                        actions[voter_id + 2] = 'give'
                    elif voter_action[voter_id] == 'ng':
                        new_state['voter_action'][voter_id] = 'ng'
                        actions[voter_id + 2] = 'ng'
                    else:
                        candidate_id = voter_action[voter_id][1]
                        new_state['vote'][voter_id] = candidate_id
                        actions[voter_id + 2] = f'Vote{candidate_id}'

                new_state_id = self.add_state(new_state)
                self.model.add_transition(current_state_id, new_state_id, actions)

    def get_coercer_possible_actions(self, state):
        coercer_actions = []
        for voter_id in range(0, self.no_voters):
            if state['pun'][voter_id] is None and state['voter_action'][voter_id] != '':
                coercer_actions.append(('pun', voter_id))
                coercer_actions.append(('np', voter_id))

        if len(coercer_actions) == 0:
            return ['Wait']
        return coercer_actions

    def get_voter_possible_actions(self, state, voter_id):
        voter_actions = ['Wait']
        if state['vote'][voter_id] == -1:
            for candidate_id in range(0, self.no_candidates):
                voter_actions.append(('vote', candidate_id))
        elif state['voter_action'][voter_id] == '':
            voter_actions.append('give')
            voter_actions.append('ng')

        return voter_actions

    def generate_ea_action(self, state, current_state_id):
        for level in ['low', 'high']:
            new_state = {'vote': state['vote'][:],
                         'voter_action': state['voter_action'][:],
                         'pun': state['pun'][:],
                         'finish': state['finish'][:],
                         'ea_action': f'{level}'}
            new_state_id = self.add_state(new_state)
            actions = ArrayTools.create_value_array_of_size(self.no_voters + 2, 'Wait')
            actions[0] = f'{level} protection'
            self.model.add_transition(current_state_id, new_state_id, actions)

    def is_final_state(self, state):
        for val in state['finish']:
            if not val:
                return False

        return True

    def get_epistemic_state(self, state: hash, agent_number: int):
        return state

    def get_actions(self) -> list:
        actions = [['low protection', 'high protection', 'Wait'], ['Wait']]
        for voter_id in range(0, self.no_voters):
            actions[-1].append(f'pun{voter_id}')
            actions[-1].append(f'np{voter_id}')
        for voter_id in range(0, self.no_voters):
            actions.append(['Wait', 'give', 'ng'])
            for candidate_id in range(0, self.no_candidates):
                actions[-1].append(f'Vote{candidate_id}')

        return actions
