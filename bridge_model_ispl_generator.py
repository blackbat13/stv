import itertools
import random


class BridgeModelIsplGenerator:
    card_names = ["As", "Krol", "Dama", "Walet", "ten", "nine", "eight", "seven", "six", "five", "four", "three", "two"]
    card_colors = ["Pik", "Trefl", "Kier", "Karo"]
    player_names = ["FirstPlayer", "SecondPlayer", "ThirdPlayer", "FourthPlayer"]
    ispl_model = ""
    cards = []
    available_cards = []
    cards_values = {}
    cards_colors = {}
    cards_colors_values = {}

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
            k = 1
            for color in self.card_colors:
                self.cards_colors[self.cards[i]] = color
                self.cards_colors_values[self.cards[i]] = k
                i += 1
                k += 1

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
        # environment += self.__create_environment_vars()
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

        for i in range(1, self.number_of_cards_in_hand + 1):
            obsvars += "\t\tu_card" + str(i) + ": {"
            for j in range(0, 4 * self.number_of_cards):
                obsvars += self.cards[j] + ", "
            obsvars += "None};\n"

        obsvars += "\tend Obsvars\n"
        return obsvars

    def __create_environment_vars(self):
        vars = "\tVars:\n"
        for i in range(1, self.number_of_cards_in_hand * 2 + 1):
            vars += "\t\thascard" + str(i) + "={"
            for card in self.available_cards:
                vars += card + ", "
            vars += "None};\n"
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

        for winning_player in range(0, 4):
            if winning_player % 2 == 0:
                evolution += "\t\tfirstTeamScore=firstTeamScore+1"
            else:
                evolution += "\t\tsecondTeamScore=secondTeamScore+1"
            evolution += " and beginningPlayer=" + str(winning_player) + " if\n"

            beginning_player_number = 0
            for beginning_player in self.player_names:
                evolution += "\t\t\t("
                for player in self.player_names:
                    if player == self.player_names[winning_player]:
                        continue
                    evolution += ""
                    evolution += "(" + player + ".playedCard % 10 != " + self.player_names[
                        winning_player] + ".playedCard % 10 or " + player + ".playedCard < " + self.player_names[
                                     winning_player] + ".playedCard"
                    evolution += ") and "
                evolution += "beginningPlayer=" + str(
                    beginning_player_number) + " and " + beginning_player + ".playedCard % 10 = " + self.player_names[
                                 winning_player] + ".playedCard % 10"

                if beginning_player_number != 3:
                    evolution += ") or\n"
                else:
                    evolution += ");\n"
                beginning_player_number += 1

        evolution += "\tend Evolution\n"
        return evolution

    def __create_player(self, player_name):
        player = "Agent " + player_name + "\n"
        # if player_name != "ThirdPlayer":
        #     player += self.__create_player_lobsvars()
        if player_name == "ThirdPlayerkk":
            player += self.__create_second_player_vars()
            player += self.__create_player_actions()
            player += self.__create_second_player_protocol()
            player += self.__create_second_player_evolution()
        else:
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
            vars += "\t\tcard" + str(i) + ": 0..140;\n"

        vars += "\t\tplayedCard: 0..140;\n"
        vars += "\tend Vars\n"
        return vars

    def __create_second_player_vars(self):
        vars = "\tVars:\n"
        vars += "\t\tc: {None};\n"
        vars += "\tend Vars\n"
        return vars

    def __create_player_actions(self):
        actions = "\tActions = {"
        for i in range(1, self.number_of_cards_in_hand):
            actions += "PlayCard" + str(i) + ", "

        actions += "Wait};\n"
        return actions

    def __create_player_protocol(self):
        protocol = "\tProtocol:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            protocol += "\t\tcard" + str(i) + "!= 0"
            protocol += ": {PlayCard" + str(i) + "};\n"

        protocol += "\tend Protocol\n"
        return protocol

    def __create_second_player_protocol(self):
        protocol = "\tProtocol:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            for j in range(0, 4 * self.number_of_cards):
                protocol += "\t\tEnvironment.u_card" + str(i) + "="
                protocol += self.cards[j] + ": {Play" + self.cards[j] + "};\n"
                # protocol += "\t\tcard" + str(i) + "=None: {Wait};\n"

        protocol += "\tend Protocol\n"
        return protocol

    def __create_player_evolution(self):
        evolution = "\tEvolution:\n"
        for i in range(1, self.number_of_cards_in_hand + 1):
            evolution += "\t\tplayedCard=" + "card" + str(i) + " and " + "card" + str(i) + "=0 if card" + str(i)
            evolution += "!= 0 and Action=PlayCard" + str(i) + ";\n"

        evolution += "\tend Evolution\n"
        return evolution

    def __create_second_player_evolution(self):
        evolution = "\tEvolution:\n"
        evolution += "\t\tc=None if c=None;\n"
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

            i = 0
            init_states += "\t(Environment.firstTeamScore=0 and Environment.secondTeamScore=0 and Environment.beginningPlayer=0"
            for player in self.player_names:
                for j in range(1, self.number_of_cards_in_hand + 1):
                    if player == "ThirdPlayer":
                        init_states += " and Environment.u_card" + str(j) + "=" + str(
                            self.__card_number(self.cards[new_card_ordering[i]]))
                    else:
                        init_states += " and " + player + ".card" + str(j) + "=" + str(
                            self.__card_number(self.cards[new_card_ordering[i]]))
                    i += 1

            init_states += ") or\n"

        init_states = init_states.rstrip("\nro ")
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
        # formulae += "\t<g1>G FirstTeamWin;\n"
        formulae += "end Formulae\n\n"
        return formulae

    def __card_number(self, card):
        return self.cards_values[card] * 10 + self.cards_colors_values[card]


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


n = 1
bridge_model_ispl_generator = BridgeModelIsplGenerator(n, n, generate_random_array(n * 4))
# bridge_model_ispl_generator = BridgeModelIsplGenerator(4, 2, [4, 8, 0, 12, 13, 14, 1, 5])
f = open("bridge_" + str(n) + "_" + str(n) + ".ispl", "w")
f.write(bridge_model_ispl_generator.create_ispl_model())
f.close()
