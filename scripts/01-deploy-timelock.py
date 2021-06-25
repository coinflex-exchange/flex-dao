#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-timelock.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-09 15:40
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
from brownie import accounts, network, Wei, Timelock
from eth_account.account import ValidationError
from yaml import safe_load

TERM_RED  = '\033[1;31m'
TERM_NFMT = '\033[0;0m'

def main():
  ### Load Account to use ###
  acct = None
  chain = network.Chain()
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
      print(f'{TERM_RED}Cannot find dev-wallet mnemonic file defined at `wallet.dev.yml`.{TERM_NFMT}')
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
  admin:str = None
  delay:int = None
  try:
    with open('params/timelock.yml', 'rb') as dep:
      params:dict = safe_load(dep)
      admin       = params.get('admin', None)
      delay       = params.get('delay', None)
      if admin is None or not isinstance(admin, str) or len(admin) < 1:
        print(f'{TERM_RED}Invalid `admin` parameter found in `params/timelock.yml` file.{TERM_NFMT}')
        return
      elif delay is None or not isinstance(delay, int) or delay < 0:
        print(f'{TERM_RED}Invalid `delay` parameter found in `params/timelock.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/timelock.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Validate admin address ###

  ### Convert `delay` parameters from days to to seconds units
  delay_seconds = delay * 24 * 60 * 60

  ### Set Gas Price ##
  gas_station = {
    'fast': 0.000000121,
    'standard': 0.000000064
  }
  gas_price = gas_station['standard']

  ### Deployment ###
  limit = Timelock.deploy.estimate_gas(admin, delay_seconds, {'from': acct}) * gas_price
  timelock = Timelock.deploy(admin, delay_seconds, { 'from': acct, 'gas_limit': limit })
  print(f'Timelock: { timelock }')