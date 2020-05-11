from stv.generators.ispl.ispl_generator import IsplGenerator
from typing import List
import itertools


class CastlesIsplGeneratorObjective(IsplGenerator):

    def __init__(self, workers: List[int], no_castles: int = 3, castles_life=None):
        super().__init__()
        if castles_life is None:
            castles_life = [3, 3, 3]
        self._workers = workers
        self._no_workers = sum(self._workers)
        self._no_castles = no_castles
        self._castles_life = castles_life

    def _define_semantics(self) -> str:
        semantics = "Semantics=SingleAssignment;\n\n"
        return semantics

    def _create_environment_obsvars(self) -> str:
        obsvars = "\tObsvars:\n"

        for castle_id in range(1, self._no_castles + 1):
            obsvars += f"\t\tcastle{castle_id}Defeated: boolean;\n"

        obsvars += "\tend Obsvars\n"
        return obsvars

    def _create_environment_vars(self) -> str:
        vars = "\tVars:\n"

        for castle_id in range(1, self._no_castles + 1):
            vars += f"\t\tcastle{castle_id}HP: 0..{self._castles_life[castle_id - 1]};\n"

        vars += "\tend Vars\n"
        return vars

    def _create_environment_actions(self) -> str:
        return "\tActions = {none};\n"

    def _create_environment_protocol(self) -> str:
        return "\tProtocol:\n" \
               "\t\tOther: {wait};\n" \
               "\tend Protocol\n"

    def _create_environment_evolution(self) -> str:
        evolution = "\tEvolution:\n"

        actions = self.__compute_workers_actions()

        for round in itertools.product(*actions):
            castle_lifes = [0, 0, 0]
            defenders = [0, 0, 0]
            attacked = [0, 0, 0]

            worker_id = -1
            for castle_id in range(1, self._no_castles + 1):
                for _ in range(0, self._workers[castle_id - 1]):
                    worker_id += 1
                    action = round[worker_id]
                    if action == "defend":
                        defenders[castle_id - 1] += 1
                    elif action != "wait":
                        for attacked_id in range(1, self._no_castles + 1):
                            if action == f'attack{attacked_id}':
                                attacked[attacked_id - 1] += 1
                                break

            for castle_id in range(0, self._no_castles):
                if attacked[castle_id] > defenders[castle_id]:
                    castle_lifes[castle_id] -= (attacked[castle_id] - defenders[castle_id])

            for castle_id in range(1, self._no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                evolution += f"\t\tcastle{castle_id}Defeated=true if\n"
                for worker_id in range(0, self._no_workers):
                    evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                life_req = castle_lifes[castle_id - 1] * (-1)
                if life_req > 3:
                    life_req = 3
                evolution += f"\t\t\tcastle{castle_id}HP <= {life_req};\n"

            for castle_id in range(1, self._no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                for life in range(1, self._castles_life[castle_id - 1] + 1):
                    new_life = life + castle_lifes[castle_id - 1]
                    if new_life < 0:
                        new_life = 0

                    evolution += f"\t\tcastle{castle_id}HP={new_life} if\n"
                    for worker_id in range(0, self._no_workers):
                        evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                    evolution += f"\t\t\tcastle{castle_id}HP = {life};\n"

        evolution += "\tend Evolution\n"
        return evolution

    def _create_agents(self) -> str:
        agents = ""
        for worker_id in range(0, self._no_workers):
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
        worker_castle_id = self.__get_castle_id(worker_id) + 1
        return f"\tLobsvars = {{castle{worker_castle_id}HP}};\n"

    def __compute_workers_actions(self) -> List[List[str]]:
        actions = []
        worker_id = -1
        for castle_id in range(1, self._no_castles + 1):
            for _ in range(0, self._workers[castle_id - 1]):
                worker_id += 1
                actions.append(['wait', 'defend'])
                for attacked_id in range(1, self._no_castles + 1):
                    if attacked_id == castle_id:
                        continue
                    actions[-1].append(f'attack{attacked_id}')

        return actions

    def __create_worker_vars(self) -> str:
        return "\tVars:\n" \
               "\t\tcanDefend: boolean;\n" \
               "\tend Vars\n"

    def __create_worker_actions(self, worker_id: int) -> str:
        actions = "\tActions = {"
        worker_castle_id = self.__get_castle_id(worker_id)
        for castle_id in range(0, self._no_castles):
            if worker_castle_id == castle_id:
                continue
            actions += f"attack{castle_id + 1}, "
        actions += "defend, wait};\n"
        return actions

    def __create_worker_protocol(self, worker_id: int) -> str:
        protocol = "\tProtocol:\n"
        worker_castle_id = self.__get_castle_id(worker_id)
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=true: {{wait}};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=true: {{defend, "
        protocol += self.__create_worker_attack_protocol(worker_castle_id)
        protocol += "wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=false: {{"
        protocol += self.__create_worker_attack_protocol(worker_castle_id)
        protocol += "wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_worker_attack_protocol(self, worker_castle_id):
        protocol = ""
        for castle_id in range(0, self._no_castles):
            if worker_castle_id == castle_id:
                continue
            protocol += f"attack{castle_id + 1}, "
        return protocol

    def __create_worker_evolution(self) -> str:
        return "\tEvolution:\n" \
               "\t\tcanDefend=false if Action=defend;\n" \
               "\t\tcanDefend=true if canDefend=false;\n" \
               "\tend Evolution\n"

    def _create_evaluation(self) -> str:
        return "Evaluation\n" \
               "\tcastle3Defeated if Environment.castle3Defeated = true;\n" \
               "end Evaluation\n\n"

    def _create_init_states(self) -> str:
        init_states = "InitStates\n"
        init_states += self.__create_environment_init_states()
        init_states += self.__create_workers_init_states()
        init_states += "end InitStates\n\n"
        return init_states

    def __create_environment_init_states(self) -> str:
        env_init_states = ""
        for castle_id in range(0, self._no_castles):
            env_init_states += f"\tEnvironment.castle{castle_id + 1}HP={self._castles_life[castle_id]} and\n" \
                               f"\tEnvironment.castle{castle_id + 1}Defeated=false and\n"
        return env_init_states

    def __create_workers_init_states(self) -> str:
        wrk_init_states = ""
        for worker_id in range(0, self._no_workers):
            wrk_init_states += f"\tWorker{worker_id + 1}.canDefend=true and\n"
        wrk_init_states = wrk_init_states.rstrip("\ndna ")
        wrk_init_states += ";\n"
        return wrk_init_states

    def _create_groups(self) -> str:
        groups = "Groups\n"
        groups += self.__create_c12_group()
        groups += "end Groups\n\n"
        return groups

    def __create_c12_group(self) -> str:
        c12_group = "\tc12 = {"
        for worker_id in range(0, self._workers[0] + self._workers[1]):
            c12_group += f"Worker{worker_id + 1}, "
        c12_group = c12_group.rstrip(" ,")
        c12_group += "};\n"
        return c12_group

    def _create_formulae(self) -> str:
        return "Formulae\n" \
               "\t<c12>F(castle3Defeated);\n" \
               "end Formulae\n\n"

    def __get_castle_id(self, worker_id: int) -> int:
        castle_id = 0
        workers_sum = 0
        for i in self._workers:
            workers_sum += i
            if worker_id >= workers_sum:
                castle_id += 1
            else:
                break

        return castle_id


class CastlesIsplGeneratorSubjective(CastlesIsplGeneratorObjective):

    def __init__(self, workers: List[int], no_castles: int = 3, castles_life=None):
        super().__init__(workers, no_castles, castles_life)

    def _create_environment_obsvars(self) -> str:
        obsvars = "\tObsvars:\n"

        for castle_id in range(1, self._no_castles + 1):
            obsvars += f"\t\tcastle{castle_id}Defeated: boolean;\n"

        obsvars += "\t\tdecide: boolean;\n" \
                   "\tend Obsvars\n"
        return obsvars

    def _create_environment_actions(self) -> str:
        return "\tActions = {wait};\n"

    def _create_environment_evolution(self) -> str:
        evolution = "\tEvolution:\n" \
                    "\t\tdecide=false if decide=true;\n"

        for castle_id in range(0, self._no_castles):
            for life in range(1, self._castles_life[castle_id] + 1):
                evolution += f"\t\tcastle{castle_id + 1}HP={life} if Decider{castle_id + 1}.Action=decideHP{life};\n"

        actions = []
        worker_id = -1
        for castle_id in range(1, self._no_castles + 1):
            for _ in range(0, self._workers[castle_id - 1]):
                worker_id += 1
                actions.append(['wait', 'defend'])
                for attacked_id in range(1, self._no_castles + 1):
                    if attacked_id == castle_id:
                        continue
                    actions[-1].append(f'attack{attacked_id}')

        for round in itertools.product(*actions):
            castle_lifes = [0, 0, 0]
            defenders = [0, 0, 0]
            attacked = [0, 0, 0]

            worker_id = -1
            for castle_id in range(1, self._no_castles + 1):
                for _ in range(0, self._workers[castle_id - 1]):
                    worker_id += 1
                    action = round[worker_id]
                    if action == "defend":
                        defenders[castle_id - 1] += 1
                    elif action != "wait":
                        for attacked_id in range(1, self._no_castles + 1):
                            if action == f'attack{attacked_id}':
                                attacked[attacked_id - 1] += 1
                                break

            for castle_id in range(0, self._no_castles):
                if attacked[castle_id] > defenders[castle_id]:
                    castle_lifes[castle_id] -= (attacked[castle_id] - defenders[castle_id])

            for castle_id in range(1, self._no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                evolution += f"\t\tcastle{castle_id}Defeated=true if\n"
                for worker_id in range(0, self._no_workers):
                    evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                life_req = castle_lifes[castle_id - 1] * (-1)
                if life_req > 3:
                    life_req = 3
                evolution += f"\t\t\tcastle{castle_id}HP <= {life_req};\n"

            for castle_id in range(1, self._no_castles + 1):
                if castle_lifes[castle_id - 1] == 0:
                    continue

                for life in range(1, self._castles_life[castle_id - 1] + 1):
                    new_life = life + castle_lifes[castle_id - 1]
                    if new_life < 0:
                        new_life = 0

                    evolution += f"\t\tcastle{castle_id}HP={new_life} if\n"
                    for worker_id in range(0, self._no_workers):
                        evolution += f"\t\t\tWorker{worker_id + 1}.Action={round[worker_id]} and\n"

                    evolution += f"\t\t\tcastle{castle_id}HP = {life};\n"

        evolution += "\tend Evolution\n"
        return evolution

    def _create_agents(self) -> str:
        agents = ""
        for worker_id in range(0, self._no_workers):
            agents += self.__create_worker(worker_id)
        for castle_id in range(0, self._no_castles):
            agents += self.__create_decider(castle_id)

        return agents

    def __create_worker_actions(self, worker_id: int) -> str:
        actions = "\tActions = {"
        worker_castle_id = self.__get_castle_id(worker_id)
        for castle_id in range(0, self._no_castles):
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
        worker_castle_id = self.__get_castle_id(worker_id)
        if worker_castle_id == 2:
            protocol += "\t\tEnvironment.decide=true: " + "{decideTrue, decideFalse};\n"
        else:
            protocol += "\t\tEnvironment.decide=true: " + "{wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=true and " \
                    f"Environment.decide=false: {{wait}};\n" \
                    f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=true and " \
                    f"Environment.decide=false: {{defend, "
        for castle_id in range(0, self._no_castles):
            if worker_castle_id == castle_id:
                continue
            protocol += f"attack{castle_id + 1}, "
        protocol += "wait};\n"
        protocol += f"\t\tEnvironment.castle{worker_castle_id + 1}Defeated=false and canDefend=false and " \
                    f"Environment.decide=false: {{"
        for castle_id in range(0, self._no_castles):
            if worker_castle_id == castle_id:
                continue
            protocol += f"attack{castle_id + 1}, "
        protocol += "wait};\n" \
                    "\tend Protocol\n"
        return protocol

    def __create_worker_evolution(self, worker_id: int) -> str:
        evolution = "\tEvolution:\n"
        worker_castle_id = self.__get_castle_id(worker_id)
        evolution += "\t\tcanDefend=false if Action=defend;\n" \
                     "\t\tcanDefend=true if canDefend=false;\n"
        if worker_castle_id == 2:
            evolution += "\t\tcanDefend=true if Action=decideTrue;\n" \
                         "\t\tcanDefend=false if Action=decideFalse;\n"
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
        return "\tVars:\n" \
               "\t\tdecide: boolean;\n" \
               "\tend Vars\n"

    def __create_decider_actions(self, castle_id: int) -> str:
        actions = "\tActions = {"
        for life in range(1, self._castles_life[castle_id] + 1):
            actions += f"decideHP{life}, "
        actions += "wait};\n"
        return actions

    def __create_decider_protocol(self, castle_id: int) -> str:
        protocol = "\tProtocol:\n" \
                   "\t\tdecide=true: {"
        for life in range(1, self._castles_life[castle_id] + 1):
            protocol += f"decideHP{life}, "

        protocol = protocol.rstrip(" ,")
        protocol += "};\n" \
                    "\t\tOther: {wait};\n" \
                    "\tend Protocol\n"
        return protocol

    def __create_decider_evolution(self) -> str:
        return "\tEvolution:\n" \
               "\t\tdecide=false if decide=true;\n" \
               "\tend Evolution\n"

    def _create_init_states(self) -> str:
        init_states = "InitStates\n"
        for castle_id in range(0, self._no_castles):
            init_states += f"\tEnvironment.castle{castle_id + 1}HP={self._castles_life[castle_id]} and\n" \
                           f"\tEnvironment.castle{castle_id + 1}Defeated=false and\n" \
                           f"\tDecider{castle_id + 1}.decide=true and\n"

        for worker_id in range(0, self._no_workers):
            init_states += f"\tWorker{worker_id + 1}.canDefend=true and\n"

        init_states += "\tEnvironment.decide=true;\n" \
                       "end InitStates\n\n"
        return init_states


if __name__ == "__main__":
    workers = [1, 1, 1]
    castles = 3
    castles_life = [1, 1, 1]
    ispl_generator = CastlesIsplGeneratorObjective(workers, castles, castles_life)
    model_txt = ispl_generator.create_model()
    file = open("castles.ispl", "w")
    file.write(model_txt)
    file.close()
