from stv.models.model_generator import ModelGenerator
from stv.tools.list_tools import ListTools
from typing import List
import itertools


class SimpleVoting2Model(ModelGenerator):

    def __init__(self, no_voters: int, no_candidates: int):
        super().__init__(agents_count=no_voters + no_candidates)
        self._no_voters = no_voters
        self._no_candidates = no_candidates

    def generate(self):
        self._generate_initial_states()
        self._generate_model()

    def _generate_initial_states(self):
        first_state = {'vote': [-1 for _ in range(self._no_voters)],
                       'voter_action': ['' for _ in range(self._no_voters)],
                       'pun': [None for _ in range(self._no_voters)],
                       'finish': [False for _ in range(self._no_voters)],
                       'ea_action': ''}
        self._add_state(first_state)

    def _generate_model(self):
        current_state_id = -1
        for state in self.states:
            current_state_id += 1
            if self._is_final_state(state):
                continue

            if state['ea_action'] == '':
                self._generate_ea_action(state, current_state_id)
                continue

            actions_product_array = [self._get_coercer_possible_actions(state)]
            for voter_id in range(0, self._no_voters):
                actions_product_array.append(self._get_voter_possible_actions(state, voter_id))

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

                actions = ['Wait' for _ in range(self._no_voters + 2)]

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

                for voter_id in range(0, self._no_voters):
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

                new_state_id = self._add_state(new_state)
                self.model.add_transition(current_state_id, new_state_id, actions)

    def _get_coercer_possible_actions(self, state):
        coercer_actions = []
        for voter_id in range(0, self._no_voters):
            if state['pun'][voter_id] is None and state['voter_action'][voter_id] != '':
                coercer_actions.append(('pun', voter_id))
                coercer_actions.append(('np', voter_id))

        if len(coercer_actions) == 0:
            return ['Wait']
        return coercer_actions

    def _get_voter_possible_actions(self, state, voter_id):
        voter_actions = ['Wait']
        if state['vote'][voter_id] == -1:
            for candidate_id in range(0, self._no_candidates):
                voter_actions.append(('vote', candidate_id))
        elif state['voter_action'][voter_id] == '':
            voter_actions.append('give')
            voter_actions.append('ng')

        return voter_actions

    def _generate_ea_action(self, state, current_state_id):
        for level in ['low', 'high']:
            new_state = {'vote': state['vote'][:],
                         'voter_action': state['voter_action'][:],
                         'pun': state['pun'][:],
                         'finish': state['finish'][:],
                         'ea_action': f'{level}'}
            new_state_id = self._add_state(new_state)
            actions = ['Wait' for _ in range(self._no_voters + 2)]
            actions[0] = f'{level} protection'
            self.model.add_transition(current_state_id, new_state_id, actions)

    def _is_final_state(self, state):
        for val in state['finish']:
            if not val:
                return False

        return True

    def _get_epistemic_state(self, state: hash, agent_id: int):
        return state

    def get_actions(self) -> list:
        actions = [['low protection', 'high protection', 'Wait'], ['Wait']]
        for voter_id in range(0, self._no_voters):
            actions[-1].append(f'pun{voter_id}')
            actions[-1].append(f'np{voter_id}')
        for voter_id in range(0, self._no_voters):
            actions.append(['Wait', 'give', 'ng'])
            for candidate_id in range(0, self._no_candidates):
                actions[-1].append(f'Vote{candidate_id}')

        return actions

    def _get_props_for_state(self, state: hash) -> List[str]:
        pass

    def get_props_list(self) -> List[str]:
        pass

    def get_winning_states(self, prop: str) -> List[int]:
        pass


if __name__ == "__main__":
    model = SimpleVoting2Model(no_voters=2, no_candidates=2)
    model.generate()
