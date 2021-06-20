from enum import Enum
from .parser import Parser


class FormulaType(Enum):
    F = "F"
    G = "G"


class Formula:
    def __init__(self):
        self._agents = []
        self._type = None
        self._expression = None

    @property
    def agents(self):
        return self._agents

    @agents.setter
    def agents(self, val):
        self._agents = val

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        self._type = val

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, val):
        self._expression = val

    def __str__(self):
        return f"<<{', '.join(self._agents)}>>{self._type.value}{self._expression}"


class SimpleExpressionOperator(Enum):
    AND = "&"
    OR = "|"
    NOT = "!"
    EQ = "="
    NEQ = "!="


class SimpleExpression:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    @staticmethod
    def __get_value(item, var_values):
        if isinstance(item, str):
            if item in var_values:
                return var_values[item]
            else:
                return item
        elif isinstance(item, SimpleExpression):
            return item.evaluate(var_values)

        return item

    def evaluate(self, var_values):
        left = self.__get_value(self.left, var_values)
        right = self.__get_value(self.right, var_values)
        if self.operator == SimpleExpressionOperator.NOT:
            return not right
        elif self.operator == SimpleExpressionOperator.AND:
            return not not (left and right)
        elif self.operator == SimpleExpressionOperator.OR:
            return not not (left or right)
        elif self.operator == SimpleExpressionOperator.EQ:
            return str(left) == str(right)
        elif self.operator == SimpleExpressionOperator.NEQ:
            return str(left) != str(right)
        else:
            raise Exception("Can't evaluate a SimpleExpression: unknown operator")

    def __str__(self):
        if self.operator == SimpleExpressionOperator.NOT:
            return str(self.operator.value) + str(self.right)
        else:
            return "(" + str(self.left) + " " + str(self.operator.value) + " " + str(self.right) + ")"


class FormulaParser(Parser):

    def __init__(self):
        super().__init__()

    def parse_formula(self, formula_str):
        self.setStr(formula_str)

        formula = Formula()
        formula.agents = self.__parse_formula_agents()
        formula.type = self.__parse_formula_type()
        formula.expression = self.__parse_formula_expression()

        return formula

    def __parse_formula_agents(self):
        agents = []
        self.consume("<<")
        while True:
            res = self.readUntil([">", ","])
            str = res[0]
            chr = res[1]
            agents.append(str)
            if chr == ">":
                break
            else:
                self.consume(",")
        self.consume(">>")
        return agents

    def __parse_formula_type(self):
        c = self.read(1)
        if c == "F":
            return FormulaType.F
        elif c == "G":
            return FormulaType.G
        else:
            raise Exception("Unknown formula type")

    def __parse_formula_expression(self):
        self.consume("(")
        formula_expression = []
        while True:
            res = self.readUntil([")", "(", "&", "|", "=", "!"])
            str = res[0]
            chr = res[1]
            if chr == ")":
                if len(str) > 0:
                    formula_expression.append(str)
                break
            elif chr == "(":
                formula_expression.append(self.__parse_formula_expression())
            elif chr == "&" or chr == "|" or chr == "=" or chr == "!":
                if len(str) > 0:
                    formula_expression.append(str)
                if chr == "!" and self.peekChar(1) == "=":
                    formula_expression.append("!=")
                    self.stepForward()
                else:
                    formula_expression.append(chr)
                self.stepForward()
            else:
                raise Exception("Unimplemented character inside __parseFormulaExpression")

        simple_expression = self.__convert_to_simple_expression(formula_expression)
        self.consume(")")
        return simple_expression

    def __convert_to_simple_expression(self, arr):
        # Single value
        if not isinstance(arr, list):
            return arr
        if len(arr) == 1:
            return arr[0]

        # NOT
        i = 0
        l = len(arr)
        while i < l:
            if arr[i] == "!":
                if i + 1 < l:
                    arr.pop(i)
                    l = l - 1
                    arr[i] = SimpleExpression(None, SimpleExpressionOperator.NOT, arr[i])
            i = i + 1

        # OR
        if arr.count("|") > 0:
            return self.__convert_to_simple_expression_by_operator(arr, SimpleExpressionOperator.OR)

        # AND
        if arr.count("&") > 0:
            return self.__convert_to_simple_expression_by_operator(arr, SimpleExpressionOperator.AND)

        # EQ/NEQ
        if len(arr) == 3 and (arr[1] == "=" or arr[1] == "!="):
            left = self.__convert_to_simple_expression(arr[0])
            right = self.__convert_to_simple_expression(arr[2])
            if arr[1] == "=":
                return SimpleExpression(left, SimpleExpressionOperator.EQ, right)
            elif arr[1] == "!=":
                return SimpleExpression(left, SimpleExpressionOperator.NEQ, right)

        return arr

    def __convert_to_simple_expression_by_operator(self, arr, op):
        i = 0
        l = len(arr)
        parts = []
        part = []
        while i < l:
            if arr[i] == op.value:
                parts.append(part)
                part = []
            else:
                part.append(arr[i])
            i = i + 1
        parts.append(part)
        for i in range(len(parts)):
            parts[i] = self.__convert_to_simple_expression(parts[i])
        expr = SimpleExpression(parts[0], op, parts[1])
        innermost_expr = expr
        for i in range(2, len(parts)):
            innermost_expr.right = SimpleExpression(innermost_expr.right, op, parts[i])
            innermost_expr = innermost_expr.right
        return expr
