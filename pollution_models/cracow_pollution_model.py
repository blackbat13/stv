#!/usr/bin/python
# -*- coding: utf-8 -*-

from atl_model import ATLModel
import itertools
from mv_atl import mvatl_model, mvatl_parser
from enum import Enum
import random

map = []

connections = []

map.append({
    "id": 0,
    "name": "Vlastimila Hofmana",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 28,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 59,
    "x": 0,
    "y": 0
})

map.append({
    "id": 1,
    "name": "Leona Wyczółkowskiego",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 58,
    "temperature": 3,
    "pressure": 1007,
    "humidity": 55,
    "x": 1,
    "y": 0
})

connections.append([0, 1])

map.append({
    "id": 2,
    "name": "Aleje Trzech Wieszczów",
    "PM2.5": "t",
    "d_PM2.5": "f",
    "PM10": 170,
    "temperature": "u",
    "pressure": "u",
    "humidity": "u",
    "x": 2,
    "y": 0
})

connections.append([1, 2])

map.append({
    "id": 3,
    "name": "Wiedeńska",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 76,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 45,
    "x": 0,
    "y": 1
})

map.append({
    "id": 4,
    "name": "Przybyszewskiego 56",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 50,
    "temperature": 4,
    "pressure": 1009,
    "humidity": 59,
    "x": 1,
    "y": 1
})

connections.append([3, 4])
connections.append([1, 4])

map.append({
    "id": 5,
    "name": "Studencka",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 72,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 66,
    "x": 2,
    "y": 1
})

connections.append([2, 5])

map.append({
    "id": 6,
    "name": "Na Błonie",
    "PM2.5": "t",
    "d_PM2.5": "f",
    "PM10": 84,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 45,
    "x": 0,
    "y": 2
})

connections.append([3, 5])

map.append({
    "id": 7,
    "name": "osiedle Złota Podkowa",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 68,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 69,
    "x": 1,
    "y": 2
})

connections.append([6, 7])

map.append({
    "id": 8,
    "name": "aleja Juliusza Słowackiego",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 70,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 66,
    "x": 2,
    "y": 2
})

connections.append([5, 8])

map.append({
    "id": 9,
    "name": "aleja Kasztanowa",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 32,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 59,
    "x": 0,
    "y": 3
})

connections.append([6, 9])

map.append({
    "id": 10,
    "name": "aleja Jerzego Waszyngtona",
    "PM2.5": "f",
    "d_PM2.5": "f",
    "PM10": 30,
    "temperature": 4,
    "pressure": 1007,
    "humidity": 45,
    "x": 1,
    "y": 3
})

connections.append([9, 10])
connections.append([7, 10])

map.append({
    "id": 11,
    "name": "Prądnicka",
    "PM2.5": "t",
    "d_PM2.5": "f",
    "PM10": 212,
    "temperature": "u",
    "pressure": 1009,
    "humidity": "u",
    "x": 2,
    "y": 3
})

connections.append([8, 11])


class DroneAction(Enum):
    Wait = 0
    N = 1
    S = 2
    E = 3
    W = 4


