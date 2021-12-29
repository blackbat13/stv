import sys
from mako.template import Template


def lstripLines(str):
    return '\n'.join([line.lstrip() for line in str.splitlines()])


def train_controller():
    input_filename = "train_controller.mako"
    config = {"N_Trains": 5,
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

def simple_voting_synchronous():
    input_filename = "simple_voting_synchronous.mako"
    config = {"N_Voters": 5,
              "N_Candidates": 2}
    output_filename = f"simple_voting_synchronous_{config['N_Voters']}v_{config['N_Candidates']}c.txt"

    return input_filename, output_filename, config

def simple_voting_synchronous_assumption():
    input_filename = "simple_voting_synchronous_assumption.mako"
    config = {"N_Voters": 5,
              "N_Candidates": 2}
    output_filename = f"simple_voting_synchronous_assumption_{config['N_Voters']}v_{config['N_Candidates']}c.txt"

    return input_filename, output_filename, config

def selene():
    input_filename = "selene.mako"
    config = {"N_Voters": 1,
              "N_CVoters": 1,
              "N_Candidates": 2}
    output_filename = f"selene_{config['N_Voters']}v_{config['N_CVoters']}cv_{config['N_Candidates']}c.txt"

    return input_filename, output_filename, config


def selene_select_vote():
    input_filename = "selene_select_vote.mako"
    config = {"N_Voters": 1,
              "N_CVoters": 1,
              "N_Candidates": 5}
    output_filename = f"selene_select_vote_{config['N_Voters']}v_{config['N_CVoters']}cv_{config['N_Candidates']}c.txt"

    return input_filename, output_filename, config


def selene_select_vote_revoting():
    input_filename = "selene_select_vote_revoting.mako"
    config = {"N_Voters": 1,
              "N_CVoters": 1,
              "N_Revote": 5,
              "N_Candidates": 5}
    output_filename = f"selene_select_vote_revoting_{config['N_Voters']}v_{config['N_CVoters']}cv_{config['N_Candidates']}c_{config['N_Revote']}rev.txt"

    return input_filename, output_filename, config


def selene_select_vote_revoting_share():
    input_filename = "selene_select_vote_revoting_share.mako"
    config = {"N_Voters": 1,
              "N_CVoters": 1,
              "N_Revote": 10,
              "N_Candidates": 3}
    output_filename = f"selene_select_vote_revoting_{config['N_Voters']}v_{config['N_CVoters']}cv_{config['N_Candidates']}c_{config['N_Revote']}rev_share.txt"

    return input_filename, output_filename, config


def robots():
    input_filename = "robots.mako"
    config = {"N_Robots": 2,
              "N_Fields": 2,
              "Energy": 2}
    output_filename = f"robots_{config['N_Robots']}r_{config['N_Fields']}f_{config['Energy']}e.txt"

    return input_filename, output_filename, config

def robots_2trains():
    input_filename = "robots_2trains.mako"
    config = {"N_Robots": 2,
              "N_Fields": 3,
              "Energy": 1,
              "Positions": [1, 2]}
    output_filename = f"robots_2trains_{config['N_Robots']}r_{config['N_Fields']}f_{config['Energy']}e.txt"

    return input_filename, output_filename, config


def robots_assumption():
    input_filename = "robots_assumption.mako"
    config = {"N_Robots": 4,
              "N_Fields": 2,
              "Energy": 2}
    output_filename = f"robots_assumption_{config['N_Robots']}r_{config['N_Fields']}f_{config['Energy']}e.txt"

    return input_filename, output_filename, config


if __name__ == "__main__":
    input_path = "specs/templates/"
    output_path = "specs/generated/"

    input_filename, output_filename, config = robots_2trains()

    template = Template(filename=input_path + input_filename)

    out = lstripLines(template.render(**config))

    with open(output_path + output_filename, 'w') as file:
        file.write(out)
