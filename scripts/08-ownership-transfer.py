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
from brownie import veFLEX, DailyPayout, QuarterlyPayout, Distributor
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
    1: None,                    # mainnet
    3: 'ropsten',               # ropsten testnet
    42: 'kovan',                # kovan testnet
    1337: 'dev',                # local ganache-cli evm
    10000: 'smartbch-mainnet',  # smartbch mainnet
    10001: 'smartbch-amber'     # smartbch testnet
  }
  if chain._chainid in (1, 42, 1337, 10000, 10001):
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
    with open('params/08-ownership-transfer.yml', 'rb') as dep:
      params: dict                                                                = safe_load(dep)

      veFLEX_new_admin                                                            = params.get('veFLEX_new_admin', None)
      veFLEX_addr                                                                 = params.get('veFLEX_addr', None)
      transfer_veFLEX_admin_to                                                    = params.get('transfer_veFLEX_admin_to', None)

      daily_payout_new_admin                                                      = params.get('daily_payout_new_admin', None)
      daily_payout_addr                                                           = params.get('daily_payout_addr', None)
      transfer_daily_payout_admin_to                                              = params.get('transfer_daily_payout_admin_to', None)

      quarterly_payout_new_admin                                                  = params.get('quarterly_payout_new_admin', None)
      quarterly_payout_addr                                                       = params.get('quarterly_payout_addr', None)
      transfer_quarterly_payout_admin_to                                          = params.get('transfer_quarterly_payout_admin_to', None)

      mini_daily_distributor_new_admin                                            = params.get('mini_daily_distributor_new_admin', None)
      mini_daily_distributor_addr                                                 = params.get('mini_daily_distributor_addr', None)
      transfer_mini_daily_distributor_admin_to                                    = params.get('transfer_mini_daily_distributor_admin_to', None)

      mini_quarterly_distributor_new_admin                                        = params.get('mini_quarterly_distributor_new_admin', None)
      mini_quarterly_distributor_addr                                             = params.get('mini_quarterly_distributor_addr', None)
      transfer_mini_quarterly_distributor_admin_to                                = params.get('transfer_mini_quarterly_distributor_admin_to', None)

      if veFLEX_new_admin is None or not isinstance(veFLEX_new_admin, str):
        print(f'{TERM_RED}Invalid `veFLEX_new_admin` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif veFLEX_addr is None or not isinstance(veFLEX_addr, str):
        print(f'{TERM_RED}Invalid `veFLEX_addr` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif transfer_veFLEX_admin_to is None or not isinstance(transfer_veFLEX_admin_to, int):
        print(f'{TERM_RED}Invalid `transfer_veFLEX_admin_to` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return

      elif daily_payout_new_admin is None or not isinstance(daily_payout_new_admin, str):
        print(f'{TERM_RED}Invalid `daily_payout_new_admin` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif daily_payout_addr is None or not isinstance(daily_payout_addr, str):
        print(f'{TERM_RED}Invalid `daily_payout_addr` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif transfer_daily_payout_admin_to is None or not isinstance(transfer_daily_payout_admin_to, int):
        print(f'{TERM_RED}Invalid `transfer_daily_payout_admin_to` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      
      elif quarterly_payout_new_admin is None or not isinstance(quarterly_payout_new_admin, str):
        print(f'{TERM_RED}Invalid `quarterly_payout_new_admin` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif quarterly_payout_addr is None or not isinstance(quarterly_payout_addr, str):
        print(f'{TERM_RED}Invalid `quarterly_payout_addr` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif transfer_quarterly_payout_admin_to is None or not isinstance(transfer_quarterly_payout_admin_to, int):
        print(f'{TERM_RED}Invalid `transfer_quarterly_payout_admin_to` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return

      elif mini_daily_distributor_new_admin is None or not isinstance(mini_daily_distributor_new_admin, str):
        print(f'{TERM_RED}Invalid `mini_daily_distributor_new_admin` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif mini_daily_distributor_addr is None or not isinstance(mini_daily_distributor_addr, str):
        print(f'{TERM_RED}Invalid `mini_daily_distributor_addr` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif transfer_mini_daily_distributor_admin_to is None or not isinstance(transfer_mini_daily_distributor_admin_to, int):
        print(f'{TERM_RED}Invalid `transfer_mini_daily_distributor_admin_to` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
  
      elif mini_quarterly_distributor_new_admin is None or not isinstance(mini_quarterly_distributor_new_admin, str):
        print(f'{TERM_RED}Invalid `mini_quarterly_distributor_new_admin` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif mini_quarterly_distributor_addr is None or not isinstance(mini_quarterly_distributor_addr, str):
        print(f'{TERM_RED}Invalid `mini_quarterly_distributor_addr` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return
      elif transfer_mini_quarterly_distributor_admin_to is None or not isinstance(transfer_mini_quarterly_distributor_admin_to, int):
        print(f'{TERM_RED}Invalid `transfer_mini_quarterly_distributor_admin_to` parameter found in `params/ownership-transfer.yml` file.{TERM_NFMT}')
        return

  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find `params/ownership-transfer.yml` file containing deployment parameters.{TERM_NFMT}')
    return

  ### Set Gas Price ##
  gas_strategy = ExponentialScalingStrategy('1.05 gwei', '5 gwei')

  ### 1. trasnfer ownership of veFLEX ###
  if transfer_veFLEX_admin_to: 
    ve_flex = veFLEX.at(veFLEX_addr)
    veFLEX_old_admin = ve_flex.admin()
    ve_flex.commit_transfer_ownership(veFLEX_new_admin, { 'from': acct, 'gas_price': gas_strategy })
    ve_flex.apply_transfer_ownership({ 'from': acct, 'gas_price': gas_strategy })

  ### 2. transfer ownership of daily payout ###
  if transfer_daily_payout_admin_to:
    daily_payout = DailyPayout.at(daily_payout_addr)
    daily_payout_old_admin = daily_payout.owner()
    daily_payout.transferOwnership(daily_payout_new_admin, { 'from': acct, 'gas_price': gas_strategy })

  ### 3. transfer ownership of quarterly payout ###
  if transfer_quarterly_payout_admin_to:
    quarterly_payout = QuarterlyPayout.at(quarterly_payout_addr)
    quarterly_payout_old_admin = quarterly_payout.owner()
    quarterly_payout.transferOwnership(quarterly_payout_new_admin, { 'from': acct, 'gas_price': gas_strategy })

  ### 4. transfer ownership of mini daily Distributor ###
  if transfer_mini_daily_distributor_admin_to:
    mini_daily_distributor = Distributor.at(mini_daily_distributor_addr)
    mini_daily_distributor_old_admin = mini_daily_distributor.admin()
    mini_daily_distributor.transferOwnership(mini_daily_distributor_new_admin, { 'from': acct, 'gas_price': gas_strategy })

  ### 5. transfer ownership of mini quarterly Distributor ###
  if transfer_mini_quarterly_distributor_admin_to:
    mini_quarterly_distributor = Distributor.at(mini_quarterly_distributor_addr)
    mini_quarterly_distributor_old_admin = mini_quarterly_distributor.admin()
    mini_quarterly_distributor.transferOwnership(mini_quarterly_distributor_new_admin, { 'from': acct, 'gas_price': gas_strategy })

  print(f'{TERM_RED}###OWNERSHIP TRANSFER SUMMARY###{TERM_NFMT}')
  if transfer_veFLEX_admin_to:
    print(f'veFLEX admin: {veFLEX_old_admin} ==> {ve_flex.admin()}')
  if transfer_daily_payout_admin_to:
    print(f'daily payout admin: {daily_payout_old_admin} ==> {daily_payout.owner()}')
  if transfer_quarterly_payout_admin_to:
    print(f'quarterly payout admin: {quarterly_payout_old_admin} ==> {quarterly_payout.owner()}')  
  if transfer_mini_daily_distributor_admin_to:
    print(f'mini daily distributor admin: {mini_daily_distributor_old_admin} ==> {mini_daily_distributor.admin()}')
  if transfer_mini_quarterly_distributor_admin_to:
    print(f'mini quarterly distributor admin: {mini_quarterly_distributor_old_admin} ==> {mini_quarterly_distributor.admin()}')
  print(f'{TERM_RED}######END###############{TERM_NFMT}')