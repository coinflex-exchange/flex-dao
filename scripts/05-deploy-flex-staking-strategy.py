#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-flex-staking-strategy.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-16 14:00
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contract(s) ###
from brownie import Controller, FLEXStakingStrategy, StakingRewards, Timelock
### Third-Party Packages ###
from brownie.convert import Wei
from brownie.network import accounts, Chain
from brownie.network.gas.strategies import GasNowStrategy
from eth_account.account import Account, ValidationError
from yaml import safe_load

TERM_RED  = '\033[1;31m'
TERM_NFMT = '\033[0;0m'

def main(gas_speed: str = 'standard'):
  ### Load Account to use ###
  acct: Account = None
  chain: Chain  = Chain()
  print(f'Network Chain-ID: { chain }')
  chain_map = {
    1: None,              # mainnet
    42: 'kovan',          # kovan testnet
    1337: 'dev',          # local ganache-cli evm
    10001: 'smartbch-t1a' # smartbch testnet
  }
  if chain._chainid in (1, 42, 1337, 10001):
    chain_name = chain_map[chain._chainid]
    file_name = 'wallet.yml' if chain_name is None else f'wallet.{chain_name}.yml'
    ### Load Mnemonic from YAML File ###
    try:
      with open(file_name) as f:
        content = safe_load(f)
        ### Read Mnemonic ###
        mnemonic = content.get('mnemonic', None)
        acct = accounts.from_mnemonic(mnemonic, count=1)
    except FileNotFoundError:
      print(f'{TERM_RED}Cannot find wallet mnemonic file defined at `{file_name}`.{TERM_NFMT}')
      return
    except ValidationError:
      print(f'{TERM_RED}Invalid address found in wallet mnemonic file.{TERM_NFMT}')
      return
    ### Transfers some Ether for usage to dev wallet ###
    if chain._chainid == 1337: 
      try:
        accounts[0].transfer(acct, Wei('100 ether').to('wei'))
      except ValueError: pass
  else:
    print('!! Invalid chainid found.')
    return
  print(f'Account: {acct}')
  balance = acct.balance()
  print(f'Account Balance: {balance}')
  if balance == 0:
    return # If balance is zero, exits

  ### Loads Deployment Parameters ###
  rewards: str    = None
  want: str       = None
  governance: str = None
  controller: str = None
  timelock: str   = None
  try:
    with open('params/flex-staking-strategy.yml', 'rb') as dep:
      params: dict = safe_load(dep)
      rewards      = params.get('rewards', None)
      want         = params.get('want', None)
      governance   = params.get('governance', None)
      controller   = params.get('controller', None)
      timelock     = params.get('timelock', None)
      if rewards is None or not isinstance(rewards, str) or len(rewards) < 1:
        print(f'{TERM_RED}Invalid `rewards` parameter found in `params/flex-staking-strategy.yml` file.{TERM_NFMT}')
        return
      elif want is None or not isinstance(want, str) or len(want) < 1:
        print(f'{TERM_RED}Invalid `want` parameter found in `params/flex-staking-strategy.yml` file.{TERM_NFMT}')
        return
      elif governance is None or not isinstance(governance, str) or len(governance) < 1:
        print(f'{TERM_RED}Invalid `governance` parameter found in `params/flex-staking-strategy.yml` file.{TERM_NFMT}')
        return
      elif controller is None or not isinstance(controller, str) or len(controller) < 1:
        print(f'{TERM_RED}Invalid `controller` parameter found in `params/flex-staking-strategy.yml` file.{TERM_NFMT}')
        return
      elif timelock is None or not isinstance(timelock, str) or len(timelock) < 1:
        print(f'{TERM_RED}Invalid `timelock` parameter found in `params/flex-staking-strategy.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/staking_rewards.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Validate Parameters ###
  staking_rewards: StakingRewards = StakingRewards.at(rewards)
  controller: Controller          = Controller.at(controller)
  timelock: Timelock              = Timelock.at(timelock)

  ### Set Gas Price ##
  gas_strategy = GasNowStrategy(gas_speed)

  ### Deployment ###
  strategy = FLEXStakingStrategy.deploy(staking_rewards, want, governance, controller, timelock, { 'from': acct, 'gas_price': gas_strategy })
