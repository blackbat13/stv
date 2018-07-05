from comparing_strats.simple_model import SimpleModel
import itertools
from typing import List


class MachineModel:
    model = None
    states = []
    states_dictionary = {}
    state_number = 0
    no_robots = 0
    no_machines = 0
    map = []
    machine_requirements = []
    items_limit = 0
    map_size = (0, 0)
    machine_positions = []
    robot_positions = []
    obstacle_positions = []
    epistemic_states_dictionaries = []
    imperfect = False

    def __init__(self, no_robots: int, no_machines: int, map_size: (int, int), items_limit: int,
                 robot_positions: List, machine_positions: List,
                 obstacle_positions: List, machine_requirements: List, imperfect: bool):
        self.no_robots = no_robots
        self.no_machines = no_machines
        self.items_limit = items_limit
        self.map_size = map_size
        self.machine_positions = machine_positions
        self.robot_positions = robot_positions
        self.obstacle_positions = obstacle_positions
        self.machine_requirements = machine_requirements
        self.imperfect = imperfect

        self.prepare_map()
        self.print_map()
        if imperfect:
            self.prepare_epistemic_dictionaries()

        self.model = SimpleModel(no_robots + no_machines)
        self.generate_model()
        if imperfect:
            self.prepare_epistemic_relation()

    def prepare_map(self):
        self.create_map()
        self.add_robots_to_map()
        self.add_machines_to_map()
        self.add_obstacles_to_map()

    def create_map(self):
        self.map = []
        for i in range(0, self.map_size[1]):
            self.map.append([])
            for j in range(0, self.map_size[0]):
                self.map[i].append(0)

    def add_robots_to_map(self):
        for i in range(0, self.no_robots):
            x, y = self.robot_positions[i]
            self.map[y][x] = i + 1

    def add_machines_to_map(self):
        for i in range(0, self.no_machines):
            x, y = self.machine_positions[i]
            self.map[y][x] = i + self.no_robots + 1

    def add_obstacles_to_map(self):
        for obstacle_pos in self.obstacle_positions:
            x, y = obstacle_pos
            self.map[y][x] = -1

    def print_map(self):
        map_string = ""
        for y in range(0, len(self.map)):
            for x in range(0, len(self.map[y])):
                if self.map[y][x] == 0:
                    map_string += '-'
                elif self.map[y][x] > 0:
                    if self.map[y][x] <= self.no_robots:
                        map_string += f'R{self.map[y][x]}'
                    else:
                        map_string += f'M{self.map[y][x] - self.no_robots}'
                else:
                    map_string += '#'
            map_string += '\n'
        print(map_string)

    def prepare_epistemic_dictionaries(self):
        self.epistemic_states_dictionaries.clear()
        for _ in range(0, self.no_robots):
            self.epistemic_states_dictionaries.append({})

    def generate_model(self):
        robot_items = []
        for i in range(0, self.no_robots):
            robot_items.append(-1)

        machine_inputs = []
        machine_outputs = []
        items_count = []

        for _ in range(0, self.no_machines):
            machine_inputs.append([])
            machine_outputs.append(0)
            items_count.append(0)
            for _ in range(0, self.no_machines):
                machine_inputs[-1].append(0)

        first_state = {'r_pos': self.robot_positions,
                       'm_pos': self.machine_positions,
                       'r_items': robot_items, 'm_in': machine_inputs, 'm_out': machine_outputs,
                       'it_count': items_count}

        self.add_state(first_state)

        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            available_actions = []

            is_end_state = True

            for i in range(0, self.no_machines):
                if state['it_count'][i] < self.items_limit:
                    is_end_state = False
                    break

            for i in range(0, self.no_robots):
                available_actions.append([])
                if is_end_state:
                    available_actions[-1].append(('Wait', 0))
                    continue

                available_actions[-1].extend(self.robot_available_actions(robot_no=i, state=state))

            for i in range(0, self.no_machines):
                available_actions.append([])
                available_actions[-1].extend(self.machine_available_actions(machine_no=i, state=state))

            for current_actions in itertools.product(*available_actions):
                robot_positions = state['r_pos'][:]
                machine_positions = state['m_pos'][:]
                robot_items = state['r_items'][:]
                machine_outputs = state['m_out'][:]
                produced_items_count = state['it_count'][:]
                machine_inputs = []
                for i in range(0, self.no_machines):
                    machine_inputs.append(state['m_in'][i][:])

                actions = []

                for robot_number in range(0, self.no_robots):
                    robot_action = current_actions[robot_number]
                    actions.append(robot_action[0])
                    if robot_action[0] in ['N', 'W', 'S', 'E']:
                        robot_positions[robot_number] = (robot_action[1][0], robot_action[1][1])

                    if robot_action[0] == 'leave':
                        machine_inputs[robot_action[1]][robot_items[robot_number]] += 1
                        robot_items[robot_number] = -1

                    if robot_action[0] == 'pick':
                        machine_outputs[robot_action[1]] -= 1
                        robot_items[robot_number] = robot_action[1]

                for machine_number in range(0, self.no_machines):
                    machine_action = current_actions[self.no_robots + machine_number]
                    actions.append(machine_action[0])
                    if machine_action[0] == 'produce':
                        for i in range(0, len(self.machine_requirements[machine_number])):
                            machine_inputs[machine_number][i] -= self.machine_requirements[machine_number][i]

                        machine_outputs[machine_number] += 1
                        produced_items_count[machine_number] += 1

                new_state = {'r_pos': robot_positions, 'm_pos': machine_positions,
                             'r_items': robot_items, 'm_in': machine_inputs,
                             'm_out': machine_outputs, 'it_count': produced_items_count}

                new_state_number = self.add_state(new_state)
                self.model.add_transition(current_state_number, new_state_number, actions)

        self.model.states = self.states

    def can_move(self, new_position: (int, int)) -> bool:
        return 0 <= new_position[0] < self.map_size[0] and 0 <= new_position[1] < self.map_size[1] and \
               self.map[new_position[1]][new_position[0]] != -1

    def robot_available_actions(self, robot_no, state):
        robot_item = state['r_items'][robot_no]
        robot_position = state['r_pos'][robot_no]
        available_actions = []

        movement = [('E', (-1, 0)), ('W', (1, 0)), ('N', (0, -1)), ('S', (0, 1))]
        for move in movement:
            x, y = move[1]
            label = move[0]
            if self.can_move((robot_position[0] + x, robot_position[1] + y)):
                available_actions.append((label, (robot_position[0] + x, robot_position[1] + y)))

        machine_number = -1
        for machine_position in state['m_pos']:
            machine_number += 1
            if robot_position[0] == machine_position[0] and robot_position[1] == machine_position[1]:
                if robot_item != -1 and self.machine_requirements[machine_number][robot_item] > 0:
                    available_actions.append(('leave', machine_number))

                if robot_item == -1 and state['m_out'][machine_number] > 0:
                    available_actions.append(('pick', machine_number))

        available_actions.append(('Wait', 0))
        return available_actions[:]

    def machine_available_actions(self, machine_no, state):
        machine_input = state['m_in'][machine_no]
        met_requirements = True
        for i in range(0, len(machine_input)):
            if machine_input[i] < self.machine_requirements[machine_no][i]:
                met_requirements = False
                break

        if state['it_count'][machine_no] >= self.items_limit:
            met_requirements = False

        if met_requirements:
            return [('produce', machine_no)]
        else:
            return [('Wait', 0)]

    def add_state(self, state: hash) -> int:
        new_state_number = self.get_state_number(state)
        if self.imperfect:
            for i in range(0, self.no_robots):
                epistemic_state = self.get_epistemic_state(state, i)
                self.add_to_epistemic_dictionary(epistemic_state, new_state_number, i)
        return new_state_number

    def get_state_number(self, state: hash) -> int:
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.states_dictionary:
            self.states_dictionary[state_str] = self.state_number
            new_state_number = self.state_number
            self.states.append(state)
            self.state_number += 1
        else:
            new_state_number = self.states_dictionary[state_str]

        return new_state_number

    def get_epistemic_state(self, state: hash, agent_number: int) -> hash:
        if agent_number >= self.no_robots:
            return state

        robot_positions = state['r_pos'][:]
        robot_items = state['r_items'][:]
        for i in range(0, self.no_robots):
            if i == agent_number:
                continue

            robot_positions[i] = -1
            robot_items[i] = -1

        machine_positions = state['m_pos'][:]
        machine_outputs = state['m_out'][:]
        produced_items_count = state['it_count'][:]
        machine_inputs = []
        for i in range(0, self.no_machines):
            machine_inputs.append(state['m_in'][i][:])

        epistemic_state = {'r_pos': robot_positions, 'm_pos': machine_positions,
                           'r_items': robot_items, 'm_in': machine_inputs,
                           'm_out': machine_outputs, 'it_count': produced_items_count}
        return epistemic_state

    def add_to_epistemic_dictionary(self, state: hash, new_state_number: int, agent_number: int):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.epistemic_states_dictionaries[agent_number]:
            self.epistemic_states_dictionaries[agent_number][state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionaries[agent_number][state_str].add(new_state_number)

    def prepare_epistemic_relation(self):
        for i in range(0, self.no_robots):
            for state, epistemic_class in self.epistemic_states_dictionaries[i].items():
                self.model.add_epistemic_class(i, epistemic_class)

    def get_actions(self):
        actions = []
        for _ in range(0, self.no_robots):
            actions.append([])
            actions[-1].extend(['W', 'N', 'E', 'S', 'Wait', 'pick', 'leave'])

        for _ in range(0, self.no_machines):
            actions.append([])
            actions[-1].extend(['Wait', 'produce'])

        return actions

    @staticmethod
    def random_factory_layout(size: int, no_robots: int, no_machines: int):
        robot_positions = []
        machine_positions = []
        obstacle_positions = []
        machine_requirements = []
        for i in range(0, no_robots):
            robot_positions.append((i, 0))
        for i in range(0, no_machines):
            machine_positions.append((size - 1 - i, size - 1))
            machine_req = []
            for j in range(0, no_machines):
                machine_req.append(0)

            if i + 1 < no_machines:
                machine_req[i + 1] = 1

            machine_requirements.append(machine_req[:])

        return robot_positions, machine_positions, obstacle_positions, machine_requirements
