# FLEX Decentralized Autonomous Organization Contracts

This repo contains the set of Contracts and the tools necessary for testing and deployment.

See individual contract descriptions here

* [Controller.sol](./docs/controller.md)
  * This is the main logic of the Decentralized Autonomous Organization
* [DAOToken](./docs/daotoken.md)
* [RewardToken](./docs/reward_token.md)
* [ProtocolGovernance](./docs/protocol_governance.md)
* [Timelock](./docs/timelock.md)

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

Afterwards, you need the following python libraries

1. [Brownie](https://github.com/eth-brownie/brownie), A Python-based development and testing framework for smart contracts targeting the Ethereum Virtual Machine.
2. [Bip-Utils](https://github.com/ebellocchia/bip_utils), Implementation of BIP39, BIP32, BIP44, BIP49 and BIP84, Monero, Substrate for generation of crypto-currencies wallets (mnemonic phrases, seeds, private/public keys and addresses)

...simply by running the following command

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

## Deployment

[TODO] Set up wallet using yaml file
[TODO] Run deployment scripts under scripts/ directory

```bash
brownie run ...
```
