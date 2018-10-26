import itertools
import random
from tools.string_tools import StringTools


class PretAVoterSpthyGenerator:
    spthy_model = ""
    no_voters = 4
    no_candidates = 3

    def __init__(self):
        return

    def create_spthy_model(self):
        self.spthy_model += "theory PretAVoter\n"
        self.spthy_model += "begin\n"
        self.spthy_model += self.__define_builtins()
        self.spthy_model += self.__define_rules()

        self.spthy_model += "end\n"
        return self.spthy_model

    def __define_builtins(self):
        builtins = "builtins: "
        libraries = ['symmetric-encryption', 'asymmetric-encryption', 'hashing', 'signing', 'diffie-hellman']
        for lib in libraries:
            builtins += f'{lib}, '

        builtins = builtins.rstrip(' ,')
        builtins += '\n'
        return builtins

    def __define_rules(self):
        rules = ""

        rules += self.__define_rules()

        return rules

    def __define_setup_rules(self):
        setup = ""
        setup += self.__define_asymetric_key_setup()
        return setup

    def __define_asymetric_key_setup(self):
        rule = "rule AsymmetricKeySetup:\n"
        rule += '\t[\n'
        rule += '\t\tFr(~f)'
        rule += '\t]\n'
        rule += '  --[ AsymmetricKeySetup($A, pk(~f), sk(~f)) ]->\n'
        rule += '\t[\n'
        rule += '\t\t!Sk($A, sk(~f)),\n'
        rule += '\t\t!Pk($A, pk(~f))\n'
        rule += '\t]\n'
        rule += '\n'
        return rule

    def __define_generate_voters(self):
        rule = "rule GenerateVoters:"
        rule += '\t[\n'
        rule += '\t]\n'


pret_a_voter_spthy_generator = PretAVoterSpthyGenerator()
file_name = "pret_a_voter.spthy"
f = open(file_name, "w")
f.write(pret_a_voter_spthy_generator.create_spthy_model())
f.close()

print(f"Done. Created model saved in {file_name}")
