from stv.logics.atl.mv import mvatl_model
from stv.models import ModelGenerator
from typing import List, Set
import itertools
import copy


class PollutionModel(ModelGenerator):
    model_map = []
    sides = ["right", "up", "left", "down"]
    graph = []
    lattice = None

    def __init__(self, model_map, connections, no_drones, energies, comm_radius, first_place_id=0):
        super().__init__(agents_count=no_drones)
        self.model_map = model_map
        self.comm_radius = comm_radius  # Communication radius for drones
        self.prepare_lattice()
        self.create_map_graph(connections)
        self.energies = energies
        self.first_place_id = first_place_id

    def _generate_initial_states(self):
        places = []
        visited = []
        for _ in range(0, self.agents_count):
            places.append(self.first_place_id)
            visited.append({self.first_place_id})

        first_state = {
            "place": places,
            "energy": self.energies,
            "visited": visited,
        }

        first_state["prop"] = self.prop_for_state(first_state)
        first_state["pollution"] = self.readings_for_state(first_state)
        self._add_state(first_state)

    def create_map_graph(self, connections):
        """Creates graph from connections between places in the map"""
        self.graph = []
        for _ in range(0, len(self.model_map)):
            self.graph.append([])

        for con in connections:
            self.graph[con[0]].append(con[1])
            self.graph[con[1]].append(con[0])  # Uncomment for undirected graph

    def prepare_lattice(self):
        self.lattice = mvatl_model.QBAlgebra('t', 'f', [('td+tg', 't'),
                                                        ('tg', 'td+tg'),
                                                        ('td', 'td+tg'),
                                                        ('u', 'td'),
                                                        ('u', 'tg'),
                                                        ('fd', 'u'),
                                                        ('fg', 'u'),
                                                        ('fd+fg', 'fd'),
                                                        ('fd+fd', 'fg'),
                                                        ('f', 'fd+fg')],
                                             {('u', 'u'),
                                              ('t', 'f'),
                                              ('td', 'fd'),
                                              ('tg', 'fg'),
                                              ('fd+fg', 'td+tg')})

    def relation_between_places(self, place_id_1, place_id_2):
        """Computes relation between two places on the map as the (+x,+y)"""
        assert (place_id_1 != place_id_2)

        if place_id_1 == 0 and place_id_2 == 1:
            return "N"
        elif place_id_1 == 1 and place_id_2 == 0:
            return "S"
        elif place_id_1 == 1 and place_id_2 == 4:
            return "E"
        elif place_id_1 == 4 and place_id_2 == 1:
            return "W"
        elif place_id_1 == 2 and place_id_2 == 3:
            return "N"
        elif place_id_1 == 3 and place_id_2 == 2:
            return "S"
        elif place_id_1 == 4 and place_id_2 == 3:
            return "S"
        elif place_id_1 == 3 and place_id_2 == 4:
            return "N"
        elif place_id_1 == 3 and place_id_2 == 8:
            return "E"
        elif place_id_1 == 8 and place_id_2 == 3:
            return "W"
        elif place_id_1 == 2 and place_id_2 == 5:
            return "E"
        elif place_id_1 == 5 and place_id_2 == 2:
            return "W"
        elif place_id_1 == 8 and place_id_2 == 5:
            return "S"
        elif place_id_1 == 5 and place_id_2 == 8:
            return "N"
        elif place_id_1 == 5 and place_id_2 == 6:
            return "E"
        elif place_id_1 == 6 and place_id_2 == 5:
            return "W"
        elif place_id_1 == 6 and place_id_2 == 7:
            return "N"
        elif place_id_1 == 7 and place_id_2 == 6:
            return "S"

    def _generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            available_actions = self.prepare_available_actions(state)
            for drone_actions in itertools.product(*available_actions):
                new_state, actions = self.new_state_after_action(state, drone_actions)
                new_state_number = self._add_state(new_state)
                self.model.add_transition(current_state_number, new_state_number, actions)

    def prepare_available_actions(self, state):
        available_actions = []
        for drone_number in range(0, self.agents_count):
            available_actions.append([])
            available_actions[drone_number].append(-1)  # Wait
            drone_energy = state["energy"][drone_number]
            if drone_energy == 0:
                continue
            current_place = state["place"][drone_number]
            for place_id in self.graph[current_place]:
                s = self.relation_between_places(current_place, place_id)
                available_actions[drone_number].append([s, place_id])

        return available_actions

    def new_state_after_action(self, state, drone_actions):
        places = state["place"][:]
        energies = state["energy"][:]
        visited = copy.deepcopy(state["visited"])
        actions = []
        drone_number = -1
        for d_action in drone_actions:
            drone_number += 1
            if energies[drone_number] > 0:
                energies[drone_number] -= 1
            if d_action == -1:
                actions.append("Wait")
                continue
            next_place = d_action[1]
            places[drone_number] = next_place
            visited[drone_number].add(next_place)
            actions.append(d_action[0])

        new_state = {
            "place": places,
            "energy": energies,
            "visited": visited,
        }

        new_state["pollution"] = self.readings_for_state(new_state)

        self.add_props_to_state(new_state)

        return new_state, actions

    def readings_for_state(self, state):
        readings = []
        for drone in range(0, self.agents_count):
            drone_reading = self.drone_reading_for_place(drone, state['place'][drone])
            prop = self.value_for_prop(drone_reading, self.model_map[state['place'][drone]]['PM2.5'])
            readings.append(prop)
        return readings

    def drone_reading_for_place(self, drone, place):
        # TODO: improve
        return self.model_map[place]["d_PM2.5"]

    def _get_epistemic_state(self, state: hash, agent_id: int) -> hash:
        drone_place = state['place'][agent_id]
        epistemic_state = {'place': state['place'][:], 'energy': state['energy'][:],
                           'visited': copy.deepcopy(state['visited'])}
        for coal_drone in range(0, self.agents_count):
            if coal_drone == agent_id:
                continue
            coal_drone_place = state['place'][coal_drone]
            if self.is_within_radius(drone_place, coal_drone_place):
                continue
            epistemic_state['place'][coal_drone] = -1
            epistemic_state['energy'][coal_drone] = -1
            epistemic_state['visited'][coal_drone] = []
        return epistemic_state

    def is_within_radius(self, place1, place2):
        x1 = self.model_map[place1]['x']
        y1 = self.model_map[place1]['y']
        x2 = self.model_map[place2]['x']
        y2 = self.model_map[place2]['y']
        distance = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)
        return distance <= (self.comm_radius ** 2)

    def _add_state(self, state: hash) -> int:
        # TODO modify that
        self.add_props_to_state(state)
        # state['props'] = self._get_props_for_state(state)
        new_state_number = self._get_state_id(state)
        for i in range(0, self.agents_count):
            epistemic_state = self._get_epistemic_state(state, i)
            self._add_to_epistemic_dictionary(epistemic_state, new_state_number, i)
        return new_state_number

    def _get_props_for_state(self, state: hash) -> List[str]:
        pass

    def prop_for_state(self, state) -> []:
        p = []
        for place in state["place"]:
            p.append(self.value_for_prop(self.model_map[place]["d_PM2.5"], self.model_map[place]["PM2.5"]))

        return p

    def add_props_to_state(self, state: hash) -> None:
        for place_number in range(0, len(self.model_map)):
            prop_name = "pol" + str(place_number)
            state[prop_name] = self.pol_prop_in_state(state, place_number)
            prop_name = "polD" + str(place_number)
            state[prop_name] = self.pol_propD_in_state(state, place_number)
            prop_name = "polE" + str(place_number)
            state[prop_name] = self.pol_propE_in_state(place_number)
            prop_name = "loc" + str(place_number)
            state[prop_name] = self.loc_prop_in_state(state, place_number)

        state['polnew'] = self.pol_new_in_state(state)

        state['locA'] = self.loc_all_prop_in_state(state)

    def pol_new_in_state(self, state) -> []:
        pol_prop = []
        for drone_number in range(0, self.agents_count):
            drone_reading = self.drone_reading_for_place(drone_number, state['place'][drone_number])
            prop = self.value_for_prop(drone_reading, self.model_map[state['place'][drone_number]]['PM2.5'])
            pol_prop.append(prop)

        return pol_prop

    def pol_prop_in_state(self, state, place_number) -> []:
        pol_prop = []
        for drone_number in range(0, self.agents_count):
            if state['place'][drone_number] != place_number:
                pol_prop.append('f')
                continue
            drone_reading = self.drone_reading_for_place(drone_number, state['place'][drone_number])
            prop = self.value_for_prop(drone_reading, self.model_map[state['place'][drone_number]]['PM2.5'])
            pol_prop.append(prop)

        return pol_prop

    def pol_propD_in_state(self, state, place_number) -> []:
        pol_prop = []
        return_prop = 'f'
        for drone_number in range(0, self.agents_count):
            if state['place'][drone_number] != place_number:
                continue
            drone_reading = self.drone_reading_for_place(drone_number, state['place'][drone_number])
            prop = self.value_for_prop(drone_reading, self.model_map[state['place'][drone_number]]['PM2.5'])
            if prop == 't':
                return_prop = 't'
            elif return_prop == 't' or prop == return_prop:
                continue
            elif prop[0] == 't' and return_prop[0] != 't':
                return_prop = prop
            elif (prop == 'td' and return_prop == 'tg') or (prop == 'tg' and return_prop == 'td'):
                return_prop = 't'
            elif return_prop[0] == 't':
                continue
            elif prop == 'u':
                return_prop = 'u'
            elif (prop == 'fd' and return_prop == 'fg') or (prop == 'fg' and return_prop == 'fd'):
                return_prop = 'u'

        pol_prop.append(return_prop)
        return pol_prop

    def pol_propE_in_state(self, place_number) -> []:
        pol_prop = [self.value_for_prop(self.model_map[place_number]['PM2.5'], self.model_map[place_number]['d_PM2.5'])]
        return pol_prop

    def loc_prop_in_state(self, state, place_number):
        loc_prop = []
        for drone_number in range(0, self.agents_count):
            prop = 'f'
            if state['place'][drone_number] == place_number:
                prop = 't'
            loc_prop.append(prop)

        return loc_prop

    def loc_all_prop_in_state(self, state):
        loc_prop = []
        for drone_number in range(0, self.agents_count):
            if len(state['visited'][drone_number]) == len(self.model_map):
                prop = 't'
            else:
                prop = 'f'
            loc_prop.append(prop)

        return loc_prop

    def print_states(self):
        for i in range(0, len(self.states)):
            print(i, self.states[i])

    def get_actions(self) -> List[List[str]]:
        drone_actions = ['N', 'E', 'S', 'W', 'Wait']
        actions = []
        for drone in range(0, self.agents_count):
            actions.append(drone_actions[:])

        return actions

    def get_props_list(self) -> List[str]:
        pass

    def get_winning_states(self, prop: str) -> Set[int]:
        pass

    @staticmethod
    def value_for_prop(v1, v2):
        if v1 == "t" and v2 == "t":
            return "t"
        if v1 == "t" and v2 == "f":
            return "td"
        if v1 == "t" and v2 == "u":
            return "td"
        if v1 == "f" and v2 == "t":
            return "tg"
        if v1 == "f" and v2 == "f":
            return "f"
        if v1 == "f" and v2 == "u":
            return "fd"
        if v1 == "u" and v2 == "t":
            return "tg"
        if v1 == "u" and v2 == "f":
            return "fg"
        if v1 == "u" and v2 == "u":
            return "u"

    @staticmethod
    def keep_values_in_list(the_list, val):
        return [value for value in the_list if value == val]

    @staticmethod
    def print_state(state):
        print("State places:", state["place"])
        print("State energies:", state["energy"])
        print("State visited places:", state["visited"])
        print("Pollutions:", state["pollution"])
