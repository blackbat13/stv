import sys
from mako.template import Template


def lstripLines(str):
    return '\n'.join([line.lstrip() for line in str.splitlines()])


def train_controller():
    input_filename = "train_controller.mako"
    output_filename = "train_controller_2_1.txt"
    config = {"N_Trains": 2,
              "N_Controllers": 1}

    return input_filename, output_filename, config


def train_controller_synchronous():
    input_filename = "train_controller_synchronous.mako"
    output_filename = "train_controller_synchronous_2_1.txt"
    config = {"N_Trains": 2,
              "N_Controllers": 1}

    return input_filename, output_filename, config


if __name__ == "__main__":
    input_path = "specs/templates/"
    output_path = "specs/generated/"

    input_filename, output_filename, config = train_controller_synchronous()

    template = Template(filename=input_path + input_filename)

    out = lstripLines(template.render(**config))

    with open(output_path + output_filename, 'w') as file:
        file.write(out)
