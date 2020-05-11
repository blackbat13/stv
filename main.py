from stv.generators.ispl import CastlesIsplGeneratorObjective, CastlesIsplGeneratorSubjective
from stv.generators.ispl import BridgeModelIsplGenerator, AbsentMindedBridgeModelIsplGenerator
from stv.generators.ispl import SimpleVotingModelIsplGenerator, SimpleVotingModel2IsplGenerator
from stv.tools import FileTools


class Menu:
    def __init__(self):
        pass

    def start(self):
        self.handle_main_menu()
        print("Goodbye")

    def handle_main_menu(self):
        option = self.show_main_menu()
        while option != 0:
            if option == 1:
                self.handle_ispl_generator_menu()
            elif option == 2:
                print("Not implemented")
                pass
            option = self.show_main_menu()

    def show_main_menu(self) -> int:
        print("0 - Exit\n"
              "1 - ISPL generators\n"
              "2 - Verification\n")
        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

    def handle_ispl_generator_menu(self):
        option = self.show_ispl_generator_menu()
        while option != 0:
            if option == 1:
                self.handle_ispl_castles_menu()
            elif option == 2:
                self.handle_ispl_bridge_menu()
            elif option == 3:
                self.handle_ispl_selene_menu()
            elif option == 4:
                self.handle_ispl_simple_voting_menu()
            elif option == 5:
                self.handle_ispl_tmn_menu()
            option = self.show_ispl_generator_menu()

    def show_ispl_generator_menu(self) -> int:
        print("0 - Exit to main menu\n"
              "1 - Castles model\n"
              "2 - Bridge endgame model\n"
              "3 - Selene protocol model\n"
              "4 - Simple Voting model\n"
              "5 - TMN protocol model")
        option = int(input("Choose option:"))
        while option > 5 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

    def handle_ispl_castles_menu(self):
        option = self.show_ispl_castles_menu()
        while option != 0:
            if option == 1:
                self.ispl_castles_objective()
            elif option == 2:
                self.ispl_castles_subjective()
            option = self.show_ispl_castles_menu()

    def show_ispl_castles_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Objective\n"
              "2 - Subjective")

        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

    def ispl_castles_objective(self) -> None:
        workers = [0, 0, 0]
        for i in range(0, len(workers)):
            workers[i] = int(input(f"Number of workers in Castle {i + 1}"))
        file_name = input("Enter output filename: ")
        castles = CastlesIsplGeneratorObjective(workers)
        file_name = FileTools.save_to_file(file_name, castles.create_model())
        print(f"Result written in the file {file_name}")

    def ispl_castles_subjective(self) -> None:
        workers = [0, 0, 0]
        for i in range(0, len(workers)):
            workers[i] = int(input(f"Number of workers in Castle {i + 1}"))
        file_name = input("Enter output filename: ")
        castles = CastlesIsplGeneratorSubjective(workers)
        file_name = FileTools.save_to_file(file_name, castles.create_model())
        print(f"Result written to the file {file_name}")

    def handle_ispl_bridge_menu(self):
        option = self.show_ispl_bridge_menu()
        while option != 0:
            if option == 1:
                self.ispl_bridge_standard()
            elif option == 2:
                self.ispl_bridge_absent_minded()
            option = self.show_ispl_bridge_menu()

    def show_ispl_bridge_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Standard\n"
              "2 - Absent minded declarer")

        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

    def ispl_bridge_standard(self):
        number_of_cards = int(input("Number of cards: "))
        number_of_cards_in_hand = int(input("Number of cards in hand: "))
        file_name = input("Enter output filename: ")
        bridge = BridgeModelIsplGenerator(number_of_cards, number_of_cards_in_hand)
        file_name = FileTools.save_to_file(file_name, bridge.create_model())
        print(f"Result written to the file {file_name}")

    def ispl_bridge_absent_minded(self):
        number_of_cards = int(input("Number of cards: "))
        number_of_cards_in_hand = int(input("Number of cards in hand: "))
        file_name = input("Enter output filename: ")
        bridge = AbsentMindedBridgeModelIsplGenerator(number_of_cards, number_of_cards_in_hand)
        file_name = FileTools.save_to_file(file_name, bridge.create_model())
        print(f"Result written to the file {file_name}")

    def handle_ispl_selene_menu(self):
        option = self.show_ispl_selene_menu()
        while option != 0:
            if option == 1:
                print("Not implemented")
                pass
            elif option == 2:
                print("Not implemented")
                pass
            option = self.show_ispl_selene_menu()

    def show_ispl_selene_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Damian's\n"
              "2 - Michal's")

        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

    def handle_ispl_simple_voting_menu(self):
        option = self.show_ispl_simple_voting_menu()
        while option != 0:
            if option == 1:
                self.ispl_simple_voting_standard()
            elif option == 2:
                self.ispl_simple_voting_modified()
            option = self.show_ispl_simple_voting_menu()

    def show_ispl_simple_voting_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Standard\n"
              "2 - Modified")

        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

    def ispl_simple_voting_standard(self):
        number_of_voters = int(input("Number of voters: "))
        number_of_candidates = int(input("Number of candidates: "))
        file_name = input("Enter output filename: ")
        simple_voting = SimpleVotingModelIsplGenerator(number_of_candidates, number_of_voters)
        file_name = FileTools.save_to_file(file_name, simple_voting.create_model())
        print(f"Result written to the file {file_name}")

    def ispl_simple_voting_modified(self):
        number_of_voters = int(input("Number of voters: "))
        number_of_candidates = int(input("Number of candidates: "))
        file_name = input("Enter output filename: ")
        simple_voting = SimpleVotingModel2IsplGenerator(number_of_candidates, number_of_voters)
        file_name = FileTools.save_to_file(file_name, simple_voting.create_model())
        print(f"Result written to the file {file_name}")

    def handle_ispl_tmn_menu(self):
        option = self.show_ispl_tmn_menu()
        while option != 0:
            if option == 1:
                print("Not implemented")
                pass
            elif option == 2:
                print("Not implemented")
                pass
            elif option == 3:
                print("Not implemented")
                pass
            option = self.show_ispl_tmn_menu()

    def show_ispl_tmn_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Standard\n"
              "2 - V2\n"
              "3 - Comp")

        option = int(input("Choose option:"))
        while option > 3 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option


if __name__ == "__main__":
    menu = Menu()
    menu.start()
