from stv.models.model_generator import ModelGenerator
from typing import List, Set
import itertools
from enum import Enum


class MachineModel(ModelGenerator):
    class RobotAction(Enum):
        N = 1
        E = 2
        S = 3
        W = 4
        WAIT = 5
        PICK = 6
        LEAVE = 7

    class MapItems(Enum):
        EMPTY = 0
        OBSTACLE = -1

    def __init__(self, no_robots: int, no_machines: int, map_size: (int, int), items_limit: int,
                 robot_positions: List, machine_positions: List,
                 obstacle_positions: List, machine_requirements: List, production_times: List, imperfect: bool):
        super().__init__(agents_count=no_robots + no_machines)

        self.no_robots = no_robots
        self.no_machines = no_machines
        self.items_limit = items_limit
        self.map_size = map_size
        self.machine_positions = machine_positions
        self.robot_positions = robot_positions
        self.obstacle_positions = obstacle_positions
        self.machine_requirements = machine_requirements
        self.production_times = production_times
        self.imperfect = imperfect
        self.output_items_limit = 1
        self.name: str = "Classic Machine Model"
        self.map_item_symbols = {self.MapItems.EMPTY: '.', self.MapItems.OBSTACLE: '#'}
        self.prepare_map()
        self.print_map()

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
                if self.map[y][x] > 0:
                    if self.map[y][x] <= self.no_robots:
                        map_string += f'R{self.map[y][x]}'
                    else:
                        map_string += f'M{self.map[y][x] - self.no_robots}'
                else:
                    map_string += self.map_item_symbols[self.MapItems(self.map[y][x])]
            map_string += '\n'
        print(map_string)

    def generate_first_state(self):
        robot_items = []
        for i in range(0, self.no_robots):
            robot_items.append(-1)

        machine_inputs = []
        machine_outputs = []
        items_count = []
        machine_clocks = []

        for _ in range(0, self.no_machines):
            machine_inputs.append([])
            machine_outputs.append(0)
            items_count.append(0)
            machine_clocks.append(0)
            for _ in range(0, self.no_machines):
                machine_inputs[-1].append(0)

        first_state = {'r_pos': self.robot_positions,
                       'm_pos': self.machine_positions,
                       'r_items': robot_items, 'm_in': machine_inputs, 'm_out': machine_outputs,
                       'it_count': items_count, 'pr_times': self.production_times, 'm_clocks': machine_clocks,
                       'prop_stuck': False}
        return first_state

    def _generate_initial_states(self):
        self._add_state(self.generate_first_state())

    def _generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            available_actions = []

            is_end_state = self.check_if_end_state(state)

            for i in range(0, self.no_robots):
                available_actions.append([])
                if is_end_state:
                    available_actions[-1].append(('Wait', 0))
                    continue

                is_in_collission = self.check_if_in_collision(state, i)
                if is_in_collission:
                    available_actions[-1].append(('Wait', 0))
                    continue

                available_actions[-1].extend(self.robot_available_actions(robot_no=i, state=state))

            for i in range(0, self.no_machines):
                available_actions.append([])
                available_actions[-1].extend(self.machine_available_actions(machine_no=i, state=state))

            for current_actions in itertools.product(*available_actions):
                new_state, actions = self.new_state_after_action(state, current_actions)

                new_state_number = self._add_state(new_state)
                self.model.add_transition(current_state_number, new_state_number, actions)

        self.model.states = self.states

    def check_if_end_state(self, state) -> bool:
        for i in range(0, self.no_machines):
            if state['it_count'][i] < self.items_limit:
                return False

        return True

    def check_if_in_collision(self, state, robot_index) -> bool:
        for i in range(0, self.no_robots):
            if i == robot_index:
                continue
            if state['r_pos'][robot_index][0] == state['r_pos'][i][0] and state['r_pos'][robot_index][1] == \
                    state['r_pos'][i][1]:
                return True

        return False

    def new_state_after_action(self, state, current_actions):
        robot_positions = state['r_pos'][:]
        machine_positions = state['m_pos'][:]
        robot_items = state['r_items'][:]
        machine_outputs = state['m_out'][:]
        produced_items_count = state['it_count'][:]
        machine_clocks = state['m_clocks'][:]
        production_times = state['pr_times'][:]
        prop_stuck = state['prop_stuck']
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
                if machine_clocks[machine_number] >= production_times[machine_number]:
                    machine_clocks[machine_number] = 0
                    for i in range(0, len(self.machine_requirements[machine_number])):
                        machine_inputs[machine_number][i] -= self.machine_requirements[machine_number][i]

                    machine_outputs[machine_number] += 1
                    produced_items_count[machine_number] += 1
                else:
                    machine_clocks[machine_number] += 1
            elif machine_action[0] == 'Wait' and machine_action[1]:
                prop_stuck = True

        new_state = {'r_pos': robot_positions, 'm_pos': machine_positions,
                     'r_items': robot_items, 'm_in': machine_inputs,
                     'm_out': machine_outputs, 'it_count': produced_items_count,
                     'pr_times': production_times, 'm_clocks': machine_clocks,
                     'prop_stuck': prop_stuck}

        return new_state, actions

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
        is_stuck = False
        met_requirements = self.machine_met_requirements(machine_no, state)
        if met_requirements and state['m_clocks'][machine_no] >= state['pr_times'][machine_no] and state['m_out'][
            machine_no] >= self.output_items_limit and state['it_count'][
            machine_no] < self.items_limit:
            is_stuck = True

        if (state['m_clocks'][machine_no] >= state['pr_times'][machine_no] and state['m_out'][
            machine_no] >= self.output_items_limit) \
                or state['it_count'][machine_no] >= self.items_limit:
            met_requirements = False

        if met_requirements:
            return [('produce', machine_no)]
        else:
            return [('Wait', is_stuck)]

    def machine_met_requirements(self, machine_no, state):
        machine_input = state['m_in'][machine_no]
        for i in range(0, len(machine_input)):
            if machine_input[i] < self.machine_requirements[machine_no][i]:
                return False

        return True

    def _get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        if agent_id >= self.no_robots:
            return state

        robot_positions = state['r_pos'][:]
        robot_items = state['r_items'][:]
        for i in range(0, self.no_robots):
            if i == agent_id:
                continue

            robot_positions[i] = -1
            robot_items[i] = -1

        machine_outputs = state['m_out'][:]
        produced_items_count = state['it_count'][:]
        machine_inputs = []
        for i in range(0, self.no_machines):
            machine_inputs.append(state['m_in'][i][:])

        epistemic_state = {'r_pos': robot_positions,
                           'r_items': robot_items, 'm_in': machine_inputs,
                           'm_out': machine_outputs, 'it_count': produced_items_count}
        return epistemic_state

    def get_actions(self):
        actions = []
        for _ in range(0, self.no_robots):
            actions.append([])
            actions[-1].extend(['W', 'N', 'E', 'S', 'Wait', 'pick', 'leave'])

        for _ in range(0, self.no_machines):
            actions.append([])
            actions[-1].extend(['Wait', 'produce'])

        return actions

    def _get_props_for_state(self, state: hash) -> List[str]:
        pass

    def get_props_list(self) -> List[str]:
        pass

    def get_winning_states(self, prop: str) -> Set[int]:
        pass

    @staticmethod
    def random_factory_layout(size: int, no_robots: int, no_machines: int, no_charging_stations: int = 0,
                              no_storage: int = 0):
        robot_positions = []
        machine_positions = []
        obstacle_positions = []
        machine_requirements = []
        production_times = []
        charging_stations = []
        storages = []
        for i in range(0, no_robots):
            robot_positions.append((i, 0))
        for i in range(0, no_machines):
            machine_positions.append((size - 1 - i, size - 1))
            production_times.append(0)
            machine_req = []
            for j in range(0, no_machines):
                machine_req.append(0)

            if i + 1 < no_machines:
                machine_req[i + 1] = 1

            machine_requirements.append(machine_req[:])

        for i in range(0, no_charging_stations):
            charging_stations.append((i, 1))

        for i in range(0, no_storage):
            storages.append((i, size - 2))

        return robot_positions, machine_positions, obstacle_positions, machine_requirements, production_times, charging_stations, storages


