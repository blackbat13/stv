import itertools
from typing import List
from generators.ispl.ispl_generator import IsplGenerator


class CastlesIsplGenerator(IsplGenerator):

    def __init__(self, workers: List[int], no_castles: int = 3, castles_life=None):
        super().__init__()
        if castles_life is None:
            castles_life = [3, 3, 3]
        self.__workers = workers
        self.__no_workers = sum(self.__workers)
        self.__no_castles = no_castles
        self.__castles_life = castles_life

    def __define_semantics(self) -> str:
        semantics = "Semantics=SingleAssignment;\n\n"
        return semantics

    def __create_environment_obsvars(self) -> str:
        obsvars = "\tObsvars:\n"

        for castle_id in range(1, self.__no_castles + 1):
            obsvars += f"\t\tcastle{castle_id}Defeated: boolean;\n"

        obsvars += "\tend Obsvars\n"
        return obsvars

    def __create_environment_vars(self) -> str:
        vars = "\tVars:\n"

        for castle_id in range(1, self.__no_castles + 1):
            vars += f"\t\tcastle{castle_id}HP: 0..{self.__castles_life[castle_id - 1]};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_environment_actions(self) -> str:
        actions = "\tActions = {none};\n"
        return actions

    def __create_environment_protocol(self) -> str:
        protocol = "\tProtocol:\n\t\tOther: {none};\n\tend Protocol\n"
        return protocol

    def __create_environment_evolution(self) -> str:
        evolution = "\tEvolution:\n"

        actions = self.__compute_workers_actions()

        for round in itertools.product(*actions):
            castle_lifes = [0, 0, 0]
            defenders = [0, 0, 0]
            attacked = [0, 0, 0]

            worker_id = -1
            for castle_id in range(1, self.__no_castles + 1):
                for _ in range(0, self.__workers[castle_id - 1]):
                    worker_id += 1
                    action = round[worker_id]
                    if action == "defend":
                        defenders[castle_id - 1] += 1
                    elif action != "wait":
                        for attacked_id in range(1, self.__no_castles + 1):
                            if action == f'attack{attacked_id}':
                                attacked[attacked_id - 1] += 1
                                break

            for castle_id in range(0, self.__no_castles):
                if attacked[castle_id] > defenders[castle_id]:
                    castle_lifes[castle_id] -= (attacked[castle_id] - defenders[castle_id])

            for castle_id in range(1, self.__no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                evolution += f"\t\tcastle{castle_id}Defeated=true if\n"
                for worker_id in range(0, self.__no_workers):
                    evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                life_req = castle_lifes[castle_id - 1] * (-1)
                if life_req > 3:
                    life_req = 3
                evolution += f"\t\t\tcastle{castle_id}HP <= {life_req};\n"

            for castle_id in range(1, self.__no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                for life in range(1, self.__castles_life[castle_id - 1] + 1):
                    new_life = life + castle_lifes[castle_id - 1]
                    if new_life < 0:
                        new_life = 0

                    evolution += f"\t\tcastle{castle_id}HP={new_life} if\n"
                    for worker_id in range(0, self.__no_workers):
                        evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                    evolution += f"\t\t\tcastle{castle_id}HP = {life};\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __compute_workers_actions(self) -> List[List[str]]:
        actions = []
        worker_id = -1
        for castle_id in range(1, self.__no_castles + 1):
            for _ in range(0, self.__workers[castle_id - 1]):
                worker_id += 1
                actions.append(['wait', 'defend'])
                for attacked_id in range(1, self.__no_castles + 1):
                    if attacked_id == castle_id:
                        continue
                    actions[-1].append(f'attack{attacked_id}')

        return actions

    def __create_agents(self) -> str:
        agents = ""
        for worker_id in range(0, self.__no_workers):
            agents += self.__create_worker(worker_id)

        return agents

    def __create_worker(self, worker_id: int) -> str:
        agent = f"Agent Worker{worker_id + 1}\n"
        # agent += self.__create_worker_lobsvars(worker_id)
        agent += self.__create_worker_vars()
        agent += self.__create_worker_actions(worker_id)
        agent += self.__create_worker_protocol(worker_id)
        agent += self.__create_worker_evolution()
        agent += "end Agent\n\n"
        return agent

    def __create_worker_lobsvars(self, worker_id: int) -> str:
        lobsvars = "\tLobsvars = {"

        worker_castle_id = self.get_castle_id(worker_id) + 1
        lobsvars += f"castle{worker_castle_id}HP"

        lobsvars += "};\n"
        return lobsvars

    def __create_worker_vars(self) -> str:
        vars = "\tVars:\n"
        vars += "\t\tcanDefend: boolean;\n"
        vars += "\tend Vars\n"
        return vars

    def __create_worker_actions(self, worker_id: int) -> str:
        actions = "\tActions = {"
        worker_castle_id = self.get_castle_id(worker_id)
        for castle_id in range(0, self.__no_castles):
            if worker_castle_id == castle_id:
                continue
            actions += f"attack{castle_id + 1}, "
        actions += "defend, "
        actions += "wait};\n"
        return actions

    def __create_worker_protocol(self, worker_id: int) -> str:
        protocol = "\tProtocol:\n"
        worker_castle_id = self.get_castle_id(worker_id)
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=true: " + "{wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=true: " + "{defend, "
        for castle_id in range(0, self.__no_castles):
            if worker_castle_id == castle_id:
                continue
            protocol += f"attack{castle_id + 1}, "
        protocol += "wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=false: " + "{"
        for castle_id in range(0, self.__no_castles):
            if worker_castle_id == castle_id:
                continue
            protocol += f"attack{castle_id + 1}, "
        protocol += "wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_worker_evolution(self) -> str:
        evolution = "\tEvolution:\n"
        evolution += "\t\tcanDefend=false if Action=defend;\n"
        evolution += "\t\tcanDefend=true if canDefend=false;\n"
        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self) -> str:
        evaluation = "Evaluation\n"
        evaluation += "\tcastle3Defeated if Environment.castle3Defeated = true;\n"
        evaluation += "end Evaluation\n\n"
        return evaluation

    def __create_init_states(self) -> str:
        init_states = "InitStates\n"
        for castle_id in range(0, self.__no_castles):
            init_states += f"\tEnvironment.castle{castle_id + 1}HP={self.__castles_life[castle_id]} and\n"
            init_states += f"\tEnvironment.castle{castle_id + 1}Defeated=false and\n"

        for worker_id in range(0, self.__no_workers):
            init_states += f"\tWorker{worker_id + 1}.canDefend=true and\n"
        init_states = init_states.rstrip("\ndna ")
        init_states += ";\nend InitStates\n\n"
        return init_states

    def __create_groups(self) -> str:
        groups = "Groups\n"
        groups += "\tc12 = {"
        for worker_id in range(0, self.__workers[0] + self.__workers[1]):
            groups += f"Worker{worker_id + 1}, "

        groups = groups.rstrip(" ,")
        groups += "};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self) -> str:
        formulae = "Formulae\n"
        formulae += "\t<c12>F(castle3Defeated);\n"
        formulae += "end Formulae\n\n"
        return formulae

    def get_castle_id(self, worker_id: int) -> int:
        castle_id = 0
        workers_sum = 0
        for i in self.__workers:
            workers_sum += i
            if worker_id >= workers_sum:
                castle_id += 1
            else:
                break

        return castle_id


class CastlesIsplGeneratorSubjective(IsplGenerator):
    workers = []
    no_castles = 3
    castles_life = [3, 3, 3]
    no_workers = 0

    def __init__(self, workers: List[int]):
        super().__init__()
        self.workers = workers
        self.no_workers = sum(self.workers)
        return

    def __create_agents(self) -> str:
        agents = ""
        for worker_id in range(0, self.no_workers):
            agents += self.__create_worker(worker_id)
        for castle_id in range(0, self.no_castles):
            agents += self.__create_decider(castle_id)

        return agents

    def __define_semantics(self) -> str:
        semantics = "Semantics=SingleAssignment;\n\n"
        return semantics

    def __create_environment_obsvars(self) -> str:
        obsvars = "\tObsvars:\n"

        for castle_id in range(1, self.no_castles + 1):
            obsvars += f"\t\tcastle{castle_id}Defeated: boolean;\n"

        obsvars += "\t\tdecide: boolean;\n"
        obsvars += "\tend Obsvars\n"
        return obsvars

    def __create_environment_vars(self) -> str:
        vars = "\tVars:\n"

        for castle_id in range(1, self.no_castles + 1):
            vars += f"\t\tcastle{castle_id}HP: 0..{self.castles_life[castle_id - 1]};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_environment_actions(self) -> str:
        actions = "\tActions = {"
        actions += "wait};\n"
        return actions

    def __create_environment_protocol(self) -> str:
        protocol = "\tProtocol:\n"
        protocol += "\t\tOther: {wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_environment_evolution(self) -> str:
        evolution = "\tEvolution:\n"

        evolution += "\t\tdecide=false if decide=true;\n"

        for castle_id in range(0, self.no_castles):
            for life in range(1, self.castles_life[castle_id] + 1):
                evolution += f"\t\tcastle{castle_id + 1}HP={life} if Decider{castle_id + 1}.Action=decideHP{life};\n"

            # evolution += f"\t\tcastle{castle_id+1}Defeated=true if Decider{castle_id+1}.Action=decideHP0;\n"

        actions = []

        worker_id = -1
        for castle_id in range(1, self.no_castles + 1):
            for _ in range(0, self.workers[castle_id - 1]):
                worker_id += 1
                actions.append(['wait', 'defend'])
                for attacked_id in range(1, self.no_castles + 1):
                    if attacked_id == castle_id:
                        continue
                    actions[-1].append(f'attack{attacked_id}')

        for round in itertools.product(*actions):
            castle_lifes = [0, 0, 0]
            defenders = [0, 0, 0]
            attacked = [0, 0, 0]

            worker_id = -1
            for castle_id in range(1, self.no_castles + 1):
                for _ in range(0, self.workers[castle_id - 1]):
                    worker_id += 1
                    action = round[worker_id]
                    if action == "defend":
                        defenders[castle_id - 1] += 1
                    elif action != "wait":
                        for attacked_id in range(1, self.no_castles + 1):
                            if action == f'attack{attacked_id}':
                                attacked[attacked_id - 1] += 1
                                break

            for castle_id in range(0, self.no_castles):
                if attacked[castle_id] > defenders[castle_id]:
                    castle_lifes[castle_id] -= (attacked[castle_id] - defenders[castle_id])

            for castle_id in range(1, self.no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                evolution += f"\t\tcastle{castle_id}Defeated=true if\n"
                for worker_id in range(0, self.no_workers):
                    evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                life_req = castle_lifes[castle_id - 1] * (-1)
                if life_req > 3:
                    life_req = 3
                evolution += f"\t\t\tcastle{castle_id}HP <= {life_req};\n"

            for castle_id in range(1, self.no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                for life in range(1, self.castles_life[castle_id - 1] + 1):
                    new_life = life + castle_lifes[castle_id - 1]
                    if new_life < 0:
                        new_life = 0

                    evolution += f"\t\tcastle{castle_id}HP={new_life} if\n"
                    for worker_id in range(0, self.no_workers):
                        evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                    evolution += f"\t\t\tcastle{castle_id}HP = {life};\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_worker(self, worker_id: int) -> str:
        agent = f"Agent Worker{worker_id + 1}\n"
        # agent += self.__create_worker_lobsvars(worker_id)
        agent += self.__create_worker_vars()
        agent += self.__create_worker_actions(worker_id)
        agent += self.__create_worker_protocol(worker_id)
        agent += self.__create_worker_evolution(worker_id)
        agent += "end Agent\n\n"
        return agent

    def __create_worker_lobsvars(self, worker_id: int) -> str:
        lobsvars = "\tLobsvars = {"

        worker_castle_id = self.get_castle_id(worker_id) + 1
        lobsvars += f"castle{worker_castle_id}HP"

        lobsvars += "};\n"
        return lobsvars

    def __create_worker_vars(self) -> str:
        vars = "\tVars:\n"
        vars += "\t\tcanDefend: boolean;\n"
        vars += "\tend Vars\n"
        return vars

    def __create_worker_actions(self, worker_id: int) -> str:
        actions = "\tActions = {"
        worker_castle_id = self.get_castle_id(worker_id)
        for castle_id in range(0, self.no_castles):
            if worker_castle_id == castle_id:
                continue
            actions += f"attack{castle_id + 1}, "
        actions += "defend, "
        if worker_castle_id == 2:
            actions += "decideTrue, decideFalse, "
        actions += "wait};\n"
        return actions

    def __create_worker_protocol(self, worker_id: int) -> str:
        protocol = "\tProtocol:\n"
        worker_castle_id = self.get_castle_id(worker_id)
        if worker_castle_id == 2:
            protocol += "\t\tEnvironment.decide=true: " + "{decideTrue, decideFalse};\n"
        else:
            protocol += "\t\tEnvironment.decide=true: " + "{wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=true and Environment.decide=false: " + "{wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=true and Environment.decide=false: " + "{defend, "
        for castle_id in range(0, self.no_castles):
            if worker_castle_id == castle_id:
                continue
            protocol += f"attack{castle_id + 1}, "
        protocol += "wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=false and Environment.decide=false: " + "{"
        for castle_id in range(0, self.no_castles):
            if worker_castle_id == castle_id:
                continue
            protocol += f"attack{castle_id + 1}, "
        protocol += "wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_worker_evolution(self, worker_id: int) -> str:
        evolution = "\tEvolution:\n"
        worker_castle_id = self.get_castle_id(worker_id)
        evolution += "\t\tcanDefend=false if Action=defend;\n"
        evolution += "\t\tcanDefend=true if canDefend=false;\n"
        if worker_castle_id == 2:
            evolution += "\t\tcanDefend=true if Action=decideTrue;\n"
            evolution += "\t\tcanDefend=false if Action=decideFalse;\n"
        evolution += "\tend Evolution\n"
        return evolution

    def __create_decider(self, castle_id: int) -> str:
        agent = f"Agent Decider{castle_id + 1}\n"
        agent += self.__create_decider_vars()
        agent += self.__create_decider_actions(castle_id)
        agent += self.__create_decider_protocol(castle_id)
        agent += self.__create_decider_evolution()
        agent += "end Agent\n\n"
        return agent

    def __create_decider_vars(self) -> str:
        vars = "\tVars:\n"
        vars += "\t\tdecide: boolean;\n"
        vars += "\tend Vars\n"
        return vars

    def __create_decider_actions(self, castle_id: int) -> str:
        actions = "\tActions = {"
        for life in range(1, self.castles_life[castle_id] + 1):
            actions += f"decideHP{life}, "
        actions += "wait};\n"
        return actions

    def __create_decider_protocol(self, castle_id: int) -> str:
        protocol = "\tProtocol:\n"
        protocol += "\t\tdecide=true: {"
        for life in range(1, self.castles_life[castle_id] + 1):
            protocol += f"decideHP{life}, "

        protocol = protocol.rstrip(" ,")
        protocol += "};\n"
        protocol += "\t\tOther: {wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_decider_evolution(self) -> str:
        evolution = "\tEvolution:\n"
        evolution += "\t\tdecide=false if decide=true;\n"
        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self) -> str:
        evaluation = "Evaluation\n"
        evaluation += "\tcastle3Defeated if Environment.castle3Defeated = true;\n"
        evaluation += "end Evaluation\n\n"
        return evaluation

    def __create_init_states(self) -> str:
        init_states = "InitStates\n"
        for castle_id in range(0, self.no_castles):
            init_states += f"\tEnvironment.castle{castle_id + 1}HP={self.castles_life[castle_id]} and\n"
            init_states += f"\tEnvironment.castle{castle_id + 1}Defeated=false and\n"
            init_states += f"\tDecider{castle_id + 1}.decide=true and\n"

        for worker_id in range(0, self.no_workers):
            init_states += f"\tWorker{worker_id + 1}.canDefend=true and\n"

        init_states += "\tEnvironment.decide=true;\n"
        init_states += "end InitStates\n\n"
        return init_states

    def __create_groups(self) -> str:
        groups = "Groups\n"
        groups += "\tc12 = {"
        for worker_id in range(0, self.workers[0] + self.workers[1]):
            groups += f"Worker{worker_id + 1}, "

        groups = groups.rstrip(" ,")
        groups += "};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self) -> str:
        formulae = "Formulae\n"
        formulae += "\t<c12>F(castle3Defeated);\n"
        formulae += "end Formulae\n\n"
        return formulae

    def get_castle_id(self, worker_id: int) -> int:
        castle_id = 0
        workers_sum = 0
        for i in self.workers:
            workers_sum += i
            if worker_id >= workers_sum:
                castle_id += 1
            else:
                break

        return castle_id
