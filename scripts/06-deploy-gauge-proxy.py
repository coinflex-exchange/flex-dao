#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-gauge-proxy.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-17 11:03
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
from brownie import accounts, network, Wei, GaugeProxy
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
  distributor:str  = None
  escrow:str       = None
  reward_token:str = None
  treasury:str     = None
  try:
    with open('params/gauge-proxy.yml', 'rb') as dep:
      params:dict     = safe_load(dep)
      distributor  = params.get('distributor', None)
      escrow       = params.get('escrow', None)
      reward_token = params.get('reward_token', None)
      treasury     = params.get('treasury', None)
      if distributor is None or not isinstance(distributor, str) or len(distributor) < 1:
        print(f'{TERM_RED}Invalid `distributor` parameter found in `params/gauge-proxy.yml` file.{TERM_NFMT}')
        return
      elif escrow is None or not isinstance(escrow, str) or len(escrow) < 1:
        print(f'{TERM_RED}Invalid `escrow` parameter found in `params/gauge-proxy.yml` file.{TERM_NFMT}')
        return
      elif reward_token is None or not isinstance(reward_token, str) or len(reward_token) < 1:
        print(f'{TERM_RED}Invalid `reward_token` parameter found in `params/gauge-proxy.yml` file.{TERM_NFMT}')
        return
      elif treasury is None or not isinstance(treasury, str) or len(treasury) < 1:
        print(f'{TERM_RED}Invalid `treasury` parameter found in `params/gauge-proxy.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/gauge-proxy.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Set Gas Price ##
  gas_station = {
    'fast': 0.000000121,
    'standard': 0.000000064
  }
  gas_price = gas_station['standard']

  ### Deployment ###
  limit = GaugeProxy.deploy.estimate_gas(distributor, escrow, reward_token, treasury, { 'from': acct }) * gas_price
  gauge_proxy = GaugeProxy.deploy(distributor, escrow, reward_token, treasury, { 'from': acct, 'gas_limit': limit })
  print(f'GaugeProxy: { gauge_proxy }')