class MachineModelWithCharging(MachineModel):
    class MapItems(Enum):
        EMPTY = 0
        OBSTACLE = -1
        CHARGING_STATION = -2

    def __init__(self, no_robots: int, no_machines: int, map_size: (int, int), items_limit: int,
                 robot_positions: List, machine_positions: List,
                 obstacle_positions: List, charging_stations_positions: List, machine_requirements: List,
                 production_times: List, imperfect: bool):

        self.charging_stations_positions = charging_stations_positions

        super().__init__(no_robots, no_machines, map_size, items_limit, robot_positions, machine_positions,
                         obstacle_positions, machine_requirements, production_times, imperfect)
        self.name: str = "Machine Model With Charging"
        self.max_charge = 10
        self.map_item_symbols = {self.MapItems.EMPTY: '.', self.MapItems.OBSTACLE: '#',
                                 self.MapItems.CHARGING_STATION: 'C'}

    def prepare_map(self):
        super().prepare_map()
        self.add_charging_stations_to_map()

    def add_charging_stations_to_map(self):
        for charging_station_pos in self.charging_stations_positions:
            x, y = charging_station_pos
            self.map[y][x] = -2

    def generate_first_state(self):
        first_state = super().generate_first_state()
        robot_charges = []
        for i in range(0, self.no_robots):
            robot_charges.append(self.max_charge)

        first_state['r_charge'] = robot_charges
        first_state['c_pos'] = self.charging_stations_positions
        return first_state

    def new_state_after_action(self, state, current_actions):
        new_state, actions = super().new_state_after_action(state, current_actions)

        ch_station_positions = state['c_pos'][:]
        robot_charges = state['r_charge'][:]

        for robot_number in range(0, self.no_robots):
            robot_action = current_actions[robot_number]

            if robot_action[0] != 'Wait':
                robot_charges[robot_number] -= 1

            if robot_action[0] == 'charge':
                robot_charges[robot_number] = self.max_charge

        new_state['c_pos'] = ch_station_positions
        new_state['r_charge'] = robot_charges

        return new_state, actions

    def get_actions(self):
        actions = []
        for _ in range(0, self.no_robots):
            actions.append([])
            actions[-1].extend(['W', 'N', 'E', 'S', 'Wait', 'pick', 'leave', 'charge'])

        for _ in range(0, self.no_machines):
            actions.append([])
            actions[-1].extend(['Wait', 'produce'])

        return actions

    def robot_available_actions(self, robot_no, state):
        if state['r_charge'][robot_no] == 0:
            return [('Wait', 0)]
        available_actions = super().robot_available_actions(robot_no, state)
        robot_position = state['r_pos'][robot_no]
        for ch_station_position in state['c_pos']:
            if robot_position[0] == ch_station_position[0] and robot_position[1] == ch_station_position[1]:
                available_actions.append(('charge', 0))

        return available_actions[:]

    def _get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        if agent_id >= self.no_robots:
            return state

        robot_positions = state['r_pos'][:]
        robot_items = state['r_items'][:]
        robot_charges = state['r_charge'][:]
        for i in range(0, self.no_robots):
            if i == agent_id:
                continue

            robot_positions[i] = -1
            robot_items[i] = -1
            robot_charges[i] = -1

        machine_positions = state['m_pos'][:]
        ch_station_positions = state['c_pos'][:]
        machine_outputs = state['m_out'][:]
        produced_items_count = state['it_count'][:]
        machine_inputs = []
        for i in range(0, self.no_machines):
            machine_inputs.append(state['m_in'][i][:])

        epistemic_state = {'r_pos': robot_positions,
                           'm_pos': machine_positions,
                           'c_pos': ch_station_positions,
                           'r_charge': robot_charges,
                           'r_items': robot_items, 'm_in': machine_inputs,
                           'm_out': machine_outputs, 'it_count': produced_items_count}
        return epistemic_state


