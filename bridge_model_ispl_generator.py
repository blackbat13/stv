import itertools
import random


class BridgeModelIsplGenerator:
    card_names = ["As", "Krol", "Dama", "Walet", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
    card_colors = ["Pik", "Trefl", "Kier", "Karo"]
    player_names = ["FirstPlayer", "SecondPlayer", "ThirdPlayer", "FourthPlayer"]
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
        self.ispl_model += self.__create_environment()
        for player_name in self.player_names:
            self.ispl_model += self.__create_player(player_name)

        self.ispl_model += self.__create_evaluation()
        self.ispl_model += self.__create_init_states()
        self.ispl_model += self.__create_groups()
        self.ispl_model += self.__create_formulae()
        return self.ispl_model

    def __create_environment(self):
        environment = "Agent Environment\n"
        environment += self.__create_environment_obsvars()
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
        obsvars += "\tend Obsvars\n"
        return obsvars

    def __create_environment_actions(self):
        actions = "\tActions = {none};\n"
        return actions

    def __create_environment_protocol(self):
        protocol = "\tProtocol:\n\t\tOther:{none};\n\tend Protocol\n"
        return protocol

    def __create_environment_evolution(self):
        evolution = "\tEvolution:\n"

        evolution += "\tfirstTeamScore=firstTeamScore+1 and beginningPlayer=0 if\n"
        add_or = False

        for combination in itertools.combinations(self.available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self.cards_colors[combination[i]] == self.cards_colors[combination[winning_player_number]]:
                        if self.cards_values[combination[i]] > self.cards_values[combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 0):
                    continue

                if add_or:
                    evolution += " or\n"
                else:
                    add_or = True

                evolution += "\t\t("
                for player in range(0, 4):
                    evolution += self.player_names[player] + ".Action=Play" + combination[player] + " and "

                evolution += "beginningPlayer=" + str(beginning_player) + ")"

        evolution += ";\n"

        evolution += "\tfirstTeamScore=firstTeamScore+1 and beginningPlayer=2 if\n"
        add_or = False

        for combination in itertools.combinations(self.available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self.cards_colors[combination[i]] == self.cards_colors[combination[winning_player_number]]:
                        if self.cards_values[combination[i]] > self.cards_values[combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 2):
                    continue

                if add_or:
                    evolution += " or\n"
                else:
                    add_or = True

                evolution += "\t\t("
                for player in range(0, 4):
                    evolution += self.player_names[player] + ".Action=Play" + combination[player] + " and "

                evolution += "beginningPlayer=" + str(beginning_player) + ")"

        evolution += ";\n"

        evolution += "\tsecondTeamScore=secondTeamScore+1 and beginningPlayer=1 if\n"

        add_or = False

        for combination in itertools.combinations(self.available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self.cards_colors[combination[i]] == self.cards_colors[combination[winning_player_number]]:
                        if self.cards_values[combination[i]] > self.cards_values[combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 1):
                    continue

                if add_or:
                    evolution += " or\n"
                else:
                    add_or = True

                evolution += "\t\t("
                for player in range(0, 4):
                    evolution += self.player_names[player] + ".Action=Play" + combination[player] + " and "

                evolution += "beginningPlayer=" + str(beginning_player) + ")"

        evolution += ";\n"

        evolution += "\tsecondTeamScore=secondTeamScore+1 and beginningPlayer=3 if\n"

        add_or = False

        for combination in itertools.combinations(self.available_cards, 4):
            for beginning_player in range(0, 4):
                winning_player_number = beginning_player
                for i in range(0, 4):
                    if i == beginning_player:
                        continue

                    if self.cards_colors[combination[i]] == self.cards_colors[combination[winning_player_number]]:
                        if self.cards_values[combination[i]] > self.cards_values[combination[winning_player_number]]:
                            winning_player_number = i

                if not (winning_player_number == 3):
                    continue

                if add_or:
                    evolution += " or\n"
                else:
                    add_or = True

                evolution += "\t\t("
                for player in range(0, 4):
                    evolution += self.player_names[player] + ".Action=Play" + combination[player] + " and "

                evolution += "beginningPlayer=" + str(beginning_player) + ")"

        evolution += ";\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_player(self, player_name):
        player = "Agent " + player_name + "\n"
        # if player_name != "ThirdPlayer":
        #     player += self.__create_player_lobsvars()

        player += self.__create_player_vars()
        player += self.__create_player_actions()
        player += self.__create_player_protocol()
        player += self.__create_player_evolution()
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

    def __create_player_vars(self):
        vars = "\tVars:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            vars += "\t\tcard" + str(i) + ": {"
            for j in range(0, 4 * self.number_of_cards):
                vars += self.cards[j] + ", "
            vars += "None};\n"

        vars += "\tend Vars\n"
        return vars

    def __create_player_actions(self):
        actions = "\tActions = {"
        for i in range(0, 4 * self.number_of_cards):
            actions += "Play" + self.cards[i] + ", "

        actions += "Wait};\n"
        return actions

    def __create_player_protocol(self):
        protocol = "\tProtocol:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            for j in range(0, 4 * self.number_of_cards):
                protocol += "\t\tcard" + str(i) + "="
                protocol += self.cards[j] + ": {Play" + self.cards[j] + "};\n"
            protocol += "\t\tcard" + str(i) + "=None: {Wait};\n"

        protocol += "\tend Protocol\n"
        return protocol

    def __create_player_evolution(self):
        evolution = "\tEvolution:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            for j in range(0, 4 * self.number_of_cards):
                evolution += "\t\tcard" + str(i) + "=None if card" + str(i)
                evolution += "=" + self.cards[j] + " and Action=Play" + self.cards[j] + ";\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_evaluation(self):
        evaulation = "Evaluation\n"
        evaulation += "\tFirstTeamWin if Environment.firstTeamScore>Environment.secondTeamScore and Environment.firstTeamScore+Environment.secondTeamScore=" + str(self.number_of_cards_in_hand) +";\n"
        evaulation += "\tSecondTeamWin if Environment.firstTeamScore<Environment.secondTeamScore and Environment.firstTeamScore+Environment.secondTeamScore=" + str(self.number_of_cards_in_hand) +";\n"
        evaulation += "end Evaluation\n\n"
        return evaulation

    def __create_init_states(self):
        init_states = "InitStates\n"
        init_states += "\tEnvironment.firstTeamScore=0 and Environment.secondTeamScore=0 and Environment.beginningPlayer=0"
        i = 0
        for player in self.player_names:
            for j in range(1, self.number_of_cards_in_hand+1):
                init_states += " and " + player + ".card" + str(j) + "=" + self.cards[i]
                i += 1

        init_states += ";\nend InitStates\n\n"
        return init_states

    def __create_groups(self):
        groups = "Groups\n"
        groups += "\tg1={FirstPlayer, ThirdPlayer};\n"
        groups += "end Groups\n\n"
        return groups

    def __create_formulae(self):
        formulae = "Formulae\n"
        formulae += "\t<g1>F FirstTeamWin;\n"
        formulae += "\t<g1>G FirstTeamWin;\n"
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

bridge_model_ispl_generator = BridgeModelIsplGenerator(1, 1, generate_random_array(4))
f = open("output", "w")
f.write(bridge_model_ispl_generator.create_ispl_model())
f.close()
