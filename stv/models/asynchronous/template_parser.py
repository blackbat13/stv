import sys
from mako.template import Template


def lstripLines(str):
    return '\n'.join([line.lstrip() for line in str.splitlines()])


def train_controller():
    input_filename = "train_controller.mako"
    config = {"N_Trains": 2,
              "N_Controllers": 1}
    output_filename = f"train_controller_{config['N_Trains']}t_{config['N_Controllers']}c.txt"

    return input_filename, output_filename, config


def train_controller_synchronous():
    input_filename = "train_controller_synchronous.mako"
    config = {"N_Trains": 2,
              "N_Controllers": 1}
    output_filename = f"train_controller_synchronous_{config['N_Trains']}t_{config['N_Controllers']}c.txt"

    return input_filename, output_filename, config


def simple_voting():
    input_filename = "simple_voting.mako"
    config = {"N_Voters": 1,
              "N_Candidates": 2}
    output_filename = f"simple_voting_{config['N_Voters']}v_{config['N_Candidates']}c.txt"

    return input_filename, output_filename, config


if __name__ == "__main__":
    input_path = "specs/templates/"
    output_path = "specs/generated/"

    input_filename, output_filename, config = train_controller()

    template = Template(filename=input_path + input_filename)

    out = lstripLines(template.render(**config))

    with open(output_path + output_filename, 'w') as file:
        file.write(out)
