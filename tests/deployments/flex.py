#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/deployments/flex.py
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
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from tests import *

@fixture
def deploy_flex(admin: Account) -> FLEXCoin:
  '''
  FIXTURE: Deploy a flex contract to be used by other contracts' testing.  

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :returns:  `FLEXCoin`  
  '''
  gas_strategy = ExponentialScalingStrategy('10 gwei', '50 gwei')
  return FLEXCoin.deploy({ 'from': admin, 'gas_price': gas_strategy })

def test_deploy_flex(admin: Account):
  '''
  TEST: Deploy flex Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  '''
  ### Deployment ###
  gas_strategy   = ExponentialScalingStrategy('10 gwei', '50 gwei')
  flex: FLEXCoin = FLEXCoin.deploy({ 'from': admin, 'gas_price': gas_strategy })
  print(f'FLEXCoin: { flex }')
