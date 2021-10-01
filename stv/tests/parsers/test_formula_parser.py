from stv.parsers import FormulaParser
import unittest


class FormulaParserTestSuite(unittest.TestCase):
    def test_and(self):
        formula = "<<X,YYY>>F(A&B&C&D&EFG)"
        formula_parser = FormulaParser()
        result = formula_parser.parseAtlFormula(formula)
        self.assertEqual(str(result), "<<X, YYY>>F(A & (B & (C & (D & EFG))))")


if __name__ == '__main__':
    unittest.main()
