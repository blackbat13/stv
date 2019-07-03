# STV - StraTegic Verifier

#### Collection of algorithms for verification of ATLir (and ATLIr) models

## Currently implemented models
+ Bridge scenario
+ Castles
+ Dining Cryptographers
+ Machines and Robots in the factory
+ Tian Ji
+ Drones and pollution

## Implemented algorithms
+ Fixpoint approximation (http://www.ifaamas.org/Proceedings/aamas2017/pdfs/p1241.pdf)
+ DominoDFS (http://www.ifaamas.org/Proceedings/aamas2019/pdfs/p197.pdf)
+ Strategy Logic with Simple Goals

## Requirements
+ Python 3.7 minimum
+ All libraries from requirements.txt
+ PyCharm IDE (Community or Professional)

## Getting started

First you need to open the project directory in the PyCharm IDE.
For some reason, without it, Python cannot see the modules.
I will try to fix that in the future.

### Approximations

To run experiments using approximations algorithm, simply select the desired model in the simple_models/experiments folder and run it in the PyCharm IDE.
Please keep in mind that you may need to modify the code a little, as not all of the experiments are implemented in an user-friendly way.

### DominoDFS

To run experiments using DominoDFS algorithm, open desired model in the comparing_strats/experiments folder and run in in the PyCharm IDE.

## Graphical Interface
There is also a graphical interface for the tool available.
As the tool itself, it's also a work in progress, so right now it supports only part of the models and algorithms.
It is available here: https://github.com/blackbat13/StraTegicVerifier