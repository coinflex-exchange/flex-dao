#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-ve-flex.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-13 17:37
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contract(s) ###
from brownie import veFLEX
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
  token: str   = None
  name: str    = None
  symbol: str  = None
  version: str = None
  try:
    with open('params/ve-flex.yml', 'rb') as dep:
      params: dict = safe_load(dep)
      token        = params.get('token', None)
      name         = params.get('name', None)
      symbol       = params.get('symbol', None)
      version      = params.get('version', None)
      if token is None or not isinstance(token, str) or len(token) < 1:
        print(f'{TERM_RED}Invalid `token` parameter found in `params/ve-flex.yml` file.{TERM_NFMT}')
        return
      elif name is None or not isinstance(name, str) or len(name) < 1:
        print(f'{TERM_RED}Invalid `name` parameter found in `params/ve-flex.yml` file.{TERM_NFMT}')
        return
      elif symbol is None or not isinstance(symbol, str) or len(symbol) < 1:
        print(f'{TERM_RED}Invalid `symbol` parameter found in `params/ve-flex.yml` file.{TERM_NFMT}')
        return
      elif version is None or not isinstance(version, str) or len(version) < 1:
        print(f'{TERM_RED}Invalid `version` parameter found in `params/ve-flex.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/ve-flex.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Set Gas Price ##
  gas_strategy = GasNowStrategy(gas_speed)

  ### Deployment ###
  ve_flex = veFLEX.deploy(token, name, symbol, version, { 'from': acct, 'gas_price': gas_strategy })
  print(f'veFLEX: { ve_flex }')
