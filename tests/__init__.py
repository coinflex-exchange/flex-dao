#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/__init__.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Standard Packages ###
from typing import List
### Third-Party Packages ###
from brownie.convert import  Wei
from brownie.network import accounts
from eth_account import Account
from pytest import fixture
from yaml import safe_load

### ANSI Coloring ###
BLUE: str  = '\033[1;34m'
RED: str   = '\033[1;31m'
GREEN: str = '\033[1;32m'
NFMT: str  = '\033[0;0m'

def load_account(file_name: str) -> Account:
  '''
  Load Mnemonic from YAML File given `file_name`
  '''
  try:
    with open(file_name) as f:
      content = safe_load(f)
      mnemonic = content.get('mnemonic', None)
      acct = accounts.from_mnemonic(mnemonic, count=1)
    return acct
  except FileNotFoundError:
    print(f'{ RED }Cannot find wallet mnemonic file defined at `{ file_name }`.{ NFMT }')

@fixture
def admin() -> Account:
  '''
  Loads test Treasury account using `wallet.test.yml` found on root-folder
  '''
  acct = load_account('wallet.test.yml')
  try: ### Transfer Initial Balance to Test WAllet ###
    accounts[0].transfer(acct, Wei('100 ether').to('wei'))
  except ValueError: pass
  return acct

@fixture
def user_accounts() -> List[Account]:
  '''
  Use remaining accounts set up by Ganache-cli to be list of user accounts.
  '''
  return accounts[1:10]

@fixture
def governance() -> Account:
  '''
  Loads test Governance account using `wallet.governance.yml` found on root-folder
  '''
  return load_account('wallet.governance.yml')

@fixture
def treasury() -> Account:
  '''
  Loads test Treasury account using `wallet.treasury.yml` found on root-folder
  '''
  return load_account('wallet.treasury.yml')

@fixture
def gas_price() -> dict:
  return { 'fast': 0.000000480, 'standard': 0.000000064 }