class MachineModelWithStorage(MachineModel):
    class MapItems(Enum):
        EMPTY = 0
        OBSTACLE = -1
        STORAGE = -2

    map_item_symbols = {MapItems.EMPTY: '.', MapItems.OBSTACLE: '#', MapItems.STORAGE: 'S'}

    def __init__(self, no_robots: int, no_machines: int, map_size: (int, int), items_limit: int,
                 robot_positions: List, machine_positions: List,
                 obstacle_positions: List, storage_positions: List, machine_requirements: List,
                 production_times: List, imperfect: bool):

        self.storage_positions = storage_positions
        self.no_storages = len(self.storage_positions)

        super().__init__(no_robots, no_machines, map_size, items_limit, robot_positions, machine_positions,
                         obstacle_positions, machine_requirements, production_times, imperfect)
        self.name: str = "Machine Model With Storage"

    def prepare_map(self):
        super().prepare_map()
        self.add_storages_to_map()

    def add_storages_to_map(self):
        for storage_pos in self.storage_positions:
            x, y = storage_pos
            self.map[y][x] = -2

    def generate_first_state(self):
        first_state = super().generate_first_state()
        storages = []

        for i in range(0, self.no_storages):
            storages.append([])

        first_state['s_pos'] = self.storage_positions
        first_state['storage'] = storages
        return first_state

    def new_state_after_action(self, state, current_actions):
        new_state, actions = super().new_state_after_action(state, current_actions)
        robot_items = new_state['r_items'][:]
        storage_positions = state['s_pos'][:]
        storages = []
        for i in range(0, self.no_storages):
            storages.append(state['storage'][i][:])

        for robot_number in range(0, self.no_robots):
            robot_action = current_actions[robot_number]

            for i in range(0, self.no_machines):
                if robot_action[0] == 'pick' + str(i):
                    robot_items[robot_number] = i
                    storages[robot_action[1]].remove(i)

            if robot_action[0] == 'leave_s':
                storages[robot_action[1]].append(robot_items[robot_number])
                robot_items[robot_number] = -1

        new_state['s_pos'] = storage_positions
        new_state['r_items'] = robot_items
        new_state['storage'] = storages

        return new_state, actions

    def get_actions(self):
        actions = []
        for _ in range(0, self.no_robots):
            actions.append([])
            actions[-1].extend(['W', 'N', 'E', 'S', 'Wait', 'pick', 'leave', 'leave_s'])
            for i in range(0, self.no_machines):
                actions[-1].append('pick' + str(i))

        for _ in range(0, self.no_machines):
            actions.append([])
            actions[-1].extend(['Wait', 'produce'])

        return actions

    def robot_available_actions(self, robot_no, state):
        available_actions = super().robot_available_actions(robot_no, state)
        robot_position = state['r_pos'][robot_no]
        storage_index = -1
        for storage_position in state['s_pos']:
            storage_index += 1
            if robot_position[0] == storage_position[0] and robot_position[1] == storage_position[1]:
                if state['r_items'][robot_no] != -1:
                    available_actions.append(('leave_s', storage_index))
                else:
                    for item in state['storage'][storage_index]:
                        available_actions.append(('pick' + str(item), storage_index))

        return available_actions[:]

    def _get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        if agent_id >= self.no_robots:
            return state

        robot_positions = state['r_pos'][:]
        robot_items = state['r_items'][:]
        for i in range(0, self.no_robots):
            if i == agent_id:
                continue

            robot_positions[i] = -1
            robot_items[i] = -1

        machine_positions = state['m_pos'][:]
        machine_outputs = state['m_out'][:]
        produced_items_count = state['it_count'][:]
        storage_positions = state['s_pos'][:]
        machine_inputs = []
        for i in range(0, self.no_machines):
            machine_inputs.append(state['m_in'][i][:])
        storages = []
        for i in range(0, self.no_storages):
            storages.append(state['storage'][i][:])

        epistemic_state = {'r_pos': robot_positions,
                           'm_pos': machine_positions,
                           'r_items': robot_items, 'm_in': machine_inputs,
                           'm_out': machine_outputs, 'it_count': produced_items_count,
                           'storage': storages, 's_pos': storage_positions}
        return epistemic_state


