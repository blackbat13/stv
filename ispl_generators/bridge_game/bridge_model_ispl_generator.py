import itertools
import random


class BridgeModelIsplGenerator:
    card_names = ["Ace", "King", "Queen", "Jack", "ten", "nine", "eight", "seven", "six", "five", "four", "three",
                  "two"]
    card_colors = ["Spade", "Heart", "Diamond", "Club"]
    player_names = ["SPlayer", "WPlayer", "NPlayer", "EPlayer"]
    ispl_model = ""
    cards = []
    available_cards = []
    cards_values = {}
    cards_colors = {}

    def __init__(self, number_of_cards, number_of_cards_in_hand, card_ordering):
        self.number_of_cards = number_of_cards
        self.number_of_cards_in_hand = number_of_cards_in_hand
        self.card_ordering = card_ordering
        self.__create_cards_array()
        self.__create_available_cards_array()
        self.__assign_cards_values()
        self.__assign_cards_colors()

    def __create_cards_array(self):
        self.cards = []
        for card_name in self.card_names:
            for card_color in self.card_colors:
                self.cards.append(card_name + card_color)

    def __create_available_cards_array(self):
        self.available_cards = []
        for j in range(0, 4 * self.number_of_cards):
            self.available_cards.append(self.cards[j])

    def __assign_cards_values(self):
        i = 0
        for card_value in range(0, 13):
            for j in range(0, 4):
                self.cards_values[self.cards[i]] = 13 - card_value
                i += 1

    def __assign_cards_colors(self):
        i = 0
        for _ in range(0, 13):
            for color in self.card_colors:
                self.cards_colors[self.cards[i]] = color
                i += 1

    def create_ispl_model(self):
        self.ispl_model += self.__define_semantics()
        self.ispl_model += self.__create_environment()
        self.ispl_model += self.__create_player(0)
        self.ispl_model += self.__create_player(1)
        self.ispl_model += self.__create_player(3)

        self.ispl_model += self.__create_evaluation()
        self.ispl_model += self.__create_init_states()
        self.ispl_model += self.__create_groups()
        self.ispl_model += self.__create_formulae()
        return self.ispl_model

    def __define_semantics(self):
        semantics = "Semantics=SingleAssignment;\n\n"
        return semantics

    def __create_environment(self):
        environment = "Agent Environment\n"
        environment += self.__create_environment_obsvars()
        environment += self.__create_environment_vars()
        environment += self.__create_environment_actions()
        environment += self.__create_environment_protocol()
        environment += self.__create_environment_evolution()
        environment += "end Agent\n\n"
        return environment

    def __create_environment_obsvars(self):
        obsvars = "\tObsvars:\n"
        obsvars += "\t\tfirstTeamScore: 0.." + str(self.number_of_cards_in_hand) + ";\n"
        obsvars += "\t\tsecondTeamScore: 0.." + str(self.number_of_cards_in_hand) + ";\n"
        obsvars += "\t\tbeginningPlayer: 0..3;\n"
        obsvars += "\t\tcurrentPlayer: 0..4;\n"
        obsvars += "\t\tclock: 0..4;\n"

        for player in self.player_names:
            obsvars += f"\t\t{player}Card: " + "{"
            for j in range(0, 4 * self.number_of_cards):
                obsvars += f"{self.cards[j]}, "
            obsvars += "None};\n"

        for i in range(1, self.number_of_cards_in_hand + 1):
            obsvars += "\t\tcardN" + str(i) + ": {"
            for j in range(0, 4 * self.number_of_cards):
                obsvars += f"N{self.cards[j]}, "
            obsvars += "None};\n"

        for i in range(0, self.number_of_cards * 4):
            obsvars += "\t\t" + self.cards[i] + "H: boolean;\n"

        obsvars += "\t\tsuit: {Spade, Heart, Diamond, Club, None};\n"

        for color in self.card_colors:
            obsvars += "\t\thas" + color + ": 0.." + str(self.number_of_cards_in_hand) + ";\n"

        obsvars += "\tend Obsvars\n"
        return obsvars

    def __create_environment_vars(self):
        vars = "\tVars:\n"
        vars += "\t\tsmc: 0..1;\n"
        vars += "\tend Vars\n"
        return vars

    def __create_environment_actions(self):
        actions = "\tActions = {none};\n"
        return actions

    def __create_environment_protocol(self):
        protocol = "\tProtocol:\n\t\tOther:{none};\n\tend Protocol\n"
        return protocol

    def __create_environment_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\t\tfirstTeamScore=firstTeamScore+1 if\n"
        for combination in itertools.permutations(self.available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self.cards_colors[combination[i]] == self.cards_colors[
                        combination[winning_player_number]]:
                        if self.cards_values[combination[i]] > self.cards_values[
                            combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 0 or winning_player_number == 2):
                    continue

                evolution += "\t\t\t(\n"
                for player in range(0, 4):
                    evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"

                evolution += f"\t\t\t\tbeginningPlayer={beginning_player})"
                evolution += " or\n"

        evolution = evolution.rstrip("\nro ")
        evolution += ";\n"

        evolution += "\t\tsecondTeamScore=secondTeamScore+1 if\n"
        for combination in itertools.permutations(self.available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self.cards_colors[combination[i]] == self.cards_colors[
                        combination[winning_player_number]]:
                        if self.cards_values[combination[i]] > self.cards_values[
                            combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 1 or winning_player_number == 3):
                    continue

                evolution += "\t\t\t(\n"
                for player in range(0, 4):
                    evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"

                evolution += f"\t\t\t\tbeginningPlayer={beginning_player})"
                evolution += " or\n"

        evolution = evolution.rstrip("\nro ")
        evolution += ";\n"

        for winning_player in range(0, 4):
            evolution += f"\t\tbeginningPlayer={winning_player} if\n"
            for combination in itertools.permutations(self.available_cards, 4):
                for beginning_player in range(0, 4):
                    winning_player_number = beginning_player
                    for i in range(0, 4):
                        if i == beginning_player:
                            continue

                        if self.cards_colors[combination[i]] == self.cards_colors[
                            combination[winning_player_number]]:
                            if self.cards_values[combination[i]] > self.cards_values[
                                combination[winning_player_number]]:
                                winning_player_number = i

                    if not (winning_player_number == winning_player):
                        continue

                    evolution += "\t\t\t(\n"
                    for player in range(0, 4):
                        evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"

                    evolution += f"\t\t\t\tbeginningPlayer={beginning_player})"
                    evolution += " or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for winning_player in range(0, 4):
            evolution += f"\t\tcurrentPlayer={winning_player} if\n"
            for combination in itertools.permutations(self.available_cards, 4):
                for beginning_player in range(0, 4):
                    winning_player_number = beginning_player
                    for i in range(0, 4):
                        if i == beginning_player:
                            continue

                        if self.cards_colors[combination[i]] == self.cards_colors[
                            combination[winning_player_number]]:
                            if self.cards_values[combination[i]] > self.cards_values[
                                combination[winning_player_number]]:
                                winning_player_number = i

                    if not (winning_player_number == winning_player):
                        continue

                    evolution += "\t\t\t(\n"
                    for player in range(0, 4):
                        evolution += f"\t\t\t\t{self.player_names[player]}Card={combination[player]} and\n"

                    evolution += f"\t\t\t\tbeginningPlayer={beginning_player})"
                    evolution += " or\n"

            previousPlayer = winning_player - 1
            if previousPlayer == -1:
                previousPlayer = 3
            evolution += f"\t\t\t(currentPlayer={previousPlayer} and clock<4)"
            evolution += ";\n"

        evolution += "\t\tsuit=None if clock=4;\n"
        evolution += "\t\tclock=0 if clock=4;\n"
        for clock in range(1, 5):
            evolution += f"\t\tclock={clock} if clock={clock - 1};\n"

        for player in self.player_names:
            evolution += f"\t\t{player}Card=None if clock=4;\n"

        for i in range(0, self.number_of_cards * 4):
            card = self.cards[i]
            for player_number in range(0, 4):
                player = self.player_names[player_number]
                if player == self.player_names[2]:
                    evolution += f"\t\t{player}Card={card} if {self.player_names[0]}.Action=Play{card} and currentPlayer=2;\n"
                else:
                    evolution += f"\t\t{player}Card={card} if {player}.Action=Play{card} and currentPlayer={player_number};\n"

        for color in self.card_colors:
            evolution += f"\t\tsuit={color} if clock=0 and (\n"
            for i in range(0, self.number_of_cards * 4):
                card = self.cards[i]
                if self.cards_colors[card] != color:
                    continue
                for player in self.player_names:
                    if player == self.player_names[2]:
                        continue
                    evolution += f"\t\t\t{player}.Action=Play{card} or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        for i in range(0, self.number_of_cards * 4):
            card = self.cards[i]
            evolution += f"\t\t{card}H=true if\n"
            for player in self.player_names:
                if player == self.player_names[2]:
                    continue
                evolution += f"\t\t\t{player}.Action=Play{card} or\n"
            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for i in range(0, self.number_of_cards * 4):
            card = self.cards[i]
            for j in range(1, self.number_of_cards_in_hand + 1):
                evolution += f"\t\tcardN{j}=None if {self.player_names[0]}.Action=Play{card} and cardN{j}=N{card};\n"

        for color in self.card_colors:
            evolution += f"\t\thas{color}=has{color}+-1 if (\n"
            for i in range(0, self.number_of_cards * 4):
                card = self.cards[i]
                if self.cards_colors[card] != color:
                    continue
                evolution += f"\t\t\t({self.player_names[0]}.Action=Play{card} and ("
                for j in range(1, self.number_of_cards_in_hand + 1):
                    evolution += f"cardN{j}=N{card} or "
                evolution = evolution.rstrip(" ro ")
                evolution += ")) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ");\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_player(self, player_number):
        player = "Agent " + self.player_names[player_number] + "\n"
        # if player_name != "ThirdPlayer":
        #     player += self.__create_player_lobsvars()

        player += self.__create_player_vars(player_number)
        player += self.__create_player_actions()
        player += self.__create_player_protocol(player_number)
        player += self.__create_player_evolution(player_number)
        player += "end Agent\n\n"
        return player

    def __create_player_lobsvars(self):
        lobsvars = "\tLobsvars = {"
        for i in range(1, self.number_of_cards_in_hand + 1):
            lobsvars += "ThirdPlayer.card" + str(i)
            if i != self.number_of_cards_in_hand:
                lobsvars += ", "

        lobsvars += "};\n"
        return lobsvars

    def __create_player_vars(self, player_number):
        vars = "\tVars:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            vars += f"\t\t{self.player_names[player_number][0]}card" + str(i) + ": {"
            for j in range(0, 4 * self.number_of_cards):
                vars += f"{self.player_names[player_number][0]}{self.cards[j]}, "
            vars += "None};\n"

        for color in self.card_colors:
            vars += "\t\thas" + color + ": 0.." + str(self.number_of_cards_in_hand) + ";\n"

        vars += "\tend Vars\n"
        return vars

    def __create_player_actions(self):
        actions = "\tActions = {"
        for i in range(0, 4 * self.number_of_cards):
            actions += "Play" + self.cards[i] + ", "

        actions += "Wait};\n"
        return actions

    def __create_player_protocol(self, player_number):
        protocol = "\tProtocol:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            for j in range(0, 4 * self.number_of_cards):
                protocol += f"\t\t{self.player_names[player_number][0]}card{i}={self.player_names[player_number][0]}{self.cards[j]} and Environment.currentPlayer={player_number} and Environment.clock<4 and (Environment.suit=None or Environment.suit={self.cards_colors[self.cards[j]]} or ((hasSpade<=0 and Environment.suit=Spade) or (hasClub<=0 and Environment.suit=Club) or (hasDiamond<=0 and Environment.suit=Diamond) or (hasHeart<=0 and Environment.suit=Heart))): " + "{Play" + \
                            self.cards[j] + "};\n"

        if player_number == 0:
            for i in range(1, self.number_of_cards_in_hand + 1):
                for j in range(0, 4 * self.number_of_cards):
                    protocol += "\t\tEnvironment.cardN" + str(i) + "=N"
                    protocol += self.cards[
                                    j] + " and Environment.currentPlayer=2 and Environment.clock<4 and (Environment.suit=None or Environment.suit=" + \
                                self.cards_colors[self.cards[
                                    j]] + " or ((Environment.hasSpade<=0 and Environment.suit=Spade) or (Environment.hasClub<=0 and Environment.suit=Club) or (Environment.hasDiamond<=0 and Environment.suit=Diamond) or (Environment.hasHeart<=0 and Environment.suit=Heart))): {Play" + \
                                self.cards[j] + "};\n"

        if player_number != 0:
            protocol += f"\t\t!(Environment.currentPlayer={player_number}) or Environment.clock=4: " + "{Wait};\n"
        else:
            protocol += f"\t\t(!(Environment.currentPlayer={player_number}) and !(Environment.currentPlayer=2)) or Environment.clock=4: " + "{Wait};\n"
        protocol += "\tend Protocol\n"
        return protocol

    def __create_player_evolution(self, player_number):
        evolution = "\tEvolution:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            evolution += f"\t\t{self.player_names[player_number][0]}card{i}=None if\n"
            for j in range(0, 4 * self.number_of_cards):
                card = self.cards[j]
                evolution += f"\t\t\t({self.player_names[player_number][0]}card{i}={self.player_names[player_number][0]}{card} and Action=Play{card}) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        for color in self.card_colors:
            evolution += f"\t\thas{color}=has{color}+-1 if\n"
            for i in range(1, self.number_of_cards_in_hand + 1):
                for j in range(0, 4 * self.number_of_cards):
                    card = self.cards[j]
                    if self.cards_colors[card] != color:
                        continue
                    evolution += f"\t\t\t({self.player_names[player_number][0]}card{i}={self.player_names[player_number][0]}{card} and Action=Play{card}) or\n"

            evolution = evolution.rstrip("\nro ")
            evolution += ";\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self):
        evaulation = "Evaluation\n"
        evaulation += "\tFirstTeamWin if Environment.firstTeamScore>Environment.secondTeamScore and Environment.firstTeamScore+Environment.secondTeamScore=" + str(
            self.number_of_cards_in_hand) + ";\n"
        evaulation += "\tSecondTeamWin if Environment.firstTeamScore<Environment.secondTeamScore and Environment.firstTeamScore+Environment.secondTeamScore=" + str(
            self.number_of_cards_in_hand) + ";\n"
        evaulation += "end Evaluation\n\n"
        return evaulation

    def __create_init_states(self):
        init_states = "InitStates\n"
        oponents_cards = []
        for k in range(self.number_of_cards_in_hand, self.number_of_cards_in_hand * 2):
            oponents_cards.append(self.card_ordering[k])

        for k in range(self.number_of_cards_in_hand * 3, self.number_of_cards_in_hand * 4):
            oponents_cards.append(self.card_ordering[k])

        oponents_cards.sort()
        number_of_beginning_states = 0

        for combination in itertools.combinations(oponents_cards, self.number_of_cards_in_hand):
            second_player_cards = combination
            fourth_player_cards = oponents_cards[:]
            for card in second_player_cards:
                fourth_player_cards.remove(card)

            new_card_ordering = self.card_ordering[:]
            i = 0
            for k in range(self.number_of_cards_in_hand, self.number_of_cards_in_hand * 2):
                new_card_ordering[k] = second_player_cards[i]
                i += 1

            i = 0
            for k in range(self.number_of_cards_in_hand * 3, self.number_of_cards_in_hand * 4):
                new_card_ordering[k] = fourth_player_cards[i]
                i += 1

            init_states += "\t(Environment.smc=0 and Environment.firstTeamScore=0 and Environment.secondTeamScore=0 and Environment.beginningPlayer=0 and Environment.currentPlayer=0 and Environment.clock=0 and Environment.SPlayerCard=None and Environment.WPlayerCard=None and Environment.NPlayerCard=None and Environment.EPlayerCard=None and Environment.suit=None"
            colors_count = {}
            i = 0
            for player in self.player_names:
                colors_count[player] = {}
                for color in self.card_colors:
                    colors_count[player][color] = 0
                for j in range(1, self.number_of_cards_in_hand + 1):
                    colors_count[player][self.cards_colors[self.cards[new_card_ordering[i]]]] += 1
                    i += 1
            i = 0
            for player in self.player_names:
                for color in self.card_colors:
                    if player == "NPlayer":
                        init_states += " and Environment.has" + color + "=" + str(colors_count[player][color])
                    else:
                        init_states += " and " + player + ".has" + color + "=" + str(colors_count[player][color])

            for player in self.player_names:
                for j in range(1, self.number_of_cards_in_hand + 1):
                    if player == "NPlayer":
                        init_states += " and Environment.cardN" + str(j) + "=N" + self.cards[new_card_ordering[i]]
                    else:
                        init_states += " and " + player + "." + player[0] + "card" + str(j) + "=" + player[0] + self.cards[new_card_ordering[i]]
                    i += 1

            for j in range(0, self.number_of_cards * 4):
                init_states += " and Environment." + self.cards[j] + "H=false"

            init_states += ") or\n"
            number_of_beginning_states += 1

        print("Number of beginning states:", number_of_beginning_states)
        init_states = init_states.rstrip("\nro ")
        init_states += ";\nend InitStates\n\n"
        return init_states

    def __create_groups(self):
        groups = "Groups\n"
        groups += "\tg1={SPlayer};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self):
        formulae = "Formulae\n"
        formulae += "\t<g1>F FirstTeamWin;\n"
        formulae += "end Formulae\n\n"
        return formulae


def generate_random_array(length):
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


n = int(input("Number of figures in game ="))
k = int(input("Number of cards in hand ="))

bridge_model_ispl_generator = BridgeModelIsplGenerator(n, k, generate_random_array(4 * n))

f = open("bridge_" + str(n) + "_" + str(k) + ".ispl", "w")
f.write(bridge_model_ispl_generator.create_ispl_model())
f.close()

print("Done. Created model saved in bridge_" + str(n) + "_" + str(k) + ".ispl")
