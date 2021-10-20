#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/deployments/daily_payout.py
# VERSION: 	 1.0
# CREATED: 	 2021-10-12 14:44
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import FLEXCoin, DailyPayout, veFLEX
### Third-Party Packages ###
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from tests import *
from .flex import deploy_flex
from .ve_flex import deploy_ve_flex

@fixture
def deploy_daily_payout(admin: Account, deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX) -> DailyPayout:
  '''
  FIXTURE: Deploy a DailyPayout contract to be used by other contracts' testing.  

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_ve_flex  `veFLEX`  vested balance token for given token  
  :returns:  `DailyPayout`  
  '''
  flex: FLEXCoin  = deploy_flex
  ve_flex: veFLEX = deploy_ve_flex
  gas_strategy    = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  return DailyPayout.deploy(flex, ve_flex, { 'from': admin, 'gas_price': gas_strategy })

def test_deploy_daily_payout(admin: Account, deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX):
  '''
  TEST: Deploy DailyPayout Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_ve_flex  `veFLEX`  vested balance token for given token  
  '''
  flex: FLEXCoin            = deploy_flex
  ve_flex: veFLEX           = deploy_ve_flex
  gas_strategy              = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  daily_payout: DailyPayout = DailyPayout.deploy(flex, ve_flex, { 'from': admin, 'gas_price': gas_strategy })
  print(f'DailyPayout: { daily_payout }')
