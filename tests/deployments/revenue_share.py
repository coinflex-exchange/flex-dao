#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/deployments/revenue_share.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-21 12:03
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import FLEXCoin, RevenueShare, veFLEX
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from tests import *
from .flex import deploy_flex
from .ve_flex import deploy_ve_flex

@fixture
def deploy_revenue_share(admin: Account, deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX) -> RevenueShare:
  '''
  FIXTURE: Deploy a RevenueShare contract to be used by other contracts' testing.  

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_ve_flex  `veFLEX`  vested balance token for given token  
  :returns:  `RevenueShare`  
  '''
  flex: FLEXCoin  = deploy_flex
  ve_flex: veFLEX = deploy_ve_flex
  gas_strategy    = GasNowStrategy('fast')
  ### Deployment ###
  return RevenueShare.deploy(flex, ve_flex, { 'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('gas_speed', ('fast', 'standard'))
def test_deploy_revenue_share(admin: Account, deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, gas_speed: str):
  '''
  TEST: Deploy RevenueShare Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_ve_flex  `veFLEX`  vested balance token for given token  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  '''
  flex: FLEXCoin              = deploy_flex
  ve_flex: veFLEX             = deploy_ve_flex
  gas_strategy                = GasNowStrategy(gas_speed)
  ### Deployment ###
  revenue_share: RevenueShare = RevenueShare.deploy(flex, ve_flex, { 'from': admin, 'gas_price': gas_strategy })
  print(f'RevenueShare: { revenue_share }')
