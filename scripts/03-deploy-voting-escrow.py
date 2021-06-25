#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-voting-escrow.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-13 16:25
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
from brownie import accounts, network, Wei, veFLEX
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
  reward_token:str = None
  name:str       = None
  symbol:str     = None
  version:str    = None
  try:
    with open('params/voting-escrow.yml', 'rb') as dep:
      params:dict = safe_load(dep)
      reward_token  = params.get('reward_token', None)
      name        = params.get('name', None)
      symbol      = params.get('symbol', None)
      version     = params.get('version', None)
      if reward_token is None or not isinstance(reward_token, str) or len(reward_token) < 1:
        print(f'{TERM_RED}Invalid `reward_token` parameter found in `params/voting-escrow.yml` file.{TERM_NFMT}')
        return
      elif name is None or not isinstance(name, str) or len(name) < 1:
        print(f'{TERM_RED}Invalid `name` parameter found in `params/voting-escrow.yml` file.{TERM_NFMT}')
        return
      elif symbol is None or not isinstance(symbol, str) or len(symbol) < 1:
        print(f'{TERM_RED}Invalid `symbol` parameter found in `params/voting-escrow.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/voting-escrow.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Validate reward_token address ###

  ### Set Gas Price ##
  gas_station = {
    'fast': 0.000000121,
    'standard': 0.000000064
  }
  gas_price = gas_station['standard']

  ### Deployment ###
  limit = veFLEX.deploy.estimate_gas(reward_token, name, symbol, version, { 'from': acct }) * gas_price
  voting_escrow = veFLEX.deploy(reward_token, name, symbol, version, { 'from': acct, 'gas_limit': limit })
  print(f'Voting Escrow: { voting_escrow }')