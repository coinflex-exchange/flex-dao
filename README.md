# FLEX Decentralized Autonomous Organization Contracts

This repo contains the set of Contracts and the tools necessary for testing and deployment.

## Deployed Contracts Addresses

### Production contracts deployed on SmartBCH Mainnet

- Flex Coin (staked coin and reward token): 0x98Dd7eC28FB43b3C4c770AE532417015fa939Dd3

- veFlex (the DAO token / voting escrow token): 0xA9bB3b5334347F9a56bebb3f590E8dF97fC091f9

- DailyPayout (daily payout distribution contract): 0xB226C60886e81920d3d913858678d8C9e71eC17E


## Contributions

To begin working on this project, you need to set up the environment using

1. Python programming  languange (3.7.2 or above)
2. [Poetry](https://github.com/python-poetry/poetry), Python dependency management and packaging made easy.

Simply run this command on your Terminal to check if you have Python installed in your local machine

```bash
python --version
# or
python3 --version
```

Install Poetry package maanger

```bash
pip install -U poetry
# or
pip3 install -U poetry
```

Afterwards, you need to run the following command to install dependencies.


```bash
poetry install
```

## Running Tests

If you set-up the workspace correctly, you would also have installed

1. [pytest](https://github.com/pytest-dev/pytest), The pytest framework makes it easy to write small tests, yet scales to support complex functional testing

already listed as development dependencies under poetry configuration.
All tests can be run using the following command

```bash
pytest
```

or individual unit test can be run using the following command

```bash
pytest -k   `<unit_test_name>` 
```
