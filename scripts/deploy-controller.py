#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-controller.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-13 18:48
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
from brownie import accounts, network, Wei, Controller
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
  governance:str = None
  strategist:str = None
  timelock:str   = None
  devfund:str    = None
  treasury:str   = None
  onesplit:str   = None
  try:
    with open('params/controller.yml', 'rb') as dep:
      params:dict = safe_load(dep)
      governance  = params.get('governance', None)
      strategist  = params.get('strategist', None)
      treasury    = params.get('treasury', None)
      devfund     = params.get('devfund', None)
      timelock    = params.get('timelock', None)
      onesplit    = params.get('onesplit', None)
      if governance is None or not isinstance(governance, str) or len(governance) < 1:
        print(f'{TERM_RED}Invalid `governance` parameter found in `params/controller.yml` file.{TERM_NFMT}')
        return
      elif strategist is None or not isinstance(strategist, str) or len(strategist) < 1:
        print(f'{TERM_RED}Invalid `strategist` parameter found in `params/controller.yml` file.{TERM_NFMT}')
        return
      elif timelock is None or not isinstance(timelock, str) or len(timelock) < 1:
        print(f'{TERM_RED}Invalid `timelock` parameter found in `params/controller.yml` file.{TERM_NFMT}')
        return
      elif devfund is None or not isinstance(devfund, str) or len(devfund) < 1:
        print(f'{TERM_RED}Invalid `devfund` parameter found in `params/controller.yml` file.{TERM_NFMT}')
        return
      elif treasury is None or not isinstance(treasury, str) or len(treasury) < 1:
        print(f'{TERM_RED}Invalid `treasury` parameter found in `params/controller.yml` file.{TERM_NFMT}')
        return
      elif onesplit is None or not isinstance(onesplit, str) or len(onesplit) < 1:
        print(f'{TERM_RED}Invalid `onesplit` parameter found in `params/controller.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/controller.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Validate addresses ###

  ### Set Gas Price ##
  gas_station = {
    'fast': 0.000000121,
    'standard': 0.000000064
  }
  gas_price = gas_station['standard']

  ### Deployment ###
  limit = Controller.deploy.estimate_gas(governance, strategist, timelock, devfund, treasury, onesplit, { 'from': acct }) * gas_price
  ctrl = Controller.deploy(governance, strategist, timelock, devfund, treasury, onesplit, { 'from': acct, 'gas_limit': limit })
  print(f'Controller: { ctrl }')
