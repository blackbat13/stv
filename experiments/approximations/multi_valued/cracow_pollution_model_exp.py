from models.mv.cracow_pollution_model import PollutionModel
import datetime
from tools.array_tools import ArrayTools
import time
from logics.atl.mv import mvatl_parser


class CracowPollutionModelExp:
    def __init__(self, n_agent: int, energy: int, radius: int, selected_place: int, first_place_id: int):
        self.n_agent = n_agent
        self.energy = energy
        self.radius = radius
        self.selected_place = selected_place
        self.first_place_id = first_place_id
        self.energies = ArrayTools.create_value_array_of_size(n_agent, energy)
        self.map, self.connections = self.create_map()

    def create_map(self):
        map = []
        connections = []

        map.append({
            "id": 0,
            "name": "Vlastimila Hofmana",
            "PM2.5": "t",
            "d_PM2.5": "t",
            "x": 0,
            "y": 0
        })

        map.append({
            "id": 1,
            "name": "Leona Wyczółkowskiego",
            "PM2.5": "t",
            "d_PM2.5": "t",
            "x": 0,
            "y": 1
        })

        map.append({
            "id": 2,
            "name": "Aleje Trzech Wieszczów",
            "PM2.5": "t",
            "d_PM2.5": "f",
            "x": 1,
            "y": 0
        })

        map.append({
            "id": 3,
            "name": "Wiedeńska",
            "PM2.5": "f",
            "d_PM2.5": "t",
            "x": 1,
            "y": 1
        })

        map.append({
            "id": 4,
            "name": "Przybyszewskiego 56",
            "PM2.5": "u",
            "d_PM2.5": "f",
            "x": 1,
            "y": 2
        })

        map.append({
            "id": 5,
            "name": "Studencka",
            "PM2.5": "u",
            "d_PM2.5": "u",
            "x": 2,
            "y": 0
        })

        map.append({
            "id": 6,
            "name": "Na Błonie",
            "PM2.5": "t",
            "d_PM2.5": "f",
            "x": 3,
            "y": 1
        })

        map.append({
            "id": 7,
            "name": "osiedle Złota Podkowa",
            "PM2.5": "t",
            "d_PM2.5": "f",
            "x": 3,
            "y": 2
        })

        map.append({
            "id": 8,
            "name": "aleja Juliusza Słowackiego",
            "PM2.5": "f",
            "d_PM2.5": "f",
            "x": 2,
            "y": 1
        })

        connections.append([0, 1])
        connections.append([1, 4])
        connections.append([2, 5])
        connections.append([2, 5])
        connections.append([3, 4])
        connections.append([3, 8])
        connections.append([5, 6])
        connections.append([5, 8])
        connections.append([6, 7])

        return map, connections

    def run_experiments(self):
        print(datetime.datetime.now())

        file = open("results-f2-perf.txt", "a")
        file.write(f"Drones: {self.n_agent}\n")
        file.write(f"Energies: {self.energies}\n")
        file.write(f"Map: {self.map}\n")
        file.write(f"Connections: {self.connections}\n")
        file.write(f'Map size: {len(self.map)}\n')
        file.write(f'Radius: {self.radius}\n')
        file.write(f'Selected place: {self.selected_place}\n')
        file.write(f'First place id: {self.first_place_id}\n')

        start = time.perf_counter()
        pollution_model = PollutionModel(self.map, self.connections, self.n_agent, self.energies, self.radius, self.first_place_id)
        stop = time.perf_counter()
        tgen = stop - start

        # pollution_model.print_states()

        file.write(f'Tgen: {tgen}\n')
        file.write(f'Number of states: {len(pollution_model.states)}\n')

        phi1_l = "<<>> F polnew_0"
        phi1_r = "<<0>> F polnew_0"
        phi2 = self.generate_new_formula2(self.n_agent, self.selected_place)

        formula_txt = phi2

        file.write(f"Formula: {formula_txt}\n")

        print(formula_txt)
        props = list()
        for l in range(0, len(self.map)):
            for a in range(0, self.n_agent):
                props.append("pol" + str(l))
                props.append("polE" + str(l))
                props.append("loc" + str(l))
                props.append("polD" + str(l))
        props.append('locA')
        props.append('polnew')
        pollution_model.model.props = props
        const = "t td tg f fd fg u"
        atlparser = mvatl_parser.AlternatingTimeTemporalLogicParser(const, props)
        formula = atlparser.parse(formula_txt)
        print("Formula:", formula)
        start = time.perf_counter()
        result = pollution_model.model.interpreter(formula, 0)
        stop = time.perf_counter()
        tverif = stop - start
        print(str(result))

        file.write(f"Result: {result}\n")
        file.write(f'Tverif: {tverif}\n')
        file.write("\n")

        file.close()

    # Syntax for propositions:
    # Polution prop -> poll the list of size no_drones with (the second) l as the location number
    # In formula -> poll_d with l location and d drone (ex: pol3 = [t,f,t] and pol3_1 = f)
    # Location prop -> locl the list of size no_drones with (the second) l as the location number
    # In formula -> locl_d with l location and d drone (ex: loc3 = [t,f,t] and loc3_1 = f)
    def generate_new_formula2(self, no_drones, location_id):
        coal = ""
        for d in range(0, no_drones):
            coal += str(d)
            if d != no_drones - 1:
                coal += ","

        result = f"<<{coal}>> F "
        lst = list()
        for d in range(0, no_drones):
            lst2 = list()
            lst2.append(f"(loc{location_id}_{d} & polnew_{d})")
            lst.append(lst2)

        result += self.cformula2string(lst, 0)
        return result

    def dformula2string(self, disj, i):
        if i == len(disj) - 1:
            return disj[i]
        return "(" + disj[i] + " | " + self.dformula2string(disj, i + 1) + ")"

    def cformula2string(self, conj, i):
        if i == len(conj) - 1:
            return self.dformula2string(conj[i], 0)
        return "(" + self.dformula2string(conj[i], 0) + " | " + self.cformula2string(conj, i + 1) + ")"


# cracow_pollution_model_exp = CracowPollutionModelExp(3, 4, 1, 7, 5)
# cracow_pollution_model_exp.run_experiments()