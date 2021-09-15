#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/flex.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import FLEXCoin
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from . import *

@fixture
def deploy_flex(admin: Account) -> FLEXCoin:
  '''
  FIXTURE: Deploy a flex contract to be used by other contracts' testing.  

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :returns:  `FLEXCoin`  
  '''
  gas_strategy = GasNowStrategy('fast')
  return FLEXCoin.deploy({ 'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('gas_speed', ('fast', 'standard'))
def test_deploy_flex(admin: Account, gas_speed: str):
  '''
  TEST: Deploy flex Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  '''
  ### Deployment ###
  gas_strategy   = GasNowStrategy(gas_speed)
  flex: FLEXCoin = FLEXCoin.deploy({ 'from': admin, 'gas_price': gas_strategy })
  print(f'flex: { flex }')
