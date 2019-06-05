from generators.ispl.castles import CastlesIsplGenerator, CastlesIsplGeneratorSubjective
from generators.ispl.bridge import BridgeModelIsplGenerator, AbsentMindedBridgeModelIsplGenerator
from generators.ispl.selene import SeleneModelIsplGenerator, SeleneModelMkIsplGenerator


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
            option = self.show_main_menu()

    def show_main_menu(self) -> int:
        print("0 - Exit\n"
              "1 - ISPL generators")
        option = int(input("Choose option:"))
        while option > 1 or option < 0:
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
                print("Not implemented")
                pass
            elif option == 2:
                print("Not implemented")
                pass
            option = self.show_ispl_castles_menu()

    def show_ispl_castles_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Objective\n"
              "2 - Subjective")

        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

    def handle_ispl_bridge_menu(self):
        option = self.show_ispl_bridge_menu()
        while option != 0:
            if option == 1:
                print("Not implemented")
                pass
            elif option == 2:
                print("Not implemented")
                pass
            option = self.show_ispl_bridge_menu()

    def show_ispl_bridge_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Standard\n"
              "2 - Absent minded declarer")

        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

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
                print("Not implemented")
                pass
            elif option == 2:
                print("Not implemented")
                pass
            option = self.show_ispl_simple_voting_menu()

    def show_ispl_simple_voting_menu(self) -> int:
        print("0 - Exit to previous menu\n"
              "1 - Standard\n"
              "2 - Modified")

        option = int(input("Choose option:"))
        while option > 2 or option < 0:
            option = int(input("Invalid oprion. Please, choose again:"))

        return option

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


menu = Menu()
menu.start()
