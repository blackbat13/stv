from stv.models.model_generator import ModelGenerator
from stv.tools.list_tools import ListTools
from typing import List
import itertools


class SimpleVotingModel(ModelGenerator):

    def __init__(self, number_of_candidates: int, number_of_voters: int):
        super().__init__(agents_count=(number_of_candidates + 1))
        self._number_of_candidates = number_of_candidates
        self._number_of_voters = number_of_voters

    def _generate_initial_states(self):
        initial_array = ['' for _ in range(self._number_of_voters)]
        initial_array_minus_one = [-1 for _ in range(self._number_of_voters)]
        first_state = {'voted': initial_array_minus_one[:], 'voters_action': initial_array[:],
                       'coercer_actions': initial_array[:], 'finish': initial_array_minus_one[:]}
        self._add_state(first_state)

    def _generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            voting_product_array = []
            coercer_possible_actions = ['wait']
            for voter_number in range(0, self._number_of_voters):
                if state['voted'][voter_number] == -1:
                    voting_product_array.append(list(range(0, self._number_of_candidates)))
                    voting_product_array[voter_number].append('wait')
                elif state['voters_action'][voter_number] == '':
                    voting_product_array.append(['give', 'ng', 'wait'])
                elif state['coercer_actions'][voter_number] == '':
                    coercer_possible_actions.append('np' + str(voter_number + 1))
                    coercer_possible_actions.append('pun' + str(voter_number + 1))
                    voting_product_array.append(['wait'])
                else:
                    voting_product_array.append(['wait'])

            voting_product_array.append(coercer_possible_actions)

            for possibility in itertools.product(*voting_product_array):
                action = ['' for _ in range(self._number_of_voters + 1)]
                new_state = {'voted': state['voted'][:], 'voters_action': state['voters_action'][:],
                             'coercer_actions': state['coercer_actions'][:], 'finish': state['finish'][:]}

                for voter_number in range(0, self._number_of_voters):
                    action[voter_number + 1] = possibility[voter_number]
                    voter_action_string = str(possibility[voter_number])
                    if voter_action_string[0] == 'g' or voter_action_string[0] == 'n':
                        new_state['voters_action'][voter_number] = voter_action_string
                    elif voter_action_string[0] != 'w':
                        new_state['voted'][voter_number] = possibility[voter_number]

                action[0] = possibility[self._number_of_voters]
                if action[0][0:3] == 'pun':
                    pun_voter_number = int(action[0][3:])
                    new_state['coercer_actions'][pun_voter_number - 1] = 'pun'
                    new_state['finish'][pun_voter_number - 1] = 1
                elif action[0][0:2] == 'np':
                    np_voter_number = int(action[0][2:])
                    new_state['coercer_actions'][np_voter_number - 1] = 'np'
                    new_state['finish'][np_voter_number - 1] = 1

                new_state_id = self._add_state(new_state)

                self.model.add_transition(current_state_number, new_state_id, action)

    def _get_epistemic_state(self, state: hash, agent_id: int):
        if agent_id == 0:
            epistemic_state = {'coercer_actions': state['coercer_actions'][:], 'voted': state['voted'][:],
                               'voters_action': state['voters_action'][:], 'finish': state['finish'][:]}
            for voter_number in range(0, self._number_of_voters):
                if state['voters_action'][voter_number] == '' and state['voted'][voter_number] != -1:
                    epistemic_state['voted'][voter_number] = -2
                elif state['voters_action'][voter_number] == 'ng':
                    epistemic_state['voted'][voter_number] = -1
            return epistemic_state
        else:
            epistemic_state = {'coercer_actions': state['coercer_actions'][:], 'voted': state['voted'][:],
                               'voters_action': state['voters_action'][:], 'finish': state['finish'][:]}
            for voter_number in range(1, self._number_of_voters):
                epistemic_state['voters_action'][voter_number] = -1
                epistemic_state['voted'][voter_number] = -1
                epistemic_state['coercer_actions'][voter_number] = -1
                # epistemic_state['finish'][voter_number] = -1
            return epistemic_state

    def get_actions(self):
        result = [['wait']]

        for voter_number in range(1, self._number_of_voters + 1):
            result[0].append(f'np{voter_number}')
            result[0].append(f'pun{voter_number}')
            result.append(['give, ng, wait'])

            for candidate_number in range(0, self._number_of_candidates):
                result[-1].append(str(candidate_number))

        return result

    def _get_props_for_state(self, state: hash) -> List[str]:
        pass

    def get_props_list(self) -> List[str]:
        pass

    def get_winning_states(self, prop: str) -> List[int]:
        pass


if __name__ == "__main__":
    model = SimpleVotingModel(number_of_candidates=2, number_of_voters=2)
    model.generate()
