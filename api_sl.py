import sys
from stv.models import SimpleModel

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Please provide file name")
        exit(1)

    file_name = sys.argv[1]
    file = open(file_name, 'r')
    json_str = file.read()
    file.close()
    result = SimpleModel.load_sl_from_json(json_str)
    output_file = open('out.txt', 'w')
    for i in result:
        output_file.write(f'{i} ')

    output_file.close()
