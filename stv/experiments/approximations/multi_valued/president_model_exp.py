from stv.logics.atl.mv import mvatl_parser
from stv.models.mv import PresidentModel
import time


class PresidentModelExp:
    def __init__(self, number_of_players: int, number_of_decks: int, number_of_cards: int):
        self.number_of_players = number_of_players
        self.number_of_decks = number_of_decks
        self.number_of_cards = number_of_cards

    def run_experiments(self):
        start = time.clock()
        test = PresidentModel(self.number_of_players, self.number_of_decks, self.number_of_cards)
        test.create_mvatl_model()
        # cards = {0: {'Two': 0, 'As': 0, 'King': 0, 'Queen': 2, 'Jack': 0, 'Ten': 2, 'Nine': 0, 'Eight': 0, 'Seven': 0, 'Six': 0, 'Five': 1, 'Four': 0, 'Three': 0}, 1: {'Two': 0, 'As': 0, 'King': 0, 'Queen': 2, 'Jack': 0, 'Ten': 0, 'Nine': 0, 'Eight': 0, 'Seven': 0, 'Six': 2, 'Five': 0, 'Four': 1, 'Three': 0}, 2: {'Two': 1, 'As': 2, 'King': 0, 'Queen': 0, 'Jack': 0, 'Ten': 0, 'Nine': 0, 'Eight': 2, 'Seven': 0, 'Six': 0, 'Five': 0, 'Four': 0, 'Three': 0}, 3: {'Two': 2, 'As': 0, 'King': 0, 'Queen': 0, 'Jack': 0, 'Ten': 0, 'Nine': 0, 'Eight': 0, 'Seven': 0, 'Six': 1, 'Five': 0, 'Four': 2, 'Three': 0}}
        # test.players_cards = cards
        test.generate_model()
        end = time.clock()
        print("Gen:", end - start, "s")
        print(f'Number of states: {len(test.states)}')
        test.model.states = test.states

        start = time.clock()
        props = "Hierarchy"
        test.model.props = [props]
        const = "b n t"
        atlparser = mvatl_parser.AlternatingTimeTemporalLogicParser(const, props)
        txt = "<<1>> F (t <= Hierarchy_1)"
        print("Formula : " + atlparser.parse(txt))
        print(str(test.model.interpreter(atlparser.parse(txt), 0)))
        end = time.clock()
        print("Verif:", end - start, "s")


if __name__ == "__main__":
    president_model_exp = PresidentModelExp(5, 1, 5)
    president_model_exp.run_experiments()
