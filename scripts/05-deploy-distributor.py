#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  deploy-distributor.py
# VERSION: 	 1.0
# CREATED: 	 2021-06-13 18:01
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
from brownie import accounts, network, Wei, Distributor, RewardToken
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
  reward_token:str    = None
  devfund:str         = None
  token_per_block:int = None
  start_block:int     = None
  end_block:int       = None
  try:
    with open('params/distributor.yml', 'rb') as dep:
      params:dict     = safe_load(dep)
      reward_token    = params.get('reward_token', None)
      devfund         = params.get('devfund', None)
      token_per_block = params.get('token_per_block', 1) # Defaults to 1
      start_block     = params.get('start_block', 0)     # Defaults to 0
      end_block       = params.get('end_block', 10)      # Defaults to 10
      if reward_token is None or not isinstance(reward_token, str) or len(reward_token) < 1:
        print(f'{TERM_RED}Invalid `reward_token` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif devfund is None or not isinstance(devfund, str) or len(devfund) < 1:
        print(f'{TERM_RED}Invalid `devfund` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif token_per_block is None or not isinstance(token_per_block, int) or token_per_block < 1:
        print(f'{TERM_RED}Invalid `token_per_block` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif start_block is None or not isinstance(start_block, int) or start_block < 0:
        print(f'{TERM_RED}Invalid `start_block` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
      elif end_block is None or not isinstance(end_block, int) or end_block < start_block:
        print(f'{TERM_RED}Invalid `end_block` parameter found in `params/distributor.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/distributor.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Set Gas Price ##
  gas_station = {
    'fast': 0.000000121,
    'standard': 0.000000064
  }
  gas_price = gas_station['standard']

  ### Deployment ###
  token = RewardToken.at(reward_token)
  limit = Distributor.deploy.estimate_gas(token, devfund, token_per_block, start_block, end_block, { 'from': acct }) * gas_price
  distributor = Distributor.deploy(token, devfund, token_per_block, start_block, end_block, { 'from': acct, 'gas_limit': limit })
  print(f'Distributor: { distributor }')
