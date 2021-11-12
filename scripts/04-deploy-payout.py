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
from brownie import DailyPayout,QuarterlyPayout
### Third-Party Packages ###
from brownie.convert import Wei
from brownie.network import accounts, Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account.account import Account, ValidationError
from yaml import safe_load
import time
import datetime

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
  if chain._chainid in (1, 42, 1337, 10000,10001):
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
    with open('params/payout.yml', 'rb') as dep:
      params:dict     = safe_load(dep)
      reward_token    = params.get('reward_token_pp', None)
      vote_escrowed_token   = params.get('vote_escrowed_token_pp', None)
      start_block_height   = params.get('start_block_height', None)
      if reward_token is None or not isinstance(reward_token, str) or len(reward_token) < 1:
        print(f'{TERM_RED}Invalid `reward_token` parameter found in `params/revenueshare.yml` file.{TERM_NFMT}')
        return
      elif vote_escrowed_token is None or not isinstance(vote_escrowed_token, str) or len(vote_escrowed_token) < 1:
        print(f'{TERM_RED}Invalid `vote_escrowed_token` parameter found in `params/revenueshare.yml` file.{TERM_NFMT}')
        return
      elif start_block_height is None or not isinstance(start_block_height, int):
        print(f'{TERM_RED}Invalid `end_block` parameter found in `params/revenueshare.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/revenueshare.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Validate Parameters ###
  #not sure what this is
  #vested_token: fVault = fVault.at(reward_token)

  ### Set Gas Price ##
  gas_strategy = ExponentialScalingStrategy('10 gwei', '50 gwei')

  ### Deployment ###
  dailyPayout = DailyPayout.deploy(reward_token, vote_escrowed_token, { 'from': acct, 'gas_price': gas_strategy })
  print(f'DailyPayout: { dailyPayout }')

  ### Set Start time ###
  dailyPayout.setStartBlockHeight(start_block_height, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Start block height: { dailyPayout.startBlockHeight() }') 
  
  ### Deployment ###
  quarterlyPayout = QuarterlyPayout.deploy(reward_token, vote_escrowed_token, { 'from': acct, 'gas_price': gas_strategy })
  print(f'QuarterlyPayout: { quarterlyPayout }')

  ### Set Start time ###
  quarterlyPayout.setStartBlockHeight(start_block_height, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Start time: { quarterlyPayout.startBlockHeight() }') 