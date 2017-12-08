from atl_model import ATLModel

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

    def __init__(self, model_map, no_drones, energy):
        self.model_map = model_map
        self.no_drones = no_drones
        self.model = ATLModel(no_drones, 1000)
        self.states.append({
            "place": 0,
            "name": model_map[0]["name"],
            "PM2.5": model_map[0]["PM2.5"],
            "PM10": model_map[0]["PM10"],
            "temperature": model_map[0]["temperature"],
            "pressure": model_map[0]["pressure"],
            "humidity": model_map[0]["humidity"],
            "x": model_map[0]["x"],
            "y": model_map[0]["y"],
            "right": model_map[0]["right"],
            "up": model_map[0]["up"],
            "down": model_map[0]["down"],
            "left": model_map[0]["left"],
            "energy": energy
        })
        self.generate_model()
        self.model.states = self.states
        self.prepare_epistemic_relation()

    def generate_model(self):
        current_state_number = -1
        for state in self.states:
            current_state_number += 1
            if state["energy"] == 0:
                continue
            for side in self.sides:
                if state[side] == -1:
                    continue

                new_state = {
                    "place": state[side],
                    "name": self.model_map[state[side]]["name"],
                    "PM2.5": self.model_map[state[side]]["PM2.5"],
                    "PM10": self.model_map[state[side]]["PM10"],
                    "temperature": self.model_map[state[side]]["temperature"],
                    "pressure": self.model_map[state[side]]["pressure"],
                    "humidity": self.model_map[state[side]]["humidity"],
                    "x": self.model_map[state[side]]["x"],
                    "y": self.model_map[state[side]]["y"],
                    "right": self.model_map[state[side]]["right"],
                    "up": self.model_map[state[side]]["up"],
                    "down": self.model_map[state[side]]["down"],
                    "left": self.model_map[state[side]]["left"],
                    "energy": state["energy"] - 1}
                actions = {0: "fly " + side}
                new_state_number = self.add_state(new_state)
                self.model.add_transition(current_state_number, new_state_number, actions)

    def add_state(self, state):
        self.states.append(state)
        return len(self.states) - 1

    def prepare_epistemic_relation(self):
        for state_number in range(0, len(self.states)):
            self.model.add_epistemic_class(0, {state_number})


pollution_model = PollutionModel(states, 1, 4)
pollution_model.model.walk(0)
print(len(pollution_model.states))
