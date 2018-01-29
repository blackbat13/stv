from atl_model import ATLModel
import itertools

states = []

states.append({
    "name": "Aleje Trzech Wieszczów",
    "PM2.5": 232,
    "PM10": 170,
    "temperature": "u",
    "pressure": "u",
    "humidity": "u",
    "x": 0,
    "y": 0,
    "right": "Felicjanek",
    "up": "Studencka",
    "down": "",
    "left": "Leona Wyczółkowskiego"
})

states.append({
    "name": "Felicjanek",
    "PM2.5": "u",
    "PM10": "u",
    "temperature": "u",
    "pressure": "u",
    "humidity": "u",
    "x": 1,
    "y": 0,
    "right": "",
    "up": "",
    "down": "",
    "left": "Aleje Trzech Wieszczów"
})

states.append({
    "name": "Studencka",
    "PM2.5": 88,
    "PM10": 72,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 66,
    "x": 0,
    "y": 1,
    "right": "",
    "up": "aleja Juliusza Słowackiego",
    "down": "Aleje Trzech Wieszczów",
    "left": ""
})

states.append({
    "name": "aleja Juliusza Słowackiego",
    "PM2.5": 88,
    "PM10": 70,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 66,
    "x": 0,
    "y": 2,
    "right": "",
    "up": "Prądnicka",
    "down": "Studencka",
    "left": ""
})

states.append({
    "name": "Prądnicka",
    "PM2.5": 308,
    "PM10": 212,
    "temperature": "u",
    "pressure": 1009,
    "humidity": "u",
    "x": 0,
    "y": 3,
    "right": "",
    "up": "",
    "down": "aleja Juliusza Słowackiego",
    "left": ""
})

states.append({
    "name": "Leona Wyczółkowskiego",
    "PM2.5": 68,
    "PM10": 58,
    "temperature": 3,
    "pressure": 1007,
    "humidity": 55,
    "x": -1,
    "y": 0,
    "right": "Aleje Trzech Wieszczów",
    "up": "",
    "down": "",
    "left": "Vlastimila Hofmana"
})

states.append({
    "name": "Vlastimila Hofmana",
    "PM2.5": 36,
    "PM10": 28,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 59,
    "x": -2,
    "y": 0,
    "right": "Leona Wyczółkowskiego",
    "up": "Przybyszewskiego 56",
    "down": "aleja Jerzego Waszyngtona",
    "left": "aleja Kasztanowa"
})

states.append({
    "name": "aleja Jerzego Waszyngtona",
    "PM2.5": 36,
    "PM10": 30,
    "temperature": 4,
    "pressure": 1007,
    "humidity": 45,
    "x": -2,
    "y": -1,
    "right": "",
    "up": "Vlastimila Hofmana",
    "down": "",
    "left": ""
})

states.append({
    "name": "aleja Kasztanowa",
    "PM2.5": 40,
    "PM10": 32,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 59,
    "x": -4,
    "y": 0,
    "right": "Vlastimila Hofmana",
    "up": "Na Błonie",
    "down": "",
    "left": ""
})

states.append({
    "name": "Na Błonie",
    "PM2.5": 100,
    "PM10": 84,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 45,
    "x": -4,
    "y": 1,
    "right": "Wiedeńska",
    "up": "osiedle Złota Podkowa",
    "down": "aleja Kasztanowa",
    "left": ""
})

states.append({
    "name": "osiedle Złota Podkowa",
    "PM2.5": 80,
    "PM10": 68,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 69,
    "x": -4,
    "y": 2,
    "right": "",
    "up": "",
    "down": "Na Błonie",
    "left": ""
})

states.append({
    "name": "Wiedeńska",
    "PM2.5": 92,
    "PM10": 76,
    "temperature": 3,
    "pressure": 1008,
    "humidity": 45,
    "x": -3,
    "y": 2,
    "right": "Przybyszewskiego 56",
    "up": "",
    "down": "",
    "left": "Na Błonie"
})

states.append({
    "name": "Przybyszewskiego 56",
    "PM2.5": 56,
    "PM10": 50,
    "temperature": 4,
    "pressure": 1009,
    "humidity": 59,
    "x": -2,
    "y": 2,
    "right": "",
    "up": "",
    "down": "Vlastimila Hofmana",
    "left": "Wiedeńska"
})

sides = ["right", "up", "left", "down"]

for i in range(0, len(states)):
    for s in sides:
        if states[i][s] == "":
            states[i][s] = -1
            continue
        for j in range(0, len(states)):
            if states[i][s] == states[j]["name"]:
                states[i][s] = j
                break


# print(states)


class PollutionModel:
    model_map = []
    model = None
    states = []
    no_drones = 1
    sides = ["right", "up", "left", "down"]
    states_dictionary = {}
    epistemic_states_dictionary = {}
    state_number = 0

    def __init__(self, model_map, no_drones, energies):
        self.model_map = model_map
        self.no_drones = no_drones
        self.model = ATLModel(no_drones, 100000)
        places = []
        visited = []
        for i in range(0, no_drones):
            places.append(0)
            visited.append({0})

        self.add_state({
            "map": model_map,
            "place": places,
            "energy": energies,
            "visited": visited
        })

        self.generate_model()
        self.model.states = self.states
        self.prepare_epistemic_relation()

    def generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1

            available_actions = []

            for drone_number in range(0, self.no_drones):
                available_actions.append([])
                available_actions[drone_number].append(-1) # Wait
                if state["energy"][drone_number] == 0:
                    continue
                k = -1
                for side in self.sides:
                    k += 1
                    if self.model_map[state["place"][drone_number]][side] == -1:
                        continue
                    available_actions[drone_number].append(k) # self.sides[k]

            # print(available_actions)

            for drone_actions in itertools.product(*available_actions):
                places = state["place"][:]
                energies = state["energy"][:]
                visited = state["visited"][:]
                k = -1
                actions = {}
                # print(drone_actions)
                for d_action in drone_actions:
                    k += 1
                    if energies[k] > 0:
                        energies[k] -= 1
                    if d_action == -1:
                        actions[k] = "wait"
                        continue
                    # print(d_action)
                    # print(state["place"][k])
                    places[k] = self.model_map[state["place"][k]][self.sides[d_action]]
                    visited[k] = visited[k].copy()
                    visited[k].add(places[k])
                    actions[k] = self.sides[d_action]

                new_state = {
                    "map": self.model_map,
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
        epistemic_state = {'place': state['place'], 'energy': state['energy'],
                           'visited': state['visited']}
        return epistemic_state

    def prepare_epistemic_relation(self):
        for state, epistemic_class in self.epistemic_states_dictionary.items():
            self.model.add_epistemic_class(0, epistemic_class)

    @staticmethod
    def keep_values_in_list(the_list, val):
        return [value for value in the_list if value == val]


pollution_model = PollutionModel(states, 1, [2])
i = 0
for state in pollution_model.states:
    print(i)
    print(state["place"])
    print(state["energy"])
    print(state["visited"])
    print()
    i+=1
# pollution_model.model.walk(0)
print(len(pollution_model.states))
