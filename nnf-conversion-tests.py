from stv.parsers import FormulaParser

fp = FormulaParser()

fs = "AG(!(A|B))"
print("Test #1: parsing '" + fs + "':")
f = fp.parseCtlFormula(fs)
f.convertToNNF()
print(str(f))
assert str(f) == "AG(!A & !B)"
print()

fs = "EF(!(A&B))"
print("Test #2: parsing '" + fs + "':")
f = fp.parseCtlFormula(fs)
f.convertToNNF()
print(str(f))
assert str(f) == "EF(!A | !B)"
print()

fs = "AF(!(A&!B)&C)"
print("Test #3: parsing '" + fs + "':")
f = fp.parseCtlFormula(fs)
f.convertToNNF()
print(str(f))
assert str(f) == "AF((!A | B) & C)"
print()

fs = "EG(!(!(A & !B)))"
print("Test #4: parsing '" + fs + "':")
f = fp.parseCtlFormula(fs)
f.convertToNNF()
print(str(f))
assert str(f) == "EG(A & !B)"
print()


#Double Negation not Implemented in STV

# fs = "AG(!!A & !!B))"
# print("Test #4: parsing '" + fs + "':")
# f = fp.parseCtlFormula(fs)
# f.convertToNNF()
# print(str(f))
# assert str(f) == "EG(A & !B)"
# # print()

print("OK")
print()