class MachineModelWaiting(MachineModel):
    def __init__(self, no_robots: int, no_machines: int, map_size: (int, int), items_limit: int,
                 robot_positions: List, machine_positions: List,
                 obstacle_positions: List, machine_requirements: List,
                 production_times: List, imperfect: bool):

        super().__init__(no_robots, no_machines, map_size, items_limit, robot_positions, machine_positions,
                         obstacle_positions, machine_requirements, production_times, imperfect)
        self.name: str = "Machine Model With Waiting"

    def generate_first_state(self):
        first_state = super().generate_first_state()
        waiting_times = []
        for _ in range(0, self.no_machines):
            waiting_times.append(0)

        first_state['m_w_times'] = waiting_times
        return first_state

    def new_state_after_action(self, state, current_actions):
        new_state, actions = super().new_state_after_action(state, current_actions)

        waiting_times = state['m_w_times'][:]

        for machine_number in range(0, self.no_machines):
            machine_action = current_actions[self.no_robots + machine_number]

            if machine_action[0] == 'Produce':
                waiting_times[machine_number] = 0
            elif machine_action[0] == 'Wait' and state['it_count'][machine_number] < self.items_limit:
                waiting_times[machine_number] += 1

        new_state['m_w_times'] = waiting_times

        return new_state, actions

    def _get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        if agent_id >= self.no_robots:
            return state

        robot_positions = state['r_pos'][:]
        robot_items = state['r_items'][:]
        for i in range(0, self.no_robots):
            if i == agent_id:
                continue

            robot_positions[i] = -1
            robot_items[i] = -1

        machine_outputs = state['m_out'][:]
        produced_items_count = state['it_count'][:]
        machine_inputs = []
        for i in range(0, self.no_machines):
            machine_inputs.append(state['m_in'][i][:])

        epistemic_state = {'r_pos': robot_positions,
                           'r_items': robot_items, 'm_in': machine_inputs,
                           'm_out': machine_outputs, 'it_count': produced_items_count}
        return epistemic_state
