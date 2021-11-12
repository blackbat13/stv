from stv.models.asynchronous.parser import GlobalModelParser
from stv.parsers import FormulaParser
import pprint

if __name__ == "__main__":
    model_str = '''Agent A[1]:
init: q0
shared A: q0 -> q1
shared B: q0 -> q1
shared C: q1 -> q2
shared D: q1 -> q2

Agent B[1]:
init: q0
shared A: q0 -> q1
shared B: q0 -> q2
shared C: q1 -> win [A1_win=True]
shared C: q2 -> win [A1_win=False]
shared D: q1 -> win [A1_win=False]
shared D: q2 -> win [A1_win=True]
PROTOCOL: [[A,B],[C,D]]

PERSISTENT: [A1_win]
COALITION: [A1]
LOGIC: ATL
FORMULA: <<A1>>F(A1_win=True)'''

    model = GlobalModelParser().parse_from_string(model_str)
    model.generate()
    model.generate_local_models()
    print(f'Under-approximation: {"holds" if model.verify_under_approximation(False) else "does not have to hold"}')
    print(f'Under-approximation (refined): {"holds" if model.verify_under_approximation(True) else "does not have to hold"}')