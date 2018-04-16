from comparing_strats.simple_model import SimpleModel
import itertools
from disjoint_set import DisjointSet
from random import randint


class CracowMap:
    places = []
    connections = []
    disjoint_set = None

    def __init__(self):
        self.create_places()
        self.create_connections()
        self.create_epistemic()

    def create_places(self):
        """Populate places array"""
        self.places.append({
            "id": 0,
            "name": "Vlastimila Hofmana",
            "PM2.5": False,
            "x": 0,
            "y": 0
        })

        self.places.append({
            "id": 1,
            "name": "Leona Wyczółkowskiego",
            "PM2.5": False,
            "x": 1,
            "y": 0
        })

        self.places.append({
            "id": 2,
            "name": "Aleje Trzech Wieszczów",
            "PM2.5": True,
            "x": 2,
            "y": 0
        })

        self.places.append({
            "id": 3,
            "name": "Wiedeńska",
            "PM2.5": False,
            "x": 0,
            "y": 1
        })

        self.places.append({
            "id": 4,
            "name": "Przybyszewskiego 56",
            "PM2.5": False,
            "x": 1,
            "y": 1
        })

        self.places.append({
            "id": 5,
            "name": "Studencka",
            "PM2.5": False,
            "x": 2,
            "y": 1
        })

        self.places.append({
            "id": 6,
            "name": "Na Błonie",
            "PM2.5": True,
            "x": 0,
            "y": 2
        })

        self.places.append({
            "id": 7,
            "name": "osiedle Złota Podkowa",
            "PM2.5": False,
            "x": 1,
            "y": 2
        })

        self.places.append({
            "id": 8,
            "name": "aleja Juliusza Słowackiego",
            "PM2.5": False,
            "x": 2,
            "y": 2
        })

        self.places.append({
            "id": 9,
            "name": "aleja Kasztanowa",
            "PM2.5": False,
            "x": 0,
            "y": 3
        })

        self.places.append({
            "id": 10,
            "name": "aleja Jerzego Waszyngtona",
            "PM2.5": False,
            "x": 1,
            "y": 3
        })

        self.places.append({
            "id": 11,
            "name": "Prądnicka",
            "PM2.5": True,
            "x": 2,
            "y": 3
        })

    def create_connections(self):
        """Populate connections array"""
        self.connections.append([0, 1])
        self.connections.append([1, 2])
        self.connections.append([3, 4])
        self.connections.append([1, 4])
        self.connections.append([2, 5])
        self.connections.append([4, 5])
        self.connections.append([6, 7])
        self.connections.append([5, 8])
        self.connections.append([6, 9])
        self.connections.append([9, 10])
        self.connections.append([7, 10])
        self.connections.append([8, 11])

        self.connections.append([4, 7])
        # self.connections.append([7, 8])
        self.connections.append([0, 3])
        # self.connections.append([0, 5])
        self.connections.append([0, 7])

    def create_epistemic(self):
        self.disjoint_set = DisjointSet(len(self.places))
        #self.disjoint_set.union(0, 1)
        #self.disjoint_set.union(1, 3)
        self.disjoint_set.union(3, 2)
        self.disjoint_set.union(4, 8)
        self.disjoint_set.union(7, 9)
        self.disjoint_set.union(11, 10)
        self.disjoint_set.union(10, 5)


