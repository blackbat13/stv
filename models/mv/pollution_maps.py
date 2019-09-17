class PollutionMaps:
    @staticmethod
    def cracow(size: int):
        map = []

        connections = []

        map.append({
            "id": 0,
            "name": "Vlastimila Hofmana",
            "PM2.5": "t",
            "d_PM2.5": "t",
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
            "PM2.5": "t",
            "d_PM2.5": "t",
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
            "d_PM2.5": "u",
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
            "PM2.5": "t",
            "d_PM2.5": "t",
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

        return map, connections
