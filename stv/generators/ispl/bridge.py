from stv.generators.ispl.ispl_generator import IsplGenerator
import itertools
import random


class BridgeModelIsplGenerator(IsplGenerator):

    @property
    def card_names(self) -> [str]:
        return ["Ace", "King", "Queen", "Jack", "ten", "nine", "eight", "seven", "six", "five", "four", "three", "two"]

    @property
    def card_colors(self) -> [str]:
        return ["Spade", "Heart", "Diamond", "Club"]

    @property
    def player_names(self) -> [str]:
        return ["SPlayer", "WPlayer", "NPlayer", "EPlayer"]

    def __init__(self, number_of_cards, number_of_cards_in_hand, card_ordering=None):
        super().__init__()
        if card_ordering is None:
            card_ordering = self.generate_random_card_array(4 * number_of_cards_in_hand)
        self._number_of_cards = number_of_cards
        self._number_of_cards_in_hand = number_of_cards_in_hand
        self._card_ordering = card_ordering
        self._cards = []
        self._available_cards = []
        self._cards_values = {}
        self._cards_colors = {}
        self._create_cards_array()
        self._create_available_cards_array()
        self._assign_cards_values()
        self._assign_cards_colors()

    def _create_cards_array(self) -> None:
        self._cards = []
        for card_name in self.card_names:
            for card_color in self.card_colors:
                self._cards.append(card_name + card_color)

    def _create_available_cards_array(self) -> None:
        self._available_cards = []
        for j in range(0, 4 * self._number_of_cards):
            self._available_cards.append(self._cards[j])

    def _assign_cards_values(self) -> None:
        i = 0
        for card_value in range(0, 13):
            for j in range(0, 4):
                self._cards_values[self._cards[i]] = 13 - card_value
                i += 1

    def _assign_cards_colors(self) -> None:
        i = 0
        for _ in range(0, 13):
            for color in self.card_colors:
                self._cards_colors[self._cards[i]] = color
                i += 1

    def _create_agents(self) -> str:
        agents = ""
        players_ids = [0, 1, 3]
        for player_id in players_ids:
            agents += self._create_player(player_id)
        return agents

    def _define_semantics(self) -> str:
        semantics = "Semantics=SingleAssignment;\n\n"
        return semantics

    def _create_environment_obsvars(self) -> str:
        obsvars = f"\tObsvars:\n" \
                  f"\t\tfirstTeamScore: 0..{self._number_of_cards_in_hand};\n" \
                  f"\t\tsecondTeamScore: 0..{self._number_of_cards_in_hand};\n" \
                  f"\t\tbeginningPlayer: 0..3;\n" \
                  f"\t\tcurrentPlayer: 0..4;\n" \
                  f"\t\tclock: 0..4;\n"
        obsvars += self._create_env_player_cards_obsvars()
        obsvars += self._create_env_n_cards_obsvars()
        obsvars += self._create_env_history_cards_obsvars()
        obsvars += "\t\tsuit: {Spade, Heart, Diamond, Club, None};\n"
        obsvars += self._create_env_has_color_obsvars()
        obsvars += "\tend Obsvars\n"
        return obsvars

    def _create_env_player_cards_obsvars(self) -> str:
        obsvars = ""
        for player in self.player_names:
            obsvars += f"\t\t{player}Card: {{"
            for j in range(0, 4 * self._number_of_cards):
                obsvars += f"{self._cards[j]}, "
            obsvars += "None};\n"
        return obsvars

    def _create_env_n_cards_obsvars(self) -> str:
        obsvars = ""
        for i in range(1, self._number_of_cards_in_hand + 1):
            obsvars += f"\t\tcardN{i}: {{"
            for j in range(0, 4 * self._number_of_cards):
                obsvars += f"N{self._cards[j]}, "
            obsvars += "None};\n"
        return obsvars

    def _create_env_history_cards_obsvars(self) -> str:
        obsvars = ""
        for i in range(0, self._number_of_cards * 4):
            obsvars += f"\t\t{self._cards[i]}H: boolean;\n"
        return obsvars

    def _create_env_has_color_obsvars(self) -> str:
        obsvars = ""
        for color in self.card_colors:
            obsvars += f"\t\thas{color}: 0..{self._number_of_cards_in_hand};\n"
        return obsvars

    def _create_environment_vars(self) -> str:
        vars = "\tVars:\n" \
               "\t\tsmc: 0..1;\n" \
               "\tend Vars\n"
        return vars

    def _create_environment_actions(self) -> str:
        actions = "\tActions = {none};\n"
        return actions

    def _create_environment_protocol(self) -> str:
        protocol = "\tProtocol:\n" \
                   "\t\tOther:{none};\n" \
                   "\tend Protocol\n"
        return protocol

    def _create_environment_evolution(self) -> str:
        evolution = "\tEvolution:\n"
        evolution += self._create_env_first_team_score_evolution()
        evolution += self._create_env_second_team_score_evolution()
        evolution += self._create_env_beginning_player_evolution()
        evolution += self._create_env_current_player_evolution()
        evolution += self._create_env_clock_evolution()
        evolution += self._create_env_player_cards_evolution()
        evolution += self._create_env_suit_evolution()
        evolution += self._create_env_history_evolution()
        evolution += self._create_env_n_cards_evolution()
        evolution += self._create_env_has_color_evolution()
        evolution += "\tend Evolution\n"
        return evolution

    def _create_env_first_team_score_evolution(self) -> str:
        evolution = "\t\tfirstTeamScore=firstTeamScore+1 if\n"
        for combination in itertools.permutations(self._available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self._cards_colors[combination[i]] == self._cards_colors[
                        combination[winning_player_number]]:
                        if self._cards_values[combination[i]] > self._cards_values[
                            combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 0 or winning_player_number == 2):
                    continue

                evolution += "\t\t\t(\n"
                for player in range(0, 4):
                    evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"

                evolution += f"\t\t\t\tbeginningPlayer={beginning_player}) or\n"

        evolution = evolution.rstrip("\nro ")
        evolution += ";\n"
        return evolution

    def _create_env_second_team_score_evolution(self) -> str:
        evolution = "\t\tsecondTeamScore=secondTeamScore+1 if\n"
        for combination in itertools.permutations(self._available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self._cards_colors[combination[i]] == self._cards_colors[
                        combination[winning_player_number]]:
                        if self._cards_values[combination[i]] > self._cards_values[
                            combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 1 or winning_player_number == 3):
                    continue

                evolution += "\t\t\t(\n"
                for player in range(0, 4):
                    evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"

                evolution += f"\t\t\t\tbeginningPlayer={beginning_player}) or\n"

        evolution = evolution.rstrip("\nro ")
        evolution += ";\n"
        return evolution

    def _create_env_beginning_player_evolution(self) -> str:
        evolution = ""
        for winning_player in range(0, 4):
            evolution += f"\t\tbeginningPlayer={winning_player} if\n"
            for combination in itertools.permutations(self._available_cards, 4):
                for beginning_player in range(0, 4):
                    winning_player_number = beginning_player
                    for i in range(0, 4):
                        if i == beginning_player:
                            continue

                        if self._cards_colors[combination[i]] == self._cards_colors[
                            combination[winning_player_number]]:
                            if self._cards_values[combination[i]] > self._cards_values[
                                combination[winning_player_number]]:
                                winning_player_number = i

                    if not (winning_player_number == winning_player):
                        continue

                    evolution += "\t\t\t(\n"
                    for player in range(0, 4):
                        evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"

                    evolution += f"\t\t\t\tbeginningPlayer={beginning_player}) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"
        return evolution

    def _create_env_current_player_evolution(self) -> str:
        evolution = ""
        for winning_player in range(0, 4):
            evolution += f"\t\tcurrentPlayer={winning_player} if\n"
            for combination in itertools.permutations(self._available_cards, 4):
                for beginning_player in range(0, 4):
                    winning_player_number = beginning_player
                    for i in range(0, 4):
                        if i == beginning_player:
                            continue
                        if self._cards_colors[combination[i]] == self._cards_colors[
                            combination[winning_player_number]]:
                            if self._cards_values[combination[i]] > self._cards_values[
                                combination[winning_player_number]]:
                                winning_player_number = i

                    if not (winning_player_number == winning_player):
                        continue
                    evolution += "\t\t\t(\n"
                    for player in range(0, 4):
                        evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"
                    evolution += f"\t\t\t\tbeginningPlayer={beginning_player}) or\n"
            previous_player = winning_player - 1
            if previous_player == -1:
                previous_player = 3
            evolution += f"\t\t\t(currentPlayer={previous_player} and clock<4);\n"
        return evolution

    def _create_env_clock_evolution(self) -> str:
        evolution = "\t\tsuit=None if clock=4;\n" \
                    "\t\tclock=0 if clock=4;\n"
        for clock in range(1, 5):
            evolution += f"\t\tclock={clock} if clock={clock - 1};\n"
        for player in self.player_names:
            evolution += f"\t\t{player}Card=None if clock=4;\n"
        return evolution

    def _create_env_player_cards_evolution(self) -> str:
        evolution = ""
        for i in range(0, self._number_of_cards * 4):
            card = self._cards[i]
            for player_number in range(0, 4):
                player = self.player_names[player_number]
                if player == self.player_names[2]:
                    evolution += f"\t\t{player}Card={card} if {self.player_names[0]}.Action=Play{card} " \
                                 f"and currentPlayer=2;\n"
                else:
                    evolution += f"\t\t{player}Card={card} if {player}.Action=Play{card} and " \
                                 f"currentPlayer={player_number};\n"
        return evolution

    def _create_env_suit_evolution(self) -> str:
        evolution = ""
        for color in self.card_colors:
            evolution += f"\t\tsuit={color} if clock=0 and (\n"
            for i in range(0, self._number_of_cards * 4):
                card = self._cards[i]
                if self._cards_colors[card] != color:
                    continue
                for player in self.player_names:
                    if player == self.player_names[2]:
                        continue
                    evolution += f"\t\t\t{player}.Action=Play{card} or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"
        return evolution

    def _create_env_history_evolution(self) -> str:
        evolution = ""
        for i in range(0, self._number_of_cards * 4):
            card = self._cards[i]
            evolution += f"\t\t{card}H=true if\n"
            for player in self.player_names:
                if player == self.player_names[2]:
                    continue
                evolution += f"\t\t\t{player}.Action=Play{card} or\n"
            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"
        return evolution

    def _create_env_n_cards_evolution(self) -> str:
        evolution = ""
        for i in range(0, self._number_of_cards * 4):
            card = self._cards[i]
            for j in range(1, self._number_of_cards_in_hand + 1):
                evolution += f"\t\tcardN{j}=None if {self.player_names[0]}.Action=Play{card} and cardN{j}=N{card};\n"
        return evolution

    def _create_env_has_color_evolution(self) -> str:
        evolution = ""
        for color in self.card_colors:
            evolution += f"\t\thas{color}=has{color}+-1 if (\n"
            for i in range(0, self._number_of_cards * 4):
                card = self._cards[i]
                if self._cards_colors[card] != color:
                    continue
                evolution += f"\t\t\t({self.player_names[0]}.Action=Play{card} and ("
                for j in range(1, self._number_of_cards_in_hand + 1):
                    evolution += f"cardN{j}=N{card} or "
                evolution = evolution.rstrip(" ro ")
                evolution += ")) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"
        return evolution

    def _create_player(self, player_number) -> str:
        player = f"Agent {self.player_names[player_number]}\n"
        # if player_name != "ThirdPlayer":
        #     player += self.__create_player_lobsvars()
        player += self._create_player_vars(player_number)
        player += self._create_player_actions()
        player += self._create_player_protocol(player_number)
        player += self._create_player_evolution(player_number)
        player += "end Agent\n\n"
        return player

    def _create_player_lobsvars(self) -> str:
        lobsvars = "\tLobsvars = {"
        for i in range(1, self._number_of_cards_in_hand + 1):
            lobsvars += f"ThirdPlayer.card{i}"
            if i != self._number_of_cards_in_hand:
                lobsvars += ", "

        lobsvars += "};\n"
        return lobsvars

    def _create_player_vars(self, player_number) -> str:
        vars = "\tVars:\n"
        for i in range(1, self._number_of_cards_in_hand + 1):
            vars += f"\t\t{self.player_names[player_number][0]}card{i}: {{"
            for j in range(0, 4 * self._number_of_cards):
                vars += f"{self.player_names[player_number][0]}{self._cards[j]}, "
            vars += "None};\n"

        for color in self.card_colors:
            vars += f"\t\thas{color}: 0..{self._number_of_cards_in_hand};\n"

        vars += "\tend Vars\n"
        return vars

    def _create_player_actions(self) -> str:
        actions = "\tActions = {"
        for i in range(0, 4 * self._number_of_cards):
            actions += f"Play{self._cards[i]}, "

        actions += "Wait};\n"
        return actions

    def _create_player_protocol(self, player_number) -> str:
        protocol = "\tProtocol:\n"
        for i in range(1, self._number_of_cards_in_hand + 1):
            for j in range(0, 4 * self._number_of_cards):
                protocol += f"\t\t{self.player_names[player_number][0]}card{i}=" \
                            f"{self.player_names[player_number][0]}{self._cards[j]} and " \
                            f"Environment.currentPlayer={player_number} and Environment.clock<4 and " \
                            f"(Environment.suit=None or Environment.suit={self._cards_colors[self._cards[j]]} or " \
                            f"((hasSpade<=0 and Environment.suit=Spade) or (hasClub<=0 and " \
                            f"Environment.suit=Club) or (hasDiamond<=0 and Environment.suit=Diamond) or " \
                            f"(hasHeart<=0 and Environment.suit=Heart))): {{Play" + \
                            self._cards[j] + "};\n"

        if player_number == 0:
            for i in range(1, self._number_of_cards_in_hand + 1):
                for j in range(0, 4 * self._number_of_cards):
                    protocol += "\t\tEnvironment.cardN" + str(i) + "=N"
                    protocol += f"{self._cards[j]} and Environment.currentPlayer=2 and " \
                                "Environment.clock<4 and " \
                                "(Environment.suit=None or Environment.suit=" \
                                f"{self._cards_colors[self._cards[j]]} or " \
                                "((Environment.hasSpade<=0 and Environment.suit=Spade) or " \
                                "(Environment.hasClub<=0 and Environment.suit=Club) or " \
                                "(Environment.hasDiamond<=0 and Environment.suit=Diamond) or " \
                                "(Environment.hasHeart<=0 and Environment.suit=Heart))): " \
                                f"{{Play{self._cards[j]}}};\n"

        if player_number != 0:
            protocol += f"\t\t!(Environment.currentPlayer={player_number}) or Environment.clock=4: " \
                        f"{{Wait}};\n"
        else:
            protocol += f"\t\t(!(Environment.currentPlayer={player_number}) and " \
                        f"!(Environment.currentPlayer=2)) or Environment.clock=4: {{Wait}};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def _create_player_evolution(self, player_number) -> str:
        evolution = "\tEvolution:\n"
        for i in range(1, self._number_of_cards_in_hand + 1):
            evolution += f"\t\t{self.player_names[player_number][0]}card{i}=None if\n"
            for j in range(0, 4 * self._number_of_cards):
                card = self._cards[j]
                evolution += f"\t\t\t({self.player_names[player_number][0]}card{i}=" \
                             f"{self.player_names[player_number][0]}{card} and Action=Play{card}) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for color in self.card_colors:
            evolution += f"\t\thas{color}=has{color}+-1 if\n"
            for i in range(1, self._number_of_cards_in_hand + 1):
                for j in range(0, 4 * self._number_of_cards):
                    card = self._cards[j]
                    if self._cards_colors[card] != color:
                        continue
                    evolution += f"\t\t\t({self.player_names[player_number][0]}card{i}=" \
                                 f"{self.player_names[player_number][0]}{card} and Action=Play{card}) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        evolution += "\tend Evolution\n"
        return evolution

    def _create_evaluation(self) -> str:
        evaulation = "Evaluation\n" \
                     "\tFirstTeamWin if Environment.firstTeamScore>Environment.secondTeamScore and " \
                     f"Environment.firstTeamScore+Environment.secondTeamScore={self._number_of_cards_in_hand};\n" \
                     "\tSecondTeamWin if Environment.firstTeamScore<Environment.secondTeamScore and " \
                     "Environment.firstTeamScore+Environment.secondTeamScore={self.__number_of_cards_in_hand};\n" \
                     "end Evaluation\n\n"
        return evaulation

    def _create_init_states(self) -> str:
        init_states = "InitStates\n"
        oponents_cards = []
        for k in range(self._number_of_cards_in_hand, self._number_of_cards_in_hand * 2):
            oponents_cards.append(self._card_ordering[k])

        for k in range(self._number_of_cards_in_hand * 3, self._number_of_cards_in_hand * 4):
            oponents_cards.append(self._card_ordering[k])

        oponents_cards.sort()
        number_of_beginning_states = 0

        for combination in itertools.combinations(oponents_cards, self._number_of_cards_in_hand):
            second_player_cards = combination
            fourth_player_cards = oponents_cards[:]
            for card in second_player_cards:
                fourth_player_cards.remove(card)

            new_card_ordering = self._card_ordering[:]
            i = 0
            for k in range(self._number_of_cards_in_hand, self._number_of_cards_in_hand * 2):
                new_card_ordering[k] = second_player_cards[i]
                i += 1

            i = 0
            for k in range(self._number_of_cards_in_hand * 3, self._number_of_cards_in_hand * 4):
                new_card_ordering[k] = fourth_player_cards[i]
                i += 1

            init_states += "\t(Environment.smc=0 and Environment.firstTeamScore=0 and " \
                           "Environment.secondTeamScore=0 and Environment.beginningPlayer=0 and " \
                           "Environment.currentPlayer=0 and Environment.clock=0 and " \
                           "Environment.SPlayerCard=None and Environment.WPlayerCard=None and " \
                           "Environment.NPlayerCard=None and Environment.EPlayerCard=None and " \
                           "Environment.suit=None"
            colors_count = {}
            i = 0
            for player in self.player_names:
                colors_count[player] = {}
                for color in self.card_colors:
                    colors_count[player][color] = 0
                for j in range(1, self._number_of_cards_in_hand + 1):
                    colors_count[player][self._cards_colors[self._cards[new_card_ordering[i]]]] += 1
                    i += 1
            i = 0
            for player in self.player_names:
                for color in self.card_colors:
                    if player == "NPlayer":
                        init_states += f" and Environment.has{color}={colors_count[player][color]}"
                    else:
                        init_states += f" and {player}.has{color}={colors_count[player][color]}"

            for player in self.player_names:
                for j in range(1, self._number_of_cards_in_hand + 1):
                    if player == "NPlayer":
                        init_states += f" and Environment.cardN{j}=N{self._cards[new_card_ordering[i]]}"
                    else:
                        init_states += f" and {player}.{player[0]}card{j}=" \
                                       f"{player[0]}{self._cards[new_card_ordering[i]]}"

                    i += 1

            for j in range(0, self._number_of_cards * 4):
                init_states += f" and Environment.{self._cards[j]}H=false"

            init_states += ") or\n"
            number_of_beginning_states += 1

        print(f"Number of beginning states: {number_of_beginning_states}")
        init_states = init_states.rstrip("\nro ")
        init_states += ";\nend InitStates\n\n"
        return init_states

    def _create_groups(self) -> str:
        groups = "Groups\n" \
                 "\tg1={SPlayer};\n" \
                 "end Groups\n\n"
        return groups

    def _create_formulae(self) -> str:
        formulae = "Formulae\n" \
                   "\t<g1>F FirstTeamWin;\n" \
                   "end Formulae\n\n"
        return formulae

    @staticmethod
    def generate_random_card_array(length: int) -> [int]:
        array = []
        used = []
        for i in range(0, length):
            used.append(False)

        for i in range(0, length):
            number = random.randrange(length)
            while used[number]:
                number = random.randrange(length)

            array.append(number)
            used[number] = True

        return array


class AbsentMindedBridgeModelIsplGenerator(BridgeModelIsplGenerator):

    def __init__(self, number_of_cards, number_of_cards_in_hand, card_ordering=None):
        super().__init__(number_of_cards, number_of_cards_in_hand, card_ordering)

    def _define_semantics(self) -> str:
        semantics = "Semantics=MultiAssignment;\n\n"
        return semantics

    def _create_environment_obsvars(self):
        obsvars = "\tObsvars:\n" \
                  f"\t\tfirstTeamScore: 0..{self._number_of_cards_in_hand};\n" \
                  f"\t\tsecondTeamScore: 0..{self._number_of_cards_in_hand};\n" \
                  "\t\tbeginningPlayer: 0..3;\n" \
                  "\t\tcurrentPlayer: 0..4;\n" \
                  "\t\tclock: 0..5;\n"
        obsvars += self._create_env_player_cards_obsvars()
        obsvars += self._create_env_n_cards_obsvars()
        obsvars += self._create_env_history_cards_obsvars()
        obsvars += "\tend Obsvars\n"
        return obsvars

    def _create_env_player_cards_obsvars(self) -> str:
        obsvars = f"\t\t{self.player_names[0]}Card: {{"
        for j in range(0, 4 * self._number_of_cards):
            obsvars += f"{self._cards[j]}, "
        obsvars += "None};\n"
        return obsvars

    def _create_env_n_cards_obsvars(self) -> str:
        obsvars = ""
        for i in range(1, self._number_of_cards_in_hand + 1):
            obsvars += f"\t\tcardN{i}: {{"
            for j in range(0, 4 * self._number_of_cards):
                obsvars += f"{self._cards[j]}, "
            obsvars += "None};\n"
        return obsvars

    def _create_environment_vars(self):
        vars = "\tVars:\n"
        vars += self._create_env_card_vars()
        vars += self._create_env_n_card_vars()
        vars += "\t\tsuit: {Spade, Heart, Diamond, Club, None};\n" \
                "\tend Vars\n"
        return vars

    def _create_env_card_vars(self) -> str:
        vars = ""
        for player in self.player_names:
            if player == self.player_names[0]:
                continue
            vars += f"\t\t{player}Card: {{"
            for j in range(0, 4 * self._number_of_cards):
                vars += f"{self._cards[j]}, "
            vars += "None};\n"
        return vars

    def _create_env_n_card_vars(self) -> str:
        vars = ""
        for i in range(1, self._number_of_cards_in_hand + 1):
            vars += f"\t\tcurrentCardN{i}: {{"
            for j in range(0, 4 * self._number_of_cards):
                vars += f"{self._cards[j]}, "
            vars += "None};\n"
        return vars

    def _create_environment_evolution(self) -> str:
        evolution = "\tEvolution:\n"

        for winning_player in range(0, 4):
            if winning_player % 2 == 0:
                evolution += "\t\tfirstTeamScore=firstTeamScore+1"
            else:
                evolution += "\t\tsecondTeamScore=secondTeamScore+1"

            evolution += f" and beginningPlayer={winning_player}" \
                         f" and clock=0 and suit=None and currentPlayer={winning_player}"

            for player in self.player_names:
                evolution += f" and {player}Card=None"

            for j in range(1, self._number_of_cards_in_hand + 1):
                evolution += f" and cardN{j}=currentCardN{j}"

            evolution += " if\n"
            add_or = False
            for combination in itertools.permutations(self._available_cards, 4):
                for beginning_player in range(0, 4):
                    winning_player_number = beginning_player
                    for i in range(0, 4):
                        if i == beginning_player:
                            continue

                        if self._cards_colors[combination[i]] == self._cards_colors[combination[winning_player_number]]:
                            if self._cards_values[combination[i]] > self._cards_values[
                                combination[winning_player_number]]:
                                winning_player_number = i

                    if not (winning_player_number == winning_player):
                        continue

                    if add_or:
                        evolution += " or\n"
                    else:
                        add_or = True

                    evolution += "\t\t\t("
                    for player in range(0, 4):
                        evolution += f"{self.player_names[player]}Card={combination[player]} and "

                    evolution += f"beginningPlayer={beginning_player} and clock>=4)"

            evolution += ";\n"

        for i in range(0, self._number_of_cards * 4):
            card = self._cards[i]

            # Player S plays
            evolution += f"\t\tcurrentPlayer=1 and clock=clock+1 and SPlayerCard={card} and {card}H=true if\n" \
                         f"\t\t\tcurrentPlayer=0 and clock<4 and clock>0 and SPlayer.Action=Play{card};\n" \
                         f"\t\tcurrentPlayer=1 and clock=clock+1 and SPlayerCard={card} and {card}H=true" \
                         f" and suit={self._cards_colors[card]} if\n" \
                         f"\t\t\tcurrentPlayer=0 and clock<4 and clock=0 and SPlayer.Action=Play{card};\n"

            # Player S should play, but play Player N card

            for j in range(1, self._number_of_cards_in_hand + 1):
                evolution += f"\t\tNPlayerCard={card} and {card}H=true and currentCardN{j}=None if\n" \
                             f"\t\t\tcurrentPlayer=0 and clock<4 and SPlayer.Action=PlayN{card} and " \
                             f"currentCardN{j}={card} and NPlayerCard=None;\n"

            # Player W plays, Player S Wait

            evolution += f"\t\tcurrentPlayer=2 and clock=clock+1 and WPlayerCard={card} and {card}H=true if\n" \
                         f"\t\t\tcurrentPlayer=1 and clock>0 and WPlayer.Action=Play{card} and SPlayer.Action=Wait and NPlayerCard=None;\n" \
                         f"\t\tcurrentPlayer=2 and clock=clock+1 and WPlayerCard={card} and {card}H=true" \
                         f" and suit={self._cards_colors[card]} if\n" \
                         f"\t\t\tcurrentPlayer=1 and clock=0 and WPlayer.Action=Play{card} and SPlayer.Action=Wait and NPlayerCard=None;\n" \
                         f"\t\tcurrentPlayer=3 and clock=clock+2 and WPlayerCard={card} and {card}H=true if\n" \
                         f"\t\t\tcurrentPlayer=1 and clock>0 and WPlayer.Action=Play{card} and SPlayer.Action=Wait and !(NPlayerCard=None);\n" \
                         f"\t\tcurrentPlayer=3 and clock=clock+2 and WPlayerCard={card} and {card}H=true" \
                         f" and suit={self._cards_colors[card]} if\n" \
                         f"\t\t\tcurrentPlayer=1 and clock=0 and WPlayer.Action=Play{card} and SPlayer.Action=Wait and !(NPlayerCard=None);\n"

            # Player W plays, Player S Play his card
            for i2 in range(0, self._number_of_cards * 4):
                card2 = self._cards[i2]

                if card == card2:
                    continue

                evolution += f"\t\tcurrentPlayer=2 and clock=clock+1 and WPlayerCard={card} and {card}H=true" \
                             f" and SPlayerCard={card2} and {card2}H=true" \
                             f" and suit={self._cards_colors[card]} if\n" \
                             f"\t\t\tcurrentPlayer=1 and clock=0 and WPlayer.Action=Play{card} and SPlayer.Action=Play{card2} and NPlayerCard=None;\n" \
                             f"\t\tcurrentPlayer=3 and clock=clock+2 and WPlayerCard={card} and {card}H=true" \
                             f" and SPlayerCard={card2} and {card2}H=true" \
                             f" and suit={self._cards_colors[card]} if\n" \
                             f"\t\t\tcurrentPlayer=1 and clock=0 and WPlayer.Action=Play{card} and SPlayer.Action=Play{card2} and !(NPlayerCard=None);\n"

            # Player W plays, Player S Play N card
            for i2 in range(0, self._number_of_cards * 4):
                card2 = self._cards[i2]
                if card == card2:
                    continue

                for j in range(1, self._number_of_cards_in_hand + 1):
                    evolution += f"\t\tcurrentPlayer=3 and clock=clock+2 and WPlayerCard={card} and {card}H=true" \
                                 f" and NPlayerCard={card2} and {card2}H=true" \
                                 f" and currentCardN{j}=None if\n" \
                                 f"\t\t\tcurrentPlayer=1 and clock>0 and WPlayer.Action=Play{card} " \
                                 f"and SPlayer.Action=PlayN{card2} and NPlayerCard=None" \
                                 f" and currentCardN{j}={card2};\n" \
                                 f"\t\tcurrentPlayer=3 and clock=clock+2 and WPlayerCard={card} and {card}H=true" \
                                 f" and NPlayerCard={card2} and {card2}H=true" \
                                 f" and currentCardN{j}=None" \
                                 f" and suit={self._cards_colors[card]} if\n" \
                                 f"\t\t\tcurrentPlayer=1 and clock=0 and WPlayer.Action=Play{card} and " \
                                 f"SPlayer.Action=PlayN{card2} and NPlayerCard=None" \
                                 f" and currentCardN{j}={card2};\n"

                evolution += f"\t\tcurrentPlayer=3 and clock=clock+2 and WPlayerCard={card} and {card}H=true if\n" \
                             f"\t\t\tcurrentPlayer=1 and clock>0 and WPlayer.Action=Play{card} and SPlayer.Action=PlayN{card2} " \
                             f"and !(NPlayerCard=None);\n" \
                             f"\t\tcurrentPlayer=3 and clock=clock+2 and WPlayerCard={card} and {card}H=true" \
                             f" and suit={self._cards_colors[card]} if\n" \
                             f"\t\t\tcurrentPlayer=1 and clock=0 and WPlayer.Action=Play{card} and SPlayer.Action=PlayN{card2} " \
                             f"and !(NPlayerCard=None);\n"

            # Player N Plays

            for j in range(1, self._number_of_cards_in_hand + 1):
                evolution += f"\t\tcurrentPlayer=3 and clock=clock+1 and NPlayerCard={card} and {card}H=true " \
                             f"and currentCardN{j}=None if\n" \
                             f"\t\t\tcurrentPlayer=2 and clock>0 and clock<4 and SPlayer.Action=PlayN{card} " \
                             f"and currentCardN{j}={card} and NPlayerCard=None;\n" \
                             f"\t\tcurrentPlayer=3 and clock=clock+1 and NPlayerCard={card} and {card}H=true and " \
                             f"currentCardN{j}=None and suit={self._cards_colors[card]} if\n" \
                             f"\t\t\tcurrentPlayer=2 and clock=0 and SPlayer.Action=PlayN{card} and " \
                             f"currentCardN{j}={card} and NPlayerCard=None;\n"

            # Player N should Play, Player S play his own card

            evolution += f"\t\tSPlayerCard={card} and {card}H=true if\n" \
                         f"\t\t\tcurrentPlayer=2 and clock<4 and SPlayer.Action=Play{card};\n"

            # Player E Plays, Player S Wait

            evolution += f"\t\tcurrentPlayer=0 and clock=clock+1 and EPlayerCard={card} and {card}H=true if\n" \
                         f"\t\t\tcurrentPlayer=3 and clock>0 and EPlayer.Action=Play{card} and SPlayer.Action=Wait " \
                         f"and SPlayerCard=None;\n" \
                         f"\t\tcurrentPlayer=0 and clock=clock+1 and EPlayerCard={card} and {card}H=true" \
                         f" and suit={self._cards_colors[card]} if\n" \
                         f"\t\t\tcurrentPlayer=3 and clock=0 and EPlayer.Action=Play{card} and SPlayer.Action=Wait " \
                         f"and SPlayerCard=None;\n" \
                         f"\t\tcurrentPlayer=1 and clock=clock+2 and EPlayerCard={card} and {card}H=true if\n" \
                         f"\t\t\tcurrentPlayer=3 and clock>0 and EPlayer.Action=Play{card} and SPlayer.Action=Wait " \
                         f"and !(SPlayerCard=None);\n" \
                         f"\t\tcurrentPlayer=1 and clock=clock+2 and EPlayerCard={card} and {card}H=true" \
                         f" and suit={self._cards_colors[card]} if\n" \
                         f"\t\t\tcurrentPlayer=3 and clock=0 and EPlayer.Action=Play{card} and SPlayer.Action=Wait and !(SPlayerCard=None);\n"

            # Player E Plays, Player S Play his card

            for i2 in range(0, self._number_of_cards * 4):
                card2 = self._cards[i2]

                if card == card2:
                    continue

                evolution += f"\t\tcurrentPlayer=1 and clock=clock+2 and EPlayerCard={card} and {card}H=true" \
                             f" and SPlayerCard={card2} and {card2}H=true" \
                             f" and suit={self._cards_colors[card]} if\n" \
                             f"\t\t\tcurrentPlayer=3 and clock=0 and EPlayer.Action=Play{card} and SPlayer.Action=Play{card2};\n" \
                             f"\t\tcurrentPlayer=1 and clock=clock+2 and EPlayerCard={card} and {card}H=true" \
                             f" and SPlayerCard={card2} and {card2}H=true if\n" \
                             f"\t\t\tcurrentPlayer=3 and clock>0 and EPlayer.Action=Play{card} and SPlayer.Action=Play{card2};\n"

            # Player E Plays, Player S Play N card

            for i2 in range(0, self._number_of_cards * 4):
                card2 = self._cards[i2]
                if card == card2:
                    continue

                for j in range(1, self._number_of_cards_in_hand + 1):
                    evolution += f"\t\tcurrentPlayer=0 and clock=clock+1 and EPlayerCard={card} and {card}H=true " \
                                 f"and NPlayerCard={card2} and {card2}H=true and currentCardN{j}=None " \
                                 f"and suit={self._cards_colors[card]} if\n" \
                                 f"\t\t\tcurrentPlayer=3 and clock=0 and EPlayer.Action=Play{card} " \
                                 f"and SPlayer.Action=PlayN{card2} and NPlayerCard=None " \
                                 f"and currentCardN{j}={card2} and SPlayerCard=None;\n" \
                                 f"\t\tcurrentPlayer=1 and clock=clock+2 and EPlayerCard={card} and {card}H=true " \
                                 f"and NPlayerCard={card2} and {card2}H=true " \
                                 f"and currentCardN{j}=None and suit={self._cards_colors[card]} if\n" \
                                 f"\t\t\tcurrentPlayer=3 and clock=0 and EPlayer.Action=Play{card} " \
                                 f"and SPlayer.Action=PlayN{card2} and NPlayerCard=None and currentCardN{j}={card2} " \
                                 f"and !(SPlayerCard=None);\n"

                evolution += f"\t\tcurrentPlayer=0 and clock=clock+1 and EPlayerCard={card} and {card}H=true if\n" \
                             f"\t\t\tcurrentPlayer=3 and clock>0 and EPlayer.Action=Play{card} and SPlayer.Action=PlayN{card2} " \
                             f"and !(NPlayerCard=None) and SPlayerCard=None;\n" \
                             f"\t\tcurrentPlayer=1 and clock=clock+2 and EPlayerCard={card} and {card}H=true if\n" \
                             f"\t\t\tcurrentPlayer=3 and clock>0 and EPlayer.Action=Play{card} and SPlayer.Action=PlayN{card2} " \
                             f"and !(NPlayerCard=None) and !(SPlayerCard=None);\n"

        evolution += "\tend Evolution\n"
        return evolution

    def _create_player(self, player_number) -> str:
        player = f"Agent {self.player_names[player_number]}\n"
        if player_number != 0:
            player += self._create_player_lobsvars()
        player += self._create_player_vars(player_number)
        player += self._create_player_actions(player_number)
        player += self._create_player_protocol(player_number)
        player += self._create_player_evolution(player_number)
        player += "end Agent\n\n"
        return player

    def _create_player_lobsvars(self) -> str:
        lobsvars = "\tLobsvars = {"
        for player in self.player_names:
            if player == self.player_names[0]:
                continue
            lobsvars += f"{player}Card, "

        for i in range(1, self._number_of_cards_in_hand + 1):
            lobsvars += f"currentCardN{i}, "

        lobsvars += "suit};\n"
        return lobsvars

    def _create_player_vars(self, player_number: int) -> str:
        vars = "\tVars:\n"
        for i in range(1, self._number_of_cards_in_hand + 1):
            vars += f"\t\tcard{i}: {{"
            for j in range(0, 4 * self._number_of_cards):
                vars += f"{self._cards[j]}, "
            vars += "None};\n"

        if player_number != 0:
            for color in self.card_colors:
                vars += f"\t\thas{color}: 0..{self._number_of_cards_in_hand};\n"

        vars += "\tend Vars\n"
        return vars

    def _create_player_actions(self, player_number: int) -> str:
        actions = "\tActions = {"
        for i in range(0, 4 * self._number_of_cards):
            actions += f"Play{self._cards[i]}, "

        if player_number == 0:
            for i in range(0, 4 * self._number_of_cards):
                actions += f"PlayN{self._cards[i]}, "

        actions += "Wait};\n"
        return actions

    def _create_player_protocol(self, player_number: int) -> str:
        protocol = "\tProtocol:\n"
        for i in range(1, self._number_of_cards_in_hand + 1):
            for j in range(0, 4 * self._number_of_cards):
                protocol += f"\t\tcard{i}={self._cards[j]}"
                if player_number != 0:
                    protocol += f" and Environment.currentPlayer={player_number} and Environment.clock<4 and " \
                                f"(Environment.suit=None or Environment.suit={self._cards_colors[self._cards[j]]} " \
                                f"or ((hasSpade<=0 and Environment.suit=Spade) or " \
                                f"(hasClub<=0 and Environment.suit=Club) or (hasDiamond<=0 and " \
                                f"Environment.suit=Diamond) or (hasHeart<=0 and Environment.suit=Heart))):"
                else:
                    protocol += " and Environment.SPlayerCard=None:"
                protocol += f" {{Play{self._cards[j]}"
                if player_number == 0:
                    protocol += ", Wait"

                protocol += "};\n"

        if player_number == 0:
            for i in range(1, self._number_of_cards_in_hand + 1):
                for j in range(0, 4 * self._number_of_cards):
                    protocol += f"\t\tEnvironment.cardN{i}={self._cards[j]}: {{PlayN{self._cards[j]}, Wait}};\n"

        protocol += "\t\tOther: {Wait};\n" \
                    "\tend Protocol\n"
        return protocol

    def _create_player_evolution(self, player_number: int) -> str:
        evolution = "\tEvolution:\n"
        for i in range(1, self._number_of_cards_in_hand + 1):
            for j in range(0, 4 * self._number_of_cards):
                evolution += f"\t\tcard{i}=None"
                if player_number != 0:
                    evolution += f" and has{self._cards_colors[self._cards[j]]}=" \
                                 f"has{self._cards_colors[self._cards[j]]}-1"
                evolution += f" if card{i}={self._cards[j]} and Action=Play{self._cards[j]}"
                if player_number == 0:
                    evolution += " and Environment.SPlayerCard=None;\n"
                else:
                    evolution += f" and Environment.currentPlayer={player_number};\n"

        evolution += "\tend Evolution\n"
        return evolution

    def _create_evaluation(self) -> str:
        evaulation = f"Evaluation\n" \
                     f"\tFirstTeamWin if Environment.firstTeamScore>Environment.secondTeamScore " \
                     f"and Environment.firstTeamScore+Environment.secondTeamScore={self._number_of_cards_in_hand};\n" \
                     f"\tSecondTeamWin if Environment.firstTeamScore<Environment.secondTeamScore and " \
                     f"Environment.firstTeamScore+Environment.secondTeamScore={self._number_of_cards_in_hand};\n" \
                     f"end Evaluation\n\n"
        return evaulation

    def _create_init_states(self) -> str:
        init_states = "InitStates\n"
        oponents_cards = []
        for k in range(self._number_of_cards_in_hand, self._number_of_cards_in_hand * 2):
            oponents_cards.append(self._card_ordering[k])

        for k in range(self._number_of_cards_in_hand * 3, self._number_of_cards_in_hand * 4):
            oponents_cards.append(self._card_ordering[k])

        oponents_cards.sort()
        number_of_beginning_states = 0

        for combination in itertools.combinations(oponents_cards, self._number_of_cards_in_hand):
            second_player_cards = combination
            fourth_player_cards = oponents_cards[:]
            for card in second_player_cards:
                fourth_player_cards.remove(card)

            new_card_ordering = self._card_ordering[:]
            i = 0
            for k in range(self._number_of_cards_in_hand, self._number_of_cards_in_hand * 2):
                new_card_ordering[k] = second_player_cards[i]
                i += 1

            i = 0
            for k in range(self._number_of_cards_in_hand * 3, self._number_of_cards_in_hand * 4):
                new_card_ordering[k] = fourth_player_cards[i]
                i += 1

            init_states += "\t(Environment.firstTeamScore=0 and Environment.secondTeamScore=0 and " \
                           "Environment.beginningPlayer=0 and Environment.currentPlayer=0 and " \
                           "Environment.clock=0 and Environment.SPlayerCard=None and " \
                           "Environment.WPlayerCard=None and Environment.NPlayerCard=None and " \
                           "Environment.EPlayerCard=None and Environment.suit=None"
            colors_count = {}
            i = 0
            for player in self.player_names:
                colors_count[player] = {}
                for color in self.card_colors:
                    colors_count[player][color] = 0
                for j in range(1, self._number_of_cards_in_hand + 1):
                    colors_count[player][self._cards_colors[self._cards[new_card_ordering[i]]]] += 1
                    i += 1
            i = 0
            for player in self.player_names:
                for color in self.card_colors:
                    if player != "NPlayer" and player != 'SPlayer':
                        init_states += f" and {player}.has{color}={colors_count[player][color]}"

            for player in self.player_names:
                for j in range(1, self._number_of_cards_in_hand + 1):
                    if player == "NPlayer":
                        init_states += f" and Environment.cardN{j}={self._cards[new_card_ordering[i]]}" \
                                       f" and Environment.currentCardN{j}={self._cards[new_card_ordering[i]]}"
                    else:
                        init_states += f" and {player}.card{j}={self._cards[new_card_ordering[i]]}"
                    i += 1

            for j in range(0, self._number_of_cards * 4):
                init_states += f" and Environment.{self._cards[j]}H=false"

            init_states += ") or\n"
            number_of_beginning_states += 1

        init_states = init_states.rstrip("\nro ")
        init_states += ";\nend InitStates\n\n"
        return init_states

    def _create_groups(self) -> str:
        groups = "Groups\n"
        groups += "\tg1={SPlayer};\n"
        groups += "end Groups\n\n"
        return groups

    def _create_formulae(self) -> str:
        formulae = "Formulae\n"
        formulae += "\t<g1>F FirstTeamWin;\n"
        formulae += "end Formulae\n\n"
        return formulae


if __name__ == "__main__":
    n = 2
    ispl_generator = BridgeModelIsplGenerator(n, n)
    model_txt = ispl_generator.create_model()
    file = open("bridge.ispl", "w")
    file.write(model_txt)
    file.close()