class DroneModel:
    no_drones = 0
    energies = []
    map = []
    model = None
    graph = []
    states = []
    states_dictionary = {}
    epistemic_states_dictionary = {}
    state_number = 0
    drone_actions = ['N', 'W', 'S', 'E', 'F']
    is_random = False

    def __init__(self, no_drones, energies, map, is_random: bool = False):
        self.clear_all()
        self.no_drones = no_drones
        self.energies = energies
        self.map = map
        self.model = SimpleModel(no_drones)
        self.create_map_graph()
        self.is_random = is_random
        places = []
        visited = []
        for i in range(0, no_drones):
            places.append(0)
            visited.append({0})

        first_state = {
            "place": places,
            "energy": energies,
            "visited": visited
        }

        self.add_state(first_state)
        self.generate_model()
        self.prepare_epistemic_relation()
        self.model.states = self.states

    def clear_all(self):
        self.no_drones = 0
        self.energies = []
        self.map = []
        self.model = None
        self.graph = []
        self.states = []
        self.states_dictionary = {}
        self.epistemic_states_dictionary = {}
        self.state_number = 0
        self.drone_actions = ['N', 'W', 'S', 'E', 'F']
        self.is_random = False

    def create_map_graph(self):
        """Creates graph from connections between places in the map"""
        self.graph = []
        for _ in range(0, len(self.map.places)):
            self.graph.append([])

        for con in self.map.connections:
            self.graph[con[0]].append(con[1])
            self.graph[con[1]].append(con[0])

    def generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1

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
                    action_id = self.movement_to_action(x, y)
                    available_actions[drone_number].append([x, y, place_id, self.drone_actions[action_id]])
                    if self.is_random:
                        rnd = randint(0, 100)
                        if rnd > 50:  # probability
                            continue
                        how_much = randint(1, 3)
                        # how_much = min(how_much, 3)
                        act = self.drone_actions[:]
                        act.remove(self.drone_actions[action_id])
                        for _ in range(0, how_much):
                            action = act[randint(0, len(act) - 1)]
                            act.remove(action)
                            available_actions[drone_number].append([x, y, place_id, action])

                actions_order = [4]  # Should be without one action - the good one
                i = -1
                # Add several bad actions
                if not self.is_random:
                    for action in actions_order:
                        i += 1
                        how_much = len(self.graph[current_place]) - 1
                        # how_much = int(len(self.graph[current_place]) / (i+1))
                        # if i >= 2:
                        #     how_much = int(len(self.graph[current_place]) / (2))
                        for j in range(0, how_much):
                            place_id = self.graph[current_place][j]
                            x, y = self.relation_between_places(current_place, place_id)
                            action_id = self.movement_to_action(x, y)
                            if action_id == action:
                                continue
                            available_actions[drone_number].append([x, y, place_id, self.drone_actions[action]])

            for drone_actions in itertools.product(*available_actions):
                places = state["place"][:]
                energies = state["energy"][:]
                visited = state["visited"][:]
                actions = []
                for _ in range(0, self.no_drones):
                    actions.append(None)
                drone_number = -1
                for d_action in drone_actions:
                    drone_number += 1
                    if energies[drone_number] > 0:
                        energies[drone_number] -= 1
                    if d_action == -1:
                        actions[drone_number] = "Wait"
                        continue
                    next_place = d_action[2]
                    # if next_place in visited[drone_number]:
                    #     # Don't visit same place twice
                    #     actions[drone_number] = "Wait"
                    #     continue
                    places[drone_number] = next_place
                    visited[drone_number] = visited[drone_number].copy()
                    visited[drone_number].add(next_place)
                    actions[drone_number] = d_action[3]

                new_state = {
                    "place": places,
                    "energy": energies,
                    "visited": visited
                }

                new_state_number = self.add_state(new_state)
                self.model.add_transition(current_state_number, new_state_number, actions)

    def add_state(self, state):
        new_state_number = self.get_state_number(state)
        epistemic_state = self.get_epistemic_state(state)
        self.add_to_epistemic_dictionary(epistemic_state, new_state_number)
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

    def add_to_epistemic_dictionary(self, state, new_state_number):
        state_str = ' '.join(str(state[e]) for e in state)
        if state_str not in self.epistemic_states_dictionary:
            self.epistemic_states_dictionary[state_str] = {new_state_number}
        else:
            self.epistemic_states_dictionary[state_str].add(new_state_number)

    def get_epistemic_state(self, state):
        new_places = state['place'][:]
        for i in range(0, len(new_places)):
            new_places[i] = self.map.disjoint_set.find(new_places[i])
        new_visited = []
        for i in range(0, len(state['visited'])):
            new_visited.append(set())
            for place in state['visited'][i]:
                new_visited[i].add(self.map.disjoint_set.find(place))
        epistemic_state = {'place': new_places, 'energy': state['energy'],
                           'visited': new_visited}
        return epistemic_state

    def prepare_epistemic_relation(self):
        for state, epistemic_class in self.epistemic_states_dictionary.items():
            self.model.add_epistemic_class(0, epistemic_class)

    def relation_between_places(self, place_id_1, place_id_2):
        """Computes relation between two places on the map as the (+x,+y)"""
        assert (place_id_1 != place_id_2)
        x = self.map.places[place_id_2]["x"] - self.map.places[place_id_1]["x"]
        y = self.map.places[place_id_2]["y"] - self.map.places[place_id_1]["y"]
        return x, y

    def movement_to_action(self, x, y):
        """Transform movement to drone action"""
        assert (x != 0 or y != 0)
        if x == 1:
            return 1
        if x == -1:
            return 3
        if y == 1:
            return 0
        if y == -1:
            return 2