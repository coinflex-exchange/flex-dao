#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-staking-rewards.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-13 18:01
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contract(s) ###
from brownie import fVault, StakingRewards
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
  reward_token: str   = None
  staking_token: str  = None
  try:
    with open('params/staking_rewards.yml', 'rb') as dep:
      params:dict     = safe_load(dep)
      reward_token    = params.get('reward_token', None)
      staking_token   = params.get('staking_token', None)
      if reward_token is None or not isinstance(reward_token, str) or len(reward_token) < 1:
        print(f'{TERM_RED}Invalid `reward_token` parameter found in `params/staking_rewards.yml` file.{TERM_NFMT}')
        return
      elif staking_token is None or not isinstance(staking_token, str) or len(staking_token) < 1:
        print(f'{TERM_RED}Invalid `staking_token` parameter found in `params/staking_rewards.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/staking_rewards.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Validate Parameters ###
  vested_token: fVault = fVault.at(reward_token)

  ### Set Gas Price ##
  gas_strategy = GasNowStrategy(gas_speed)

  ### Deployment ###
  staking_rewards = StakingRewards.deploy(vested_token, staking_token, { 'from': acct, 'gas_price': gas_strategy })
