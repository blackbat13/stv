import yaml
from enum import Enum
from typing import Dict, List, Set

class MapFieldType(Enum):
    EMPTY = 0
    WALL = 1

class Machine:
    
    id: str
    x: int
    y: int
    requirements: Dict[str, int]
    maxItems: int
    
    def __init__(self, id: str, obj):
        self.id = id
        self.x = obj["x"]
        self.y = obj["y"]
        self.requirements = obj["requirements"]
        self.maxItems = obj["maxItems"]

class Robot:
    
    id: str
    x: int
    y: int
    
    def __init__(self, id: str, obj):
        self.id = id
        self.x = obj["x"]
        self.y = obj["y"]

class FactoryModelGenerator:
    
    mapWidth: int
    mapHeight: int
    mapNumFields: int
    map: List[List[MapFieldType]]
    machines: Dict[str, Machine]
    robots: Dict[str, Robot]
    persistentVarNames: Set[str] = set()
    
    def __init__(self, inputStr: str):
        self.__loadInput(inputStr)
    
    def __loadInput(self, inputStr: str):
        inputObj = yaml.safe_load(inputStr)
        self.__loadMap(inputObj["map"])
        self.__loadMachines(inputObj["machines"])
        self.__loadRobots(inputObj["robots"])
    
    def __loadMap(self, mapStr: str):
        self.map = list(map(lambda rowStr: list(map(self.__getMapFieldType, list(rowStr))), mapStr.strip().split(" ")))
        self.mapWidth = len(self.map[0])
        self.mapHeight = len(self.map)
        self.mapNumFields = self.mapWidth * self.mapHeight
    
    def __getMapFieldType(self, fieldChar: str) -> MapFieldType:
        if fieldChar == "O":
            return MapFieldType.EMPTY
        elif fieldChar == "X":
            return MapFieldType.WALL
        else:
          raise "Unknown map field type"  
    
    def __loadMachines(self, machines):
        self.machines = {}
        for machineId in machines:
            self.machines[machineId] = Machine(machineId, machines[machineId])
    
    def __loadRobots(self, robots):
        self.robots = {}
        for robotId in robots:
            self.robots[robotId] = Robot(robotId, robots[robotId])
    
    def __getFieldId(self, x: int, y: int) -> int:
        return (y - 1) * self.mapWidth + x
    
    def generate(self) -> str:
        result = ""
        result += self.__generateAgents()
        result += self.__generateReduction()
        result += self.__generatePersistent()
        result += self.__generateCoalition()
        result += self.__generateFormula()
        print(result)
    
    def __generateAgents(self) -> str:
        numRobots = len(self.robots)
        agentsStr = f"Agent R[{numRobots}]:\n"
        agentsStr += "init: r_init1\n"
        agentsStr += self.__generateRobotTransitions()
        agentsStr += "\n"
        return agentsStr
    
    def __generateRobotTransitions(self) -> str:
        transitionsStr = ""
        transitionsStr += self.__generateRobotInit()
        transitionsStr += self.__generateRobotMove()
        transitionsStr += self.__generateRobotItemDropOff()
        transitionsStr += self.__generateRobotItemPickUp()
        return transitionsStr
    
    def __generateRobotInit(self) -> str:
        transitionsStr = ""
        transitionsStr += f"init1: r_init1 -> r_init2 [{self.__getVarName_robotCarriedItemMachineNum('aID')} = 0]\n"
        for robotId in self.robots.keys():
            robot = self.robots[robotId]
            fieldId = self.__getFieldId(robot.x, robot.y)
            transitionsStr += f"init2: r_init2 -[{self.__getVarName_robotCarriedItemMachineNum(robotId)} == 0]> r_empty [{self.__getVarName_robotFieldId('aID')} = {fieldId}, {self.__getVarName_mapFieldLocked(fieldId)} = 1]\n"
        return transitionsStr
    
    def __generateRobotMove(self) -> str:
        transitionsStr = ""
        for state in ["r_empty", "r_carrying"]:
            for x in range(1, self.mapWidth + 1):
                for y in range(1, self.mapHeight + 1):
                    if self.map[y - 1][x - 1] == MapFieldType.WALL:
                        continue
                    fieldId = self.__getFieldId(x, y)
                    targetFieldIds = []
                    if x > 1 and self.map[y - 1][x - 1 - 1] == MapFieldType.EMPTY:
                        targetFieldIds.append(self.__getFieldId(x - 1, y))
                    if x < self.mapWidth and self.map[y - 1][x - 1 + 1] == MapFieldType.EMPTY:
                        targetFieldIds.append(self.__getFieldId(x + 1, y))
                    if y > 1 and self.map[y - 1 - 1][x - 1] == MapFieldType.EMPTY:
                        targetFieldIds.append(self.__getFieldId(x, y - 1))
                    if y < self.mapHeight and self.map[y - 1 + 1][x - 1] == MapFieldType.EMPTY:
                        targetFieldIds.append(self.__getFieldId(x, y + 1))
                    for targetFieldId in targetFieldIds:
                        transitionsStr += f"move1_{state}_{fieldId}_{targetFieldId}: {state} -[{self.__getVarName_robotFieldId('aID')} == {fieldId}]> {state}_movingTo_{targetFieldId}\n"
                        transitionsStr += f"move2_{state}_{fieldId}_{targetFieldId}: {state}_movingTo_{targetFieldId} -[{self.__getVarName_mapFieldLocked(targetFieldId)} != 1]> {state} [{self.__getVarName_mapFieldLocked(targetFieldId)} = 1, {self.__getVarName_mapFieldLocked(fieldId)} = 0, {self.__getVarName_robotFieldId('aID')} = {targetFieldId}]\n"
                        transitionsStr += f"move_cancel_{state}_{fieldId}_{targetFieldId}: {state}_movingTo_{targetFieldId} -> {state}\n"
        return transitionsStr
    
    def __generateRobotItemDropOff(self) -> str:
        transitionsStr = ""
        for machineId in self.machines.keys():
            machine = self.machines[machineId]
            if len(machine.requirements) == 0:
                continue
            fieldId = self.__getFieldId(machine.x, machine.y)
            transitionsStr += f"dropoff1_{machineId}: r_carrying -[{self.__getVarName_robotFieldId('aID')} == {fieldId}]> r_tryDropoff_{machineId}\n"
            transitionsStr += f"dropoff1_{machineId}_cancel: r_tryDropoff_{machineId} -> r_carrying\n"
            transitionsStr += f"dropoff2_{machineId}: r_tryDropoff_{machineId} -[{self.__getVarName_robotCarriedItemMachineNum('aID')} == {machineId[1:]}]> r_dropoff_{machineId}\n"
            transitionsStr += f"dropoff2_{machineId}_cancel: r_dropoff_{machineId} -> r_carrying\n"
            for itemMachineId in machine.requirements.keys():
                itemRequiredNum = machine.requirements[itemMachineId]
                for numStoredItems in range(0, itemRequiredNum):
                    transitionsStr += f"dropoff_{machineId}_{itemMachineId}_{numStoredItems}: r_dropoff_{machineId} -[{self.__getVarName_numItemsStoredByMachine(machineId, itemMachineId)} == {numStoredItems}]> r_empty [{self.__getVarName_numItemsStoredByMachine(machineId, itemMachineId)} == {numStoredItems + 1}, {self.__getVarName_robotCarriedItemMachineNum('aID')} = 0]\n"
        return transitionsStr
    
    def __generateRobotItemPickUp(self) -> str:
        transitionsStr = ""
        for machineId in self.machines.keys():
            machine = self.machines[machineId]
            fieldId = self.__getFieldId(machine.x, machine.y)
            transitionsStr += f"pickup_{machineId}: r_empty -[{self.__getVarName_robotFieldId('aID')} == {fieldId}]> r_pickup_{machineId}_step_0\n"
            for numProducedItems in range(0, machine.maxItems):
                conds = self.__getPickUpConditionsForMachine(machine, numProducedItems)
                for i in range(0, len(conds)):
                    cond = conds[i]
                    if i + 1 < len(conds):
                        transitionsStr += f"pickup_{machineId}_{numProducedItems}_step_{i}: r_pickup_{machineId}_step_{i} -[{cond}]> r_pickup_{machineId}_step_{i + 1}\n"
                    else:
                        transitionsStr += f"pickup_{machineId}_{numProducedItems}_step_{i}: r_pickup_{machineId}_step_{i} -[{cond}]> r_carrying [{self.__generatePostPickUpVarsForMachine(machine, numProducedItems)}, {self.__getVarName_robotCarriedItemMachineNum('aID')} = {machineId[1:]}]\n"
                    transitionsStr += f"pickup_{machineId}_{numProducedItems}_step_{i}_cancel: r_pickup_{machineId}_step_{i} -> r_empty\n"
        return transitionsStr
    
    def __getPickUpConditionsForMachine(self, machine: Machine, numProducedItems: int) -> List[str]:
        conds = []
        for itemMachineId in machine.requirements.keys():
            itemRequiredCount = machine.requirements[itemMachineId]
            conds.append(f"{self.__getVarName_numItemsStoredByMachine(machine.id, itemMachineId)} == {itemRequiredCount}")
        conds.append(f"{self.__getVarName_numProducedItemsByMachine(machine.id)} == {numProducedItems}")
        return conds
    
    def __generatePostPickUpVarsForMachine(self, machine: Machine, numProducedItems: int) -> str:
        vars = []
        for itemMachineId in machine.requirements.keys():
            vars.append(f"{self.__getVarName_numItemsStoredByMachine(machine.id, itemMachineId)} = 0")
        vars.append(f"{self.__getVarName_numProducedItemsByMachine(machine.id)} = {numProducedItems + 1}")
        return ", ".join(vars)
    
    def __generateReduction(self) -> str:
        reductionStr = "REDUCTION: []\n"
        return reductionStr
    
    def __generatePersistent(self) -> str:
        persistentStr = "PERSISTENT: ["
        for machineId in self.machines.keys():
            machine = self.machines[machineId]
            for requiredItemMachineId in machine.requirements.keys():
                self.persistentVarNames.add(self.__getVarName_numItemsStoredByMachine(machineId, requiredItemMachineId))
            self.persistentVarNames.add(self.__getVarName_numProducedItemsByMachine(machineId))
        for robotId in self.robots.keys():
            self.persistentVarNames.add(self.__getVarName_robotCarriedItemMachineNum(robotId))
            self.persistentVarNames.add(self.__getVarName_robotFieldId(robotId))
        for fieldId in range(1, self.mapNumFields + 1):
            self.persistentVarNames.add(self.__getVarName_mapFieldLocked(fieldId))
        persistentStr += ",".join(self.persistentVarNames)
        persistentStr += "]\n"
        return persistentStr
    
    def __generateCoalition(self) -> str:
        coalitionStr = "COALITION: []\n"
        return coalitionStr
    
    def __generateFormula(self) -> str:
        formulaAgentsStr = ",".join(self.robots.keys())
        lastMachineId = list(self.machines.keys())[-1]
        formulaConditionVarName = self.__getVarName_numProducedItemsByMachine(lastMachineId)
        formulaConditionStr = f"{formulaConditionVarName} = 1"
        formulaStr = f"FORMULA: <<{formulaAgentsStr}>>({formulaConditionStr})\n"
        return formulaStr
    
    def __getVarName_numItemsStoredByMachine(self, machineId: str, itemMachineId: str) -> str:
        return f"{machineId}_numStoredItems_{itemMachineId}"
    
    def __getVarName_numProducedItemsByMachine(self, machineId: str) -> str:
        return f"{machineId}_numProducedItems"
    
    def __getVarName_robotCarriedItemMachineNum(self, robotId: str) -> str:
        return f"{robotId}_carriedItemMachineNum"
    
    def __getVarName_robotFieldId(self, robotId: str) -> str:
        return f"{robotId}_fieldId"
    
    def __getVarName_mapFieldLocked(self, fieldId: int) -> str:
        return f"mapField_{fieldId}_locked"

if __name__ == "__main__":
    stream = open("inputs/factory1.yaml", "r")
    generator = FactoryModelGenerator(stream.read())
    generator.generate()
