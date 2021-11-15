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
from brownie import Distributor, FLEXCoin
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
    3: 'ropsten',         # ropsten testnet
    42: 'kovan',          # kovan testnet
    1337: 'dev',          # local ganache-cli evm
    10001: 'smartbch-amber', # smartbch testnet
    10000: 'smartbch-mainnet'
  }
  if chain._chainid in (1, 3, 42, 1337, 10001,10000):
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
  
  try:
    with open('params/distribution.yml', 'rb') as dep:
      params: dict                  = safe_load(dep)
      flex_addr                     = params.get('flex', None)
      distributor_addr        = params.get('distributor', None)

      if flex_addr is None or not isinstance(flex_addr, str) or len(flex_addr) < 1:
        print(f'{TERM_RED}Invalid `flex` parameter found in `params/distribution.yml` file.{TERM_NFMT}')
        return
      elif distributor_addr is None or not isinstance(distributor_addr, str) or len(distributor_addr) < 1:
        print(f'{TERM_RED}Invalid `daily_distributor` parameter found in `params/distribution.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/distributor.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Set Gas Price ##
  gas_strategy = ExponentialScalingStrategy('10 gwei', '50 gwei')

  ## need manually add the distributor into whitelist of payout contract

  flex = FLEXCoin.at(flex_addr)
  distributor = Distributor.at(distributor_addr)
  
  for i in range(10):
    flex.transfer(distributor, 100e18, {'from': acct, 'gas_price': gas_strategy})
    distributor.distribute({'from': acct, 'gas_price': gas_strategy})
