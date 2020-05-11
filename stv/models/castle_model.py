from stv.models.model_generator import ModelGenerator
from stv.tools.list_tools import ListTools
from typing import List
import itertools


class CastleModel(ModelGenerator):

    def __init__(self, castle_sizes: List[int], castles_life: List[int]):
        assert len(castle_sizes) == len(castles_life)
        super().__init__(agents_count=sum(castle_sizes))
        self._castle_sizes = castle_sizes
        self._castles_life = castles_life
        self._castles_no = len(castles_life)

    def _generate_initial_states(self):
        defend = []
        defeated = []
        for castle_id in range(0, self._castles_no):
            defeated.append(False)
            defend.append([])
            for i in range(0, self._castle_sizes[castle_id]):
                defend[castle_id].append(False)
        first_state = {'lifes': self._castles_life[:], 'defend': defend, 'defeated': defeated}
        self._add_state(first_state)

    def _get_props_for_state(self, state: hash) -> List[str]:
        props = []
        for i in range(0, 3):
            if state['lifes'][i] == 0:
                props.append(f'castle{i + 1}defeated')

        if sum(state['lifes']) == 0:
            props.append('alldefeated')

        return props

    def get_props_list(self) -> List[str]:
        props = ['castle1defeated', 'castle2defeated', 'castle3defeated', 'alldefeated']
        return props

    def _get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        castle_id = 0
        agent_no = 0
        size = 0
        for i in range(0, self._castles_no):
            prev_size = size
            size += self._castle_sizes[i]
            if agent_id < size:
                castle_id = i
                agent_no = agent_id - prev_size
                break

        defend = state['defend'][castle_id][agent_no]
        epistemic_state = {'defend': defend, 'defeated': state['defeated'], 'life': state['lifes'][castle_id]}

        return epistemic_state

    def _generate_model(self):
        current_state_id = -1

        for state in self.states:
            current_state_id += 1
            if sum(state['lifes']) == 0:
                continue

            possible_actions = self._generate_possible_actions(state)
            for action in itertools.product(*possible_actions):
                new_state = self._new_state_after_action(state, action)
                new_state_id = self._add_state(new_state)
                self.model.add_transition(current_state_id, new_state_id, list(action))

    def _new_state_after_action(self, state: dict, action: tuple) -> dict:
        defend = []
        for i in range(0, self._castles_no):
            defend.append(state['defend'][i][:])
        new_state = {'lifes': state['lifes'][:],
                     'defend': defend, 'defeated': state['defeated'][:]}
        self._apply_action_to_state(new_state, action)

        return new_state

    def _apply_action_to_state(self, state: dict, action: tuple) -> None:
        life_result = [0 for _ in range(self._castles_no)]

        agent_id = -1
        for castle_id in range(0, self._castles_no):
            for i in range(0, self._castle_sizes[castle_id]):
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

        self._apply_life_result_to_state(state, life_result)

    def _apply_life_result_to_state(self, state: dict, life_result: List[int]) -> None:
        for i in range(0, self._castles_no):
            if life_result[i] < 0:
                state['lifes'][i] += life_result[i]
                if state['lifes'][i] < 0:
                    state['lifes'][i] = 0
                if state['lifes'][i] == 0:
                    state['defeated'][i] = True

    def _generate_possible_actions(self, state: dict) -> List[List]:
        possible_actions = []

        for castle_id in range(0, self._castles_no):
            for worker_id in range(0, self._castle_sizes[castle_id]):
                possible_actions.append(['idle'])
                if state['defeated'][castle_id]:
                    continue
                if not state['defend'][castle_id][worker_id]:
                    possible_actions[-1].append('defend')
                for enemy_castle_id in range(0, self._castles_no):
                    if enemy_castle_id == castle_id:
                        continue
                    possible_actions[-1].append(f'attack {enemy_castle_id}')

        return possible_actions

    def get_actions(self):
        actions = []
        for castle_id in range(0, self._castles_no):
            for worker_id in range(0, self._castle_sizes[castle_id]):
                actions.append(['idle', 'defend'])
                for enemy_castle_id in range(0, self._castles_no):
                    if enemy_castle_id == castle_id:
                        continue
                    actions[-1].append(f'attack {enemy_castle_id}')
        return actions

    def get_winning_states(self, prop: str) -> List[int]:
        result = []
        for state_id in range(0, len(self.states)):
            state = self.states[state_id]
            if prop in state['props']:
                result.append(state_id)

        return result


if __name__ == "__main__":
    castle_model = CastleModel([1, 1, 1], [3, 3, 3])
    castle_model.generate()
