from pyparsing import *

class AlternatingTimeTemporalLogicParser:
    def __init__(self, lat, props):
        self.lat = lat
        self.props = props
        self.initializeGroupingSymbols()
        self.initializeConnectives()
        self.initializeZeroaryAndAtomicFormulas()
        self.initializeFormula()

    def initializeGroupingSymbols(self):
        self.left_parenthesis = Suppress("(")
        self.right_parenthesis = Suppress(")")
        self.left_agents = "<<"
        self.right_agents = ">>"

    def initializeConnectives(self):
        # Binary Connectives
        self.less_equal = Keyword("<=")
        self.or_ = Keyword("|")
        self.and_ = Keyword("&")
        self.until = Keyword("U")
        self.weak = Keyword("W")
        # Unary Connectives
        self.not_ = Keyword("!") | Keyword("~")
        self.next = Keyword("X") | Keyword("()")
        self.event = Keyword("F") | Keyword("<>")
        self.always = Keyword("G") | Keyword("[]")


    def initializeZeroaryAndAtomicFormulas(self):
        self.lattice = oneOf(self.lat)
        self.prop = Combine(oneOf(self.props) + Optional("_" + Word(alphanums)))

    def initializeFormula(self):
        self.formula = Forward()
        self.operand = self.lattice | self.prop

        self.binaryConnective = self.or_ | self.and_ | self.less_equal | self.until | self.weak
        self.unaryConnective = self.not_ | self.next | self.event | self.always

        self.unaryFormula = Group(
            self.unaryConnective + self.formula) | \
                            Group(
            self.left_agents + Group(delimitedList(Word(alphanums), delim=','))
            + self.right_agents + self.formula)
        self.binaryFormula = Group(
            self.left_parenthesis
            + self.formula + self.binaryConnective
            + self.formula + self.right_parenthesis)

        self.formula << (self.unaryFormula | self.binaryFormula | self.operand)

    def parse(self, text):
        try:
            result = self.formula.parseString(text, parseAll=True)
            assert len(result) == 1

            return result[0]

        except (ParseException, ParseSyntaxException) as err:
            #			print("Syntax error:\n{0.line}\n{1}^".format(err, " " * (err.column - 1)))
            return "Error"

#props = "In Out Penalty Collision"
#const = "b n i u s t"
#ATLparser = AlternatingTimeTemporalLogicParser(const, props)
#txt = input()
#print(str(ATLparser.parse(txt)))