import sys
from mako.template import Template


def lstripLines(str):
    return '\n'.join([line.lstrip() for line in str.splitlines()])

# @YK (possible) todo: "magic"-substitute for the input file pre-processing, s.t:
# lines containing one of pre-defined in configuration keywords (e.g. @v_i)
# are "unwrapped" into a set of lines over all possible evaluations of v_i
# (resulting in a user-friendly, easy to read specification)
# e.g.: for configuration with two voters, two candidates the following line
# shared vote_@v_i_@c_i: v_start -> v_end [wbb@v_i=@c_i]
# will be unwrapped into 4 lines:
# shared vote_1_1: v_start -> v_end [wbb1=1]
# shared vote_1_2: v_start -> v_end [wbb1=2]
# shared vote_2_1: v_start -> v_end [wbb2=1]
# shared vote_2_2: v_start -> v_end [wbb2=2]
# PS: another approach would be to return a valid mako input (pipeline: input>magic-preprocess>mako>output)

if __name__ == "__main__":
    myTemplate = Template(filename='./selene_template.mako')
    myConfig = {
        "N_Voters": 2,
        "N_Controllers": 1,
        "N_Candidates": 2
    }

    # myTemplate = Template(filename='./train_controller_template.mako')
    # myConfig = {
    #     "N_Trains": 2,
    #     "N_Controllers": 1
    # }

    out = lstripLines(myTemplate.render(**myConfig))
    print(out)
