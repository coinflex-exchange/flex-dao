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
from brownie import veFLEX, DailyPayout,QuarterlyPayout, Distributor
### Third-Party Packages ###
from brownie.convert import Wei
from brownie.network import accounts, Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account.account import Account, ValidationError
from yaml import safe_load

TERM_RED  = '\033[1;31m'
TERM_NFMT = '\033[0;0m'

def main():
  ### Load Account to use ###
  acct: Account = None
  chain: Chain  = Chain()
  print(f'Network Chain-ID: { chain }')
  chain_map = {
    1: None,              # mainnet
    3: 'ropsten',         # ropsten testnet
    42: 'kovan',          # kovan testnet
    1337: 'dev',          # local ganache-cli evm
    10001: 'smartbch-amber' # smartbch testnet
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
    with open('params/integration-fixed.yml', 'rb') as dep:
      params: dict              = safe_load(dep)
      flex                      = params.get('flex', None)
      
      name                      = params.get('name', None)
      symbol                    = params.get('symbol', None)
      version                   = params.get('version', None)
      
      start_block_height        = params.get('start_block_height', None)
      operator                  = params.get('operator', None)
      
      name_daily                = params.get('name_daily', None)
      name_quarterly            = params.get('name_quarterly', None)
      delegatee                 = params.get('delegatee', None) 


      if flex is None or not isinstance(flex, str) or len(flex) < 1:
        print(f'{TERM_RED}Invalid `flex` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif name is None or not isinstance(name, str) or len(name) < 1:
        print(f'{TERM_RED}Invalid `name` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif symbol is None or not isinstance(symbol, str) or len(symbol) < 1:
        print(f'{TERM_RED}Invalid `symbol` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif version is None or not isinstance(version, str) or len(version) < 1:
        print(f'{TERM_RED}Invalid `version` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif start_block_height is None or not isinstance(start_block_height, int):
        print(f'{TERM_RED}Invalid `start_block_height` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif operator is None or not isinstance(operator, str) or len(operator) < 1:
        print(f'{TERM_RED}Invalid `operator` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif name_daily is None or not isinstance(name_daily, str) or len(name_daily) < 1:
        print(f'{TERM_RED}Invalid `name_daily` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif name_quarterly is None or not isinstance(name_quarterly, str) or len(name_quarterly) < 1:
        print(f'{TERM_RED}Invalid `name_quarterly` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
      elif delegatee is None or not isinstance(delegatee, str) or len(delegatee) < 1:
        print(f'{TERM_RED}Invalid `name_quarterly` parameter found in `params/interation.yml` file.{TERM_NFMT}')
        return
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/interation.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Set Gas Price ##
  gas_strategy = ExponentialScalingStrategy('10 gwei', '50 gwei')

  ### 1. Deploy veFLEX ###
  ve_flex = veFLEX.deploy(flex, name, symbol, version, { 'from': acct, 'gas_price': gas_strategy })
  print(f'veFLEX: { ve_flex } at block height {ve_flex.tx.block_number}')

  if start_block_height <= ve_flex.tx.block_number:
    print(f'{TERM_RED}Aborting deployment, the payout start block height should be bigger than veFlex contract deployment block height.{TERM_NFMT}')
    return

  ### 2. Deploy Daily Payout ###
  daily_payout = DailyPayout.deploy(flex, ve_flex, { 'from': acct, 'gas_price': gas_strategy })
  print(f'DailyPayout: { daily_payout }')

  ### 2.1. Set Start block height ###
  daily_payout.setStartBlockHeight(start_block_height, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Start block height: { daily_payout.startBlockHeight() }') 

  ### 2.2. Add operator ###
  daily_payout.addOperator(operator, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Daily payout added an operator: {operator}')

  ### 3. Deploy Quarterly Payout ###
  quarterly_payout = QuarterlyPayout.deploy(flex, ve_flex, { 'from': acct, 'gas_price': gas_strategy })
  print(f'QuarterlyPayout: { quarterly_payout }')

  ### 3.1. Set Start block height ###
  quarterly_payout.setStartBlockHeight(start_block_height, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Start time: { quarterly_payout.startBlockHeight() }') 

  ### 3.2. Add operator ###
  quarterly_payout.addOperator(operator, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Quarterly payout added an operator: {operator}')

  ### 4. Deploy mini Daily Distributor ###
  distributor_daily = Distributor.deploy(daily_payout, flex , name_daily, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Distributor daily: { distributor_daily }')

  ### 4.1. Add mini daily distributor into whitelist of daily payout ###
  daily_payout.addDistributor(distributor_daily, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Enable distributor {distributor_daily} in daily payout {daily_payout}')

  ### 4.2. Add additional delegatee for mini distributor ###
  distributor_daily.addDistributor(delegatee, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Daily distributor added an delegatee: {delegatee}')

  ### 5. Deployment mini Quarterly Distributor ###
  distributor_quarterly = Distributor.deploy(quarterly_payout, flex , name_quarterly, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Distributor quarterly: { distributor_quarterly }')

  ### 5.1. Add mini Quarterly distributor into whitelist of Quarterly payout ###
  quarterly_payout.addDistributor(distributor_quarterly, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Enable distributor {distributor_quarterly} in quarterly payout {quarterly_payout}')
  
  ### 5.2. Add additional delegatee for mini distributor ###
  distributor_quarterly.addDistributor(delegatee, { 'from': acct, 'gas_price': gas_strategy })
  print(f'Quarterly distributor added an delegatee: {delegatee}')

  print(f'{TERM_RED}###DEPLOYMENT SUMMARY###{TERM_NFMT}')
  print(f'FLEX deployed at: {flex}');
  print(f'veFLEX deployed at: {ve_flex}')
  print(f'Daily payout deployed at: {daily_payout} with start height: {start_block_height}')
  print(f'Daily payout added an operator {operator}')
  print(f'Quarterly payout deployed at: {quarterly_payout} with start height: {start_block_height}')
  print(f'Quarterly payout added an operator {operator}')
  print(f'Mini Daily distributor deployed at {distributor_daily}')
  print(f'Mini Daily distributor added a delegatee {delegatee}')
  print(f'Mini Quarterly distributor deployed at {distributor_quarterly}')
  print(f'Mini Quaterly distributor added a delegatee {delegatee}')
  print(f'{TERM_RED}######END###############{TERM_NFMT}')