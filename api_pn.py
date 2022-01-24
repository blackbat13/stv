import sys
from stv.models.asynchronous import GlobalModel
from stv.models.asynchronous.parser import GlobalModelParser
import time

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Please provide file name")
        exit(1)

    file_name = sys.argv[1]

    model = GlobalModelParser().parse(file_name)
    start = time.process_time()
    model.generate(reduction=False)
    end = time.process_time()

    print(f"Generation time: {end - start}, #states: {model.states_count}, #transitions: {model.transitions_count}")

    print("Approx low", model.verify_approximation(False))
    print("Approx up", model.verify_approximation(True))
