#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-distributor.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-13 17:37
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contract(s) ###
from brownie import Distributor
### Third-Party Packages ###
from brownie.convert import Wei
from brownie.network import accounts, Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
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
    10001: 'smartbch-amber', # smartbch testnet
    10000: 'smartbch-mainnet'
  }
  if chain._chainid in (1, 42, 1337, 10001,10000):
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
  payout: str   = None
  flex: str  = None
  name: str    = None
  
  try:
    with open('params/distributor.yml', 'rb') as dep:
      params: dict       = safe_load(dep)
      flex               = params.get('flex', None)
      payout_daily       = params.get('payout_daily', None)
      name_daily         = params.get('name_daily', None)
      payout_quarterly   = params.get('payout_quarterly', None)
      name_quarterly     = params.get('name_quarterly', None)

      if payout_daily is None or not isinstance(payout_daily, str) or len(payout_daily) < 1:
        print(f'{TERM_RED}Invalid `payout_daily` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif name_daily is None or not isinstance(name_daily, str) or len(name_daily) < 1:
        print(f'{TERM_RED}Invalid `name_daily` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif payout_quarterly is None or not isinstance(payout_quarterly, str) or len(payout_quarterly) < 1:
        print(f'{TERM_RED}Invalid `payout_quarterly` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif name_quarterly is None or not isinstance(name_quarterly, str) or len(name_quarterly) < 1:
        print(f'{TERM_RED}Invalid `name_quarterly` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif flex is None or not isinstance(flex, str) or len(flex) < 1:
        print(f'{TERM_RED}Invalid `flex` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/distributor.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Set Gas Price ##
  gas_strategy = ExponentialScalingStrategy('10 gwei', '50 gwei')

  ### Deployment daily ###
  distributor_daily = Distributor.deploy(payout_daily, flex , name_daily, { 'from': acct, 'gas_price': gas_strategy })
  print(f'distributor daily: { distributor_daily }')

  ### Deployment quarterly###
  distributor_quarterly = Distributor.deploy(payout_quarterly, flex , name_quarterly, { 'from': acct, 'gas_price': gas_strategy })
  print(f'distributor quarterly: { distributor_quarterly }')