class PollutionModel:
    model_map = []
    model = None
    states = []
    no_drones = 1
    sides = ["right", "up", "left", "down"]
    states_dictionary = {}
    epistemic_states_dictionary = []
    state_number = 0
    graph = []
    lattice = None

    def __init__(self, model_map, connections, no_drones, energies, comm_radius):
        self.model_map = model_map
        self.no_drones = no_drones
        self.comm_radius = comm_radius  # Communication radius for drones
        self.create_mvatl_model()
        self.prepare_epistemic_states_dictionary()
        self.create_map_graph(connections)

        first_state = self.create_first_state(energies)
        self.add_state(first_state)

        self.generate_model()
        self.model.states = self.states
        self.prepare_epistemic_relation()

    def create_first_state(self, energies):
        places = []
        visited = []
        for _ in range(0, self.no_drones):
            places.append(0)
            visited.append({0})

        first_state = {
            "map": self.model_map,
            "place": places,
            "energy": energies,
            "visited": visited
        }

        first_state["prop"] = self.prop_for_state(first_state)
        first_state["pollution"] = self.readings_for_state(first_state)
        return first_state

    def prepare_epistemic_states_dictionary(self):
        self.epistemic_states_dictionary = []
        for _ in range(0, self.no_drones):
            self.epistemic_states_dictionary.append({})

    def create_mvatl_model(self):
        # TODO: Approx number of states
        self.prepare_lattice()
        self.model = mvatl_model.MvATLModel(self.no_drones, 1000000, self.lattice)
        self.add_actions()

    def add_actions(self):
        actions = ['N', 'E', 'S', 'W', 'Wait']
        for drone in range(0, self.no_drones):
            for action in actions:
                self.model.add_action(drone, action)

    def create_map_graph(self, connections):
        """Creates graph from connections between places in the map"""
        self.graph = []
        for _ in range(0, len(self.model_map)):
            self.graph.append([])

        for con in connections:
            self.graph[con[0]].append(con[1])
            self.graph[con[1]].append(con[0])

    def prepare_lattice(self):
        self.lattice = mvatl_model.QBAlgebra('t', 'f', [('tg', 't'),
                                                        ('td', 't'), ('Td', 'td'), ('Tg', 'tg'),
                                                        ('u', 'Td'), ('u', 'Tg'), ('fd', 'u'),
                                                        ('fg', 'u'), ('f', 'fd'), ('f', 'fg')
                                                        ])

    def relation_between_places(self, place_id_1, place_id_2):
        """Computes relation between two places on the map as the (+x,+y)"""
        assert (place_id_1 != place_id_2)
        x = self.model_map[place_id_2]["x"] - self.model_map[place_id_1]["x"]
        y = self.model_map[place_id_2]["y"] - self.model_map[place_id_1]["y"]
        return x, y

    def generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            available_actions = self.prepare_available_actions(state)
            for drone_actions in itertools.product(*available_actions):
                new_state, actions = self.new_state_after_action(state, drone_actions)
                new_state_number = self.add_state(new_state)
                self.model.add_transition(current_state_number, new_state_number, actions)

    def prepare_available_actions(self, state):
        available_actions = []
        for drone_number in range(0, self.no_drones):
            available_actions.append([])
            available_actions[drone_number].append(-1)  # Wait
            drone_energy = state["energy"][drone_number]
            if drone_energy == 0:
                continue
            current_place = state["place"][drone_number]
            for place_id in self.graph[current_place]:
                x, y = self.relation_between_places(current_place, place_id)
                available_actions[drone_number].append([x, y, place_id])

        return available_actions

    def new_state_after_action(self, state, drone_actions):
        places = state["place"][:]
        energies = state["energy"][:]
        visited = state["visited"][:]
        actions = {}
        drone_number = -1
        for d_action in drone_actions:
            drone_number += 1
            if energies[drone_number] > 0:
                energies[drone_number] -= 1
            if d_action == -1:
                actions[drone_number] = "Wait"
                continue
            next_place = d_action[2]
            places[drone_number] = next_place
            visited[drone_number] = visited[drone_number].copy()
            visited[drone_number].add(next_place)
            actions[drone_number] = self.movement_to_action(d_action[0], d_action[1])

        new_state = {
            "map": self.model_map,
            "place": places,
            "energy": energies,
            "visited": visited
        }

        new_state["prop"] = self.prop_for_state(new_state)
        new_state["pollution"] = self.readings_for_state(new_state)

        return new_state, actions

    def readings_for_state(self, state):
        readings = []
        for drone in range(0, self.no_drones):
            drone_reading = self.drone_rading_for_place(drone, state['place'][drone])
            prop = self.value_for_prop(drone_reading, self.model_map[state['place'][drone]]['PM2.5'])
            readings.append(prop)
        return readings

    def drone_rading_for_place(self, drone, place):
        # TODO: improve
        return 't'
        rand = random.randint(0, 2)
        if rand == 0:
            return 't'
        elif rand == 1:
            return 'f'
        else:
            return 'u'

    def movement_to_action(self, x, y):
        """Transform movement to drone action"""
        assert (x != 0 or y != 0)
        if x == 1:
            return "W"
        if x == -1:
            return "E"
        if y == 1:
            return "N"
        if y == -1:
            return "S"

    def add_state(self, state):
        new_state_number = self.get_state_number(state)
        epistemic_states = self.get_epistemic_states(state)
        self.add_to_epistemic_dictionary(epistemic_states, new_state_number)
        return new_state_number

    def get_state_number(self, state):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.states_dictionary:
            self.states_dictionary[state_str] = self.state_number
            new_state_number = self.state_number
            self.states.append(state)
            self.state_number += 1
        else:
            new_state_number = self.states_dictionary[state_str]

        return new_state_number

    def add_to_epistemic_dictionary(self, states, new_state_number):
        drone = -1
        for state in states:
            drone += 1
            state_str = ' '.join(str(state[e]) for e in state)
            if state_str not in self.epistemic_states_dictionary[drone]:
                self.epistemic_states_dictionary[drone][state_str] = {new_state_number}
            else:
                self.epistemic_states_dictionary[drone][state_str].add(new_state_number)

    def get_epistemic_state(self, state, drone):
        drone_place = state['place'][drone]
        epistemic_state = {'place': state['place'][:], 'energy': state['energy'][:],
                           'visited': state['visited'][:]}
        for coal_drone in range(0, self.no_drones):
            if coal_drone == drone:
                continue
            coal_drone_place = state['place'][coal_drone]
            if self.is_within_radius(drone_place, coal_drone_place):
                continue
            epistemic_state['place'][coal_drone] = -1
            epistemic_state['energy'][coal_drone] = -1
            epistemic_state['visited'][coal_drone] = []
        return epistemic_state

    def get_epistemic_states(self, state):
        epistemic_states = []
        for drone in range(0, self.no_drones):
            epistemic_states.append(self.get_epistemic_state(state, drone))
        return epistemic_states

    def is_within_radius(self, place1, place2):
        x1 = self.model_map[place1]['x']
        y1 = self.model_map[place1]['y']
        x2 = self.model_map[place2]['x']
        y2 = self.model_map[place2]['y']
        distance = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)
        return distance <= (self.comm_radius ** 2)

    def prepare_epistemic_relation(self):
        for drone in range(0, self.no_drones):
            for state, epistemic_class in self.epistemic_states_dictionary[drone].items():
                self.model.add_epistemic_class(drone, epistemic_class)

    def prop_for_state(self, state):
        p = []
        for place in state["place"]:
            p.append(self.value_for_prop(self.model_map[place]["d_PM2.5"], self.model_map[place]["PM2.5"]))

        return p

    @staticmethod
    def value_for_prop(v1, v2):
        if v1 == "t" and v2 == "t":
            return "t"
        if v1 == "t" and v2 == "f":
            return "Td"
        if v1 == "t" and v2 == "u":
            return "td"
        if v1 == "f" and v2 == "t":
            return "Tg"
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
        print("Properties:", state["prop"])
        print("Pollutions:", state["pollution"])

