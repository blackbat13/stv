from stv.parsers import FormulaParser


def testEval(formula, varValues, expected):
    print("    using", varValues, "and expecting", expected)
    evaluated = formula.expression.evaluate(varValues)
    print("        evaluated to", evaluated)
    assert evaluated == expected


fp = FormulaParser()

fs = "<<X,YYY>>F(A&B&C&D&EFG)"
print("Test #1: parsing '" + fs + "':")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X, YYY>>F(A & (B & (C & (D & EFG))))"
print()

fs = "<<X,YYY>>G(A|B|C|D|EFG)"
print("Test #2: parsing '" + fs + "':")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X, YYY>>G(A | (B | (C | (D | EFG))))"
print()

fs = "<<X,YYY>>F(A&B|C|D|E&F&G|H)"
print("Test #3: parsing '" + fs + "':")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X, YYY>>F((A & B) | (C | (D | ((E & (F & G)) | H))))"
print()

fs = "<<X,YYY>>F(A & (B|C) | D | E & F & G | H)"
print("Test #4: parsing '" + fs + "':")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X, YYY>>F((A & (B | C)) | (D | ((E & (F & G)) | H)))"
print()

fs = "<<X,YYY>>F(A&!B|C!=2&(AAA=BBB&CX)&A=3)"
print("Test #5: parsing '" + fs + "':")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X, YYY>>F((A & !B) | ((C != 2) & (((AAA = BBB) & CX) & (A = 3))))"
print()

fs = "<<X>>F(A&B)"
print("Test #6: parsing & evaluating '" + fs + "'")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X>>F(A & B)"
testEval(f, {"A": 1, "B": 0}, False)
testEval(f, {"A": 1, "B": 1}, True)
testEval(f, {"A": 0, "B": 0}, False)
print()

fs = "<<X>>F(A|B&C)"
print("Test #7: parsing & evaluating '" + fs + "'")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X>>F(A | (B & C))"
print("using: A=1, B=1, C=1")
testEval(f, {"A": 1, "B": 1, "C": 1}, True)
testEval(f, {"A": 0, "B": 1, "C": 1}, True)
testEval(f, {"A": 0, "B": 0, "C": 1}, False)
testEval(f, {"A": 1, "B": 0, "C": 1}, True)
print()

fs = "<<X>>F(A=3)"
print("Test #8: parsing & evaluating '" + fs + "'")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X>>F(A = 3)"
testEval(f, {"A": 1}, False)
testEval(f, {"A": 3}, True)
testEval(f, {"A": 33}, False)
print()

fs = "<<X>>F(A!=test)"
print("Test #9: parsing & evaluating '" + fs + "'")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X>>F(A != test)"
testEval(f, {"A": "blah"}, True)
testEval(f, {"A": "test"}, False)
print()

fs = "<<X>>F(A&!B | C != test & D)"
print("Test #10: parsing & evaluating '" + fs + "'")
f = fp.parseAtlFormula(fs)
print(f)
assert str(f) == "<<X>>F((A & !B) | ((C != test) & D))"
testEval(f, {"A": 1, "B": 0, "C": "test", "D": 0}, True)
testEval(f, {"A": 1, "B": 1, "C": "test", "D": 0}, False)
testEval(f, {"A": 1, "B": 1, "C": "test", "D": 1}, False)
testEval(f, {"A": 1, "B": 1, "C": "xxxx", "D": 1}, True)
print()

print("OK")
print()
