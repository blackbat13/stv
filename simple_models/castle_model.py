from simple_models.simple_model import SimpleModel
from simple_models.model_generator import ModelGenerator
from typing import List
from tools.array_tools import ArrayTools
import itertools


class CastleModel(ModelGenerator):
    castle_sizes: List[int] = []
    castle_lifes: List[int] = []
    castles_no: int = 0

    def __init__(self, castle_sizes: List[int], castle_lifes: List[int]):
        assert len(castle_sizes) == len(castle_lifes)
        super().__init__(no_agents=sum(castle_sizes))
        self.castle_sizes = castle_sizes
        self.castle_lifes = castle_lifes
        self.castles_no = len(castle_lifes)
        self.model = SimpleModel(sum(castle_sizes))
        self.prepare_epistemic_dictionaries()
        self.generate_model()
        self.prepare_epistemic_relation()

    def generate_first_state(self) -> hash:
        defend = []
        defeated = []
        for castle_id in range(0, self.castles_no):
            defeated.append(False)
            defend.append([])
            for i in range(0, self.castle_sizes[castle_id]):
                defend[castle_id].append(False)
        first_state = {'lifes': self.castle_lifes[:], 'defend': defend, 'defeated': defeated}
        return first_state

    def get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        castle_id = 0
        agent_no = 0
        size = 0
        for i in range(0, self.castles_no):
            prev_size = size
            size += self.castle_sizes[i]
            if agent_id < size:
                castle_id = i
                agent_no = agent_id - prev_size
                break

        defend = state['defend'][castle_id][agent_no]
        epistemic_state = {'defend': defend, 'defeated': state['defeated']}

        return epistemic_state

    def generate_model(self):
        first_state = self.generate_first_state()
        self.add_state(first_state)
        current_state_id = -1

        for state in self.states:
            current_state_id += 1
            if sum(state['lifes']) == 0:
                continue

            possible_actions = self.generate_possible_actions(state)
            for action in itertools.product(*possible_actions):
                new_state = self.new_state_after_action(state, action)
                new_state_id = self.add_state(new_state)
                self.model.add_transition(current_state_id, new_state_id, list(action))

    def new_state_after_action(self, state: dict, action: tuple) -> dict:
        defend = []
        for i in range(0, self.castles_no):
            defend.append(state['defend'][i][:])
        new_state = {'lifes': state['lifes'][:],
                     'defend': defend, 'defeated': state['defeated'][:]}
        self.apply_action_to_state(new_state, action)

        return new_state

    def apply_action_to_state(self, state: dict, action: tuple) -> None:
        life_result = ArrayTools.create_value_array_of_size(self.castles_no, 0)

        agent_id = -1
        for castle_id in range(0, self.castles_no):
            for i in range(0, self.castle_sizes[castle_id]):
                agent_id += 1
                if action[agent_id] == 'idle':
                    state['defend'][castle_id][i] = False
                elif action[agent_id] == 'defend':
                    state['defend'][castle_id][i] = True
                    life_result[castle_id] += 1
                else:
                    castle_no = int(action[agent_id].split()[1])
                    state['defend'][castle_id][i] = False
                    life_result[castle_no] -= 1

        self.apply_life_result_to_state(state, life_result)

    def apply_life_result_to_state(self, state: dict, life_result: List[int]) -> None:
        for i in range(0, self.castles_no):
            if life_result[i] < 0:
                state['lifes'][i] += life_result[i]
                if state['lifes'][i] < 0:
                    state['lifes'][i] = 0
                if state['lifes'][i] == 0:
                    state['defeated'][i] = True

    def generate_possible_actions(self, state: dict) -> List[List]:
        possible_actions = []

        for castle_id in range(0, self.castles_no):
            for worker_id in range(0, self.castle_sizes[castle_id]):
                possible_actions.append(['idle'])
                if state['defeated'][castle_id]:
                    continue
                if not state['defend'][castle_id][worker_id]:
                    possible_actions[-1].append('defend')
                for enemy_castle_id in range(0, self.castles_no):
                    if enemy_castle_id == castle_id:
                        continue
                    possible_actions[-1].append(f'attack {enemy_castle_id}')

        return possible_actions
