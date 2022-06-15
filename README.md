# STV - StraTegic Verifier

#### Collection of algorithms for verification of ATLir (and ATLIr) models

## Currently implemented models
Currently there are several models implemented in the tool. 
It is also possible to define other models using simple input language.

Available models:
+ Bridge scenario (two versions)
+ Castles
+ Dining Cryptographers
+ Machines and Robots in the factory (several versions)
+ Tian Ji
+ Drones and pollution
+ Random model
+ Asynchronous models
+ Selene e-voting protocol
+ Simple voting model (two versions)

## Other models
To create some of the models used in a various experiments, other model-checker tools were used.
Here is the list of created models.

Tamarin:
+ Prêt à Voter voting system
+ TMN protocol

UPPAAL:
+ Prêt à Voter voting system
+ vVote voting system

## Implemented algorithms
+ Fixpoint approximation (http://www.ifaamas.org/Proceedings/aamas2017/pdfs/p1241.pdf)
+ DominoDFS (http://www.ifaamas.org/Proceedings/aamas2019/pdfs/p197.pdf)
+ Strategy Logic with Simple Goals

## Requirements
+ Python 3.7 minimum
+ All libraries from requirements.txt

## Usage

```
pip install -r requirements.txt
```

```
python main.py generate-spec sai
python main.py verify synchronous tianji
python main.py verify synchronous castles
python main.py verify synchronous bridge
```

## Graphical Interface

There is also a graphical interface for the tool available.
As the tool itself, it's also a work in progress, so right now it supports only part of the models and algorithms.

### Desktop version

https://github.com/blackbat13/stv-ui

### Web version

http://stv.cs-htiew.com

## Credits

Lead Developer - Damian Kurpiewski (@blackbat13)

Additional features - Witold Pazderski, Yan Kim

## License

MIT License

Copyright (c) 2017 Damian Kurpiewski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.