from simple_models.simple_model import SimpleModel
from simple_models.model_generator import ModelGenerator
from typing import List
import itertools


class CastleModel(ModelGenerator):
    castle_sizes: List[int] = []
    castle_lifes: List[int] = []

    def __init__(self, castle_sizes: List[int], castle_lifes: List[int]):
        assert len(castle_sizes) == len(castle_lifes)
        super().__init__(no_agents=sum(castle_sizes))
        self.castle_sizes = castle_sizes
        self.castle_lifes = castle_lifes
        self.model = SimpleModel(sum(castle_sizes))
        self.prepare_epistemic_dictionaries()
        self.generate_model()
        self.prepare_epistemic_relation()

    def generate_first_state(self) -> hash:
        defend = []
        defeated = []
        for castle_id in range(0, len(self.castle_sizes)):
            defeated.append(False)
            defend.append([])
            for i in range(0, self.castle_sizes[castle_id]):
                defend[castle_id].append(False)
        first_state = {'lifes': self.castle_lifes[:], 'defend': defend, 'defeated': defeated}
        return first_state

    def get_epistemic_state(self, state: hash, agent_number: int) -> hash:
        castle_id = 0
        agent_no = 0
        size = 0
        for i in range(0, len(self.castle_sizes)):
            prev_size = size
            size += self.castle_sizes[i]
            if agent_number < size:
                castle_id = i
                agent_no = agent_number - prev_size
                break

        defend = state['defend'][castle_id][agent_no]
        epistemic_state = {'defend': defend, 'defeated': state['defeated']}

        return epistemic_state

    def generate_model(self):
        first_state = self.generate_first_state()
        self.add_state(first_state)
        current_state_number = -1
        possible_actions = self.generate_actions()

        for state in self.states:
            current_state_number += 1
            if sum(state['lifes']) == 0:
                continue

            for action in itertools.product(*possible_actions):
                defend = []
                for i in range(0, len(self.castle_sizes)):
                    defend.append(state['defend'][i][:])
                new_state = {'lifes': state['lifes'][:],
                             'defend': defend, 'defeated': state['defeated'][:]}
                lifes_result = []
                for i in range(0, len(self.castle_sizes)):
                    lifes_result.append(0)
                skip = False

                agent_no = -1
                for castle_id in range(0, len(self.castle_sizes)):
                    for i in range(0, self.castle_sizes[castle_id]):
                        agent_no += 1
                        if action[agent_no] == 'idle':
                            new_state['defend'][castle_id][i] = False
                        elif state['lifes'][castle_id] == 0:
                            skip = True
                            break
                        elif action[agent_no] == 'defend':
                            if state['defend'][castle_id][i]:
                                skip = True
                                break
                            else:
                                new_state['defend'][castle_id][i] = True
                                lifes_result[castle_id] += 1
                        else:
                            castle_no = int(action[agent_no].split()[1])
                            new_state['defend'][castle_id][i] = False
                            lifes_result[castle_no] -= 1

                    if skip:
                        break

                if skip:
                    continue

                for i in range(0, len(self.castle_sizes)):
                    if lifes_result[i] < 0:
                        new_state['lifes'][i] += lifes_result[i]
                        if new_state['lifes'][i] < 0:
                            new_state['lifes'][i] = 0
                        if new_state['lifes'][i] == 0:
                            new_state['defeated'][i] = True

                new_state_number = self.add_state(new_state)

                actions = []
                for i in range(0, self.no_agents):
                    actions.append(action[i])

                self.model.add_transition(current_state_number, new_state_number, actions)

    def generate_actions(self):
        actions = []
        for i in range(0, len(self.castle_sizes)):
            actions.append(['idle', 'defend'])
            for j in range(0, len(self.castle_sizes)):
                if i == j:
                    continue
                actions[-1].append('attack ' + str(j))

        possible_actions = []

        for i in range(0, len(self.castle_sizes)):
            for j in range(0, self.castle_sizes[i]):
                possible_actions.append(actions[i])

        return possible_actions
