from enum import Enum
from .parser import Parser


class TemporalOperator(Enum):
    F = "F"
    G = "G"
    FG = "FG"


class PathQuantifier(Enum):
    A = "A"
    E = "E"


class Formula:
    expression = None
    temporalOperator = None

    def __init__(self):
        pass

    def __str__(self):
        return str(self.temporalOperator.value) + str(self.expression)


class AtlFormula(Formula):
    agents = []

    def __str__(self):
        return "<<" + (", ".join(self.agents)) + ">>" + super().__str__()


class CtlFormula(Formula):
    pathQuantifier = None

    def __str__(self):
        return str(self.pathQuantifier.value) + super().__str__()


class SimpleExpressionOperator(Enum):
    AND = "&"
    OR = "|"
    NOT = "!"
    EQ = "="
    NEQ = "!="


class SimpleExpression:
    left = None
    operator = None
    right = None

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __getValue(self, item, varValues):
        if isinstance(item, str):
            if item in varValues:
                return varValues[item]
            else:
                return item
        elif isinstance(item, SimpleExpression):
            return item.evaluate(varValues)
        return item

    def evaluate(self, varValues):
        left = self.__getValue(self.left, varValues)
        right = self.__getValue(self.right, varValues)
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
        pass

    def parseAtlFormula(self, formulaStr):
        self.setStr(formulaStr)

        formula = AtlFormula()
        formula.agents = self.__parseFormulaAgents()
        formula.temporalOperator = self.__parseFormulaTemporalOperator()
        formula.expression = self.__parseFormulaExpression()

        return formula

    def parseCtlFormula(self, formulaStr):
        self.setStr(formulaStr)

        formula = CtlFormula()
        formula.pathQuantifier = self.__parseFormulaPathQuantifier()
        formula.temporalOperator = self.__parseFormulaTemporalOperator()
        formula.expression = self.__parseFormulaExpression()

        return formula

    def __parseFormulaAgents(self):
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

    def __parseFormulaTemporalOperator(self):
        c, _ = self.readUntil(["("])
        if c == "F":
            return TemporalOperator.F
        elif c == "G":
            return TemporalOperator.G
        elif c == "FG":
            return TemporalOperator.FG
        else:
            raise Exception("Unknown formula temporal operator")

    def __parseFormulaPathQuantifier(self):
        c = self.read(1)
        if c == "A":
            return PathQuantifier.A
        elif c == "E":
            return PathQuantifier.E
        else:
            raise Exception("Unknown formula path quantifier")

    def __parseFormulaExpression(self):
        self.consume("(")
        formulaExpression = []
        while True:
            res = self.readUntil([")", "(", "&", "|", "=", "!"])
            str = res[0]
            chr = res[1]
            if chr == ")":
                if len(str) > 0:
                    formulaExpression.append(str)
                break
            elif chr == "(":
                formulaExpression.append(self.__parseFormulaExpression())
            elif chr == "&" or chr == "|" or chr == "=" or chr == "!":
                if len(str) > 0:
                    formulaExpression.append(str)
                if chr == "!" and self.peekChar(1) == "=":
                    formulaExpression.append("!=")
                    self.stepForward()
                else:
                    formulaExpression.append(chr)
                self.stepForward()
            else:
                raise Exception("Unimplemented character inside __parseFormulaExpression")
        simpleExpression = self.__convertToSimpleExpression(formulaExpression)
        self.consume(")")
        return simpleExpression

    def __convertToSimpleExpression(self, arr):
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
            return self.__convertToSimpleExpressionByOperator(arr, SimpleExpressionOperator.OR)

        # AND
        if arr.count("&") > 0:
            return self.__convertToSimpleExpressionByOperator(arr, SimpleExpressionOperator.AND)

        # EQ/NEQ
        if len(arr) == 3 and (arr[1] == "=" or arr[1] == "!="):
            left = self.__convertToSimpleExpression(arr[0])
            right = self.__convertToSimpleExpression(arr[2])
            if arr[1] == "=":
                return SimpleExpression(left, SimpleExpressionOperator.EQ, right)
            elif arr[1] == "!=":
                return SimpleExpression(left, SimpleExpressionOperator.NEQ, right)

        return arr

    def __convertToSimpleExpressionByOperator(self, arr, op):
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
            parts[i] = self.__convertToSimpleExpression(parts[i])
        expr = SimpleExpression(parts[0], op, parts[1])
        innermostExpr = expr
        for i in range(2, len(parts)):
            innermostExpr.right = SimpleExpression(innermostExpr.right, op, parts[i])
            innermostExpr = innermostExpr.right
        return expr
