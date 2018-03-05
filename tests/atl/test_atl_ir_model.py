import unittest
from atl.atl_ir_model import *


class TestATLIrModel(unittest.TestCase):
    atl_Ir_model = None

    def setUp(self):
        self.create_test_model()

    def create_test_model(self):
        self.atl_Ir_model = ATLIrModel(number_of_agents=2)
        self.atl_Ir_model.add_action(0, 'Wait')
        self.atl_Ir_model.add_action(0, 'Push')
        self.atl_Ir_model.add_action(1, 'Wait')
        self.atl_Ir_model.add_action(1, 'Push')
        self.atl_Ir_model.add_transition(0, 1, ['Push', 'Wait'])
        self.atl_Ir_model.add_transition(0, 2, ['Wait', 'Push'])
        self.atl_Ir_model.add_transition(1, 2, ['Push', 'Wait'])
        self.atl_Ir_model.add_transition(1, 0, ['Wait', 'Push'])
        self.atl_Ir_model.add_transition(2, 0, ['Push', 'Wait'])
        self.atl_Ir_model.add_transition(2, 1, ['Wait', 'Push'])
        self.atl_Ir_model.add_transition(0, 0, ['Wait', 'Wait'])
        self.atl_Ir_model.add_transition(1, 1, ['Wait', 'Wait'])
        self.atl_Ir_model.add_transition(2, 2, ['Wait', 'Wait'])
        self.atl_Ir_model.add_transition(0, 0, ['Push', 'Push'])
        self.atl_Ir_model.add_transition(1, 1, ['Push', 'Push'])
        self.atl_Ir_model.add_transition(2, 2, ['Push', 'Push'])

    def test_minimum_formula_one_agent(self):
        result = self.atl_Ir_model.minimum_formula_one_agent(0, {1})
        self.assertEqual(len(result), 1)

    def test_minimum_formula_many_agents(self):
        result = self.atl_Ir_model.minimum_formula_many_agents([0, 1], {1})
        self.assertEqual(len(result), 3)

    def test_minimum_formula_no_agents(self):
        result = self.atl_Ir_model.minimum_formula_no_agents({1})
        self.assertEqual(len(result), 1)


class TestATLirModel(unittest.TestCase):
    atl_ir_model = None

    def setUp(self):
        self.create_test_model()

    def create_test_model(self):
        self.atl_ir_model = ATLirModel(number_of_agents=2)
        self.atl_ir_model.add_action(0, 'Wait')
        self.atl_ir_model.add_action(0, 'Push')
        self.atl_ir_model.add_action(1, 'Wait')
        self.atl_ir_model.add_action(1, 'Push')
        self.atl_ir_model.add_transition(0, 1, ['Push', 'Wait'])
        self.atl_ir_model.add_transition(0, 2, ['Wait', 'Push'])
        self.atl_ir_model.add_transition(1, 2, ['Push', 'Wait'])
        self.atl_ir_model.add_transition(1, 0, ['Wait', 'Push'])
        self.atl_ir_model.add_transition(2, 0, ['Push', 'Wait'])
        self.atl_ir_model.add_transition(2, 1, ['Wait', 'Push'])
        self.atl_ir_model.add_transition(0, 0, ['Wait', 'Wait'])
        self.atl_ir_model.add_transition(1, 1, ['Wait', 'Wait'])
        self.atl_ir_model.add_transition(2, 2, ['Wait', 'Wait'])
        self.atl_ir_model.add_transition(0, 0, ['Push', 'Push'])
        self.atl_ir_model.add_transition(1, 1, ['Push', 'Push'])
        self.atl_ir_model.add_transition(2, 2, ['Push', 'Push'])
        self.atl_ir_model.finish_model()
        self.atl_ir_model.add_epistemic_class(agent_number=0, epistemic_class={0, 1})
        self.atl_ir_model.add_epistemic_class(agent_number=1, epistemic_class={0, 2})

    def test_minimum_formula_one_agent(self):
        result = self.atl_ir_model.minimum_formula_one_agent(0, {2})
        self.assertEqual(len(result), 1)


if __name__ == '__main__':
    unittest.main()