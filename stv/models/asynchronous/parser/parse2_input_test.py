from stv.models.asynchronous.parser import GlobalModelParser
from stv.parsers import FormulaParser
import pprint

if __name__ == "__main__":
    model_str = '''Agent A{
        var: !A_win;
        init: q0;
    
        a: q0 --> q1;
        b: q0 --> q1;
        c: q1 --> q2;
        d: q1 --> q2;
    }
    
    Agent B[1]{
        init: q0;
    
        sh a: q0 --> q1;
        sh b: q0 --> q2;
    
        sh c: q1 --> q3: A_win = True;
        sh c: q2 --> q3: A_win = False;
    
        sh d: q1 --> q3: A_win = False;
        sh d: q2 --> q3: A_win = True;
    
        protocol: [a,b], [b,c]; # B cannot control which action from the bracket-group will be taken
    }
    
    Query Psi{
        reduction: [A_win];
        formula: <<A1>>F(A_win=True);
    }'''
    model = GlobalModelParser().parse_2(model_str)

    model.generate()
    model.generate_local_models()

    pp = pprint.PrettyPrinter(indent=4, depth=8)
    print('=' * 32)
    print("Local models:")
    print('=' * 32)
    for local_model in model.local_models:
        local_model.print()
        print('-'*32)