def generate_formula(no_drones, no_places):
    coal = ""
    for d in range(0, no_drones):
        coal += str(d)
        if d != no_drones -1:
            coal += ","
    txt = ""
    for l in range(0, no_places):
        for d in range(0, no_drones):
            txt += "(!(<<"+str(d)+">>F (p_"+str(d)+",e,"+str(l)+")) | <<"+coal+">> F (p_"+str(d)+",e,"+str(l)+"))"
            if d != no_drones - 1:
                txt += "|"
        txt += "&"
    for l in range(0, no_places):
        for d in range(0, no_drones):
            txt += "(<<"+str(d)+">>F p_"+str(d)+"@"+str(l)+")"
            if d != no_drones - 1:
                txt += "|"
        if l != no_places - 1:
            txt += "&"
    return txt

print(generate_formula(2,5))
pollution_model = PollutionModel(map, connections, 2, [3, 3], 1)
i = 0
# for state in pollution_model.states:
#     print(i)
#     print(state["place"])
#     print(state["energy"])
#     print(state["visited"])
#     print()
#     i += 1
#
# pollution_model.model.walk(0, PollutionModel.print_state)
print('Number of states:', len(pollution_model.states))

props = "pollution"
pollution_model.model.props = [props]
const = "t Td td Tg tg f fd fg u"
atlparser = mvatl_parser.AlternatingTimeTemporalLogicParser(const, props)
txt = "<<0>> F (pollution_0 <= Td)"

formula = atlparser.parse(txt)

print("Formula:", formula)
print(str(pollution_model.model.interpreter(formula, 0)))
