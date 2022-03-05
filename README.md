# BLockchain with Proof Of Stake writing in Python

## Getting Started

Python 3.x and Pip 3.x is required to run.

If you prefer, you can create a Python virtual environment to run the project.

## Installing

Some packages are needed to run the project, install using the python Pip package manager

``` bash
pip install pycryptodome p2pnetwork Flask flask-classful waitress requests jsonify jsonpickle
```

## Run

Run main.py passing the ip address and port as argument
``` bash
python main.py 127.0.0.1:10000
```

## Interaction

To send transactions, you must use the REST API.

You can use `interaction.py` to test